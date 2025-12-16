from typing import List, Dict, Any, Optional, Tuple

from ..domain.exceptions import ErrorDominio
from ..domain.enums import CodigoError
from .ports import RepositorioOrden, AlmacenEventos
from .dtos import OrdenDTO, EventoDTO, ErrorDTO
from .mappers import (
    crear_orden_dto, agregar_servicio_dto,
    estado_diagnosticado_dto, autorizar_dto,
    estado_en_proceso_dto, costo_real_dto,
    intentar_completar_dto, reautorizar_dto,
    entregar_dto, cancelar_dto, orden_a_dto, evento_a_dto
)
from .acciones import (
    CrearOrden, AgregarServicio, EstablecerEstadoDiagnosticado,
    Autorizar, EstablecerEstadoEnProceso, EstablecerCostoReal,
    IntentarCompletar, Reautorizar, EntregarOrden, CancelarOrden
)
from ..infrastructure.logging_config import obtener_logger, obtener_contexto_log


logger = obtener_logger("app.application.action_service")


class ActionService:
    def __init__(self, repo: RepositorioOrden, auditoria: AlmacenEventos):
        self.repo = repo
        self.auditoria = auditoria
    
    def _normalizar_order_id(self, data: dict) -> Optional[str]:
        """Normaliza order_id a string si es numérico."""
        order_id = data.get("order_id")
        if isinstance(order_id, (int, float)):
            return str(order_id)
        return order_id
    
    def _obtener_eventos_anteriores(self, order_id: Optional[str]) -> int:
        """Obtiene el número de eventos anteriores de una orden."""
        if not order_id:
            return 0
        try:
            ord_ant = self.repo.obtener(order_id)
            return len(ord_ant.eventos) if ord_ant else 0
        except Exception:
            return 0
    
    def _crear_accion_por_operacion(self, op: str, data: dict, ts: Optional[str]) -> OrdenDTO:
        """Crea y ejecuta la acción correspondiente a la operación."""
        match op:
            case "CREATE_ORDER":
                dto = crear_orden_dto(data, ts)
                accion = CrearOrden(self.repo, self.auditoria, None, None)
                return accion.ejecutar(dto)
            
            case "ADD_SERVICE":
                dto = agregar_servicio_dto(data)
                accion = AgregarServicio(self.repo, self.auditoria)
                return accion.ejecutar(dto)
            
            case "SET_STATE_DIAGNOSED":
                dto = estado_diagnosticado_dto(data)
                accion = EstablecerEstadoDiagnosticado(self.repo, self.auditoria)
                return accion.ejecutar(dto)
            
            case "AUTHORIZE":
                dto = autorizar_dto(data, ts)
                accion = Autorizar(self.repo, self.auditoria)
                return accion.ejecutar(dto)
            
            case "SET_STATE_IN_PROGRESS":
                dto = estado_en_proceso_dto(data)
                accion = EstablecerEstadoEnProceso(self.repo, self.auditoria)
                return accion.ejecutar(dto)
            
            case "SET_REAL_COST":
                dto = costo_real_dto(data)
                accion = EstablecerCostoReal(self.repo, self.auditoria)
                return accion.ejecutar(dto)
            
            case "TRY_COMPLETE":
                dto = intentar_completar_dto(data)
                accion = IntentarCompletar(self.repo, self.auditoria)
                return accion.ejecutar(dto)
            
            case "REAUTHORIZE":
                dto = reautorizar_dto(data, ts)
                accion = Reautorizar(self.repo, self.auditoria)
                return accion.ejecutar(dto)
            
            case "DELIVER":
                dto = entregar_dto(data)
                accion = EntregarOrden(self.repo, self.auditoria)
                return accion.ejecutar(dto)
            
            case "CANCEL":
                dto = cancelar_dto(data)
                accion = CancelarOrden(self.repo, self.auditoria)
                return accion.ejecutar(dto)
            
            case _:
                raise ValueError(f"Operación desconocida: {op}")
    
    def _extraer_nuevos_eventos(self, orden_dto: OrdenDTO, evts_ant: int) -> List[EventoDTO]:
        """Extrae solo los eventos nuevos generados por la acción."""
        todos_evts = orden_dto.events
        return todos_evts[evts_ant:] if evts_ant < len(todos_evts) else []
    
    def _manejar_error_dominio(self, e: ErrorDominio, op: str, order_id: Optional[str], evts_ant: int) -> Tuple[Optional[OrdenDTO], List[EventoDTO], ErrorDTO]:
        """Maneja errores de dominio y retorna respuesta apropiada."""
        ctx = obtener_contexto_log()
        logger.error(
            f"Error {op}: {e.mensaje}",
            extra={
                **ctx,
                "op": op,
                "order_id": order_id,
                "operacion": op,
                "error_code": e.codigo.value,
                **e.contexto
            },
            exc_info=True
        )
        err = ErrorDTO(op=op, order_id=order_id, code=e.codigo.value, message=e.mensaje)
        
        if e.codigo == CodigoError.REQUIRES_REAUTH:
            ord = self.repo.obtener(order_id)
            if ord:
                ord_dto = orden_a_dto(ord)
                nuevos_evts = self._extraer_nuevos_eventos(ord_dto, evts_ant)
                return ord_dto, nuevos_evts, err
        
        return None, [], err
    
    def _manejar_error_validacion(self, ve: ValueError, op: str, order_id: Optional[str]) -> Tuple[Optional[OrdenDTO], List[EventoDTO], ErrorDTO]:
        """Maneja errores de validación (ValueError)."""
        msg = str(ve)
        ctx = obtener_contexto_log()
        logger.error(
            msg,
            extra={**ctx, "op": op, "order_id": order_id, "operacion": op}
        )
        return None, [], ErrorDTO(
            op=op,
            order_id=order_id,
            code=CodigoError.INVALID_OPERATION.value,
            message=msg
        )
    
    def _manejar_error_inesperado(self, e: Exception, op: str, order_id: Optional[str], data: dict) -> Tuple[Optional[OrdenDTO], List[EventoDTO], ErrorDTO]:
        """Maneja errores inesperados (excepciones genéricas)."""
        ctx = obtener_contexto_log()
        logger.error(
            f"Error inesperado {op}: {str(e)}",
            extra={
                **ctx,
                "op": op,
                "order_id": order_id,
                "operacion": op,
                "error_type": type(e).__name__,
                "data": str(data)[:200] if data else None
            },
            exc_info=True
        )
        return None, [], ErrorDTO(op=op, order_id=order_id, code="INTERNAL_ERROR", message=str(e))
    
    def procesar_comando(self, comando: Dict[str, Any]) -> Tuple[Optional[OrdenDTO], List[EventoDTO], Optional[ErrorDTO]]:
        op = comando.get("op")
        data = comando.get("data", {})
        ts = comando.get("ts")
        order_id = self._normalizar_order_id(data)
        evts_ant = self._obtener_eventos_anteriores(order_id)
        
        try:
            orden_dto = self._crear_accion_por_operacion(op, data, ts)
            nuevos_evts = self._extraer_nuevos_eventos(orden_dto, evts_ant)
            return orden_dto, nuevos_evts, None
        
        except ValueError as ve:
            return self._manejar_error_validacion(ve, op, order_id)
        
        except ErrorDominio as e:
            return self._manejar_error_dominio(e, op, order_id, evts_ant)
        
        except Exception as e:
            return self._manejar_error_inesperado(e, op, order_id, data)

