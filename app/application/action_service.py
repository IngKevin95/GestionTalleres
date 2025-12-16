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
    
    def procesar_comando(self, comando: Dict[str, Any]) -> Tuple[Optional[OrdenDTO], List[EventoDTO], Optional[ErrorDTO]]:
        op = comando.get("op")
        data = comando.get("data", {})
        ts = comando.get("ts")
        order_id = data.get("order_id")
        if isinstance(order_id, (int, float)):
            order_id = str(order_id)
        
        evts_ant = 0
        if order_id:
            ord_ant = self.repo.obtener(order_id)
            if ord_ant:
                evts_ant = len(ord_ant.eventos)
        
        try:
            match op:
                case "CREATE_ORDER":
                    dto = crear_orden_dto(data, ts)
                    accion = CrearOrden(self.repo, self.auditoria, None, None)
                    orden_dto = accion.ejecutar(dto)
                
                case "ADD_SERVICE":
                    dto = agregar_servicio_dto(data)
                    accion = AgregarServicio(self.repo, self.auditoria)
                    orden_dto = accion.ejecutar(dto)
                
                case "SET_STATE_DIAGNOSED":
                    dto = estado_diagnosticado_dto(data)
                    accion = EstablecerEstadoDiagnosticado(self.repo, self.auditoria)
                    orden_dto = accion.ejecutar(dto)
                
                case "AUTHORIZE":
                    dto = autorizar_dto(data, ts)
                    accion = Autorizar(self.repo, self.auditoria)
                    orden_dto = accion.ejecutar(dto)
                
                case "SET_STATE_IN_PROGRESS":
                    dto = estado_en_proceso_dto(data)
                    accion = EstablecerEstadoEnProceso(self.repo, self.auditoria)
                    orden_dto = accion.ejecutar(dto)
                
                case "SET_REAL_COST":
                    dto = costo_real_dto(data)
                    accion = EstablecerCostoReal(self.repo, self.auditoria)
                    orden_dto = accion.ejecutar(dto)
                
                case "TRY_COMPLETE":
                    dto = intentar_completar_dto(data)
                    accion = IntentarCompletar(self.repo, self.auditoria)
                    orden_dto = accion.ejecutar(dto)
                
                case "REAUTHORIZE":
                    dto = reautorizar_dto(data, ts)
                    accion = Reautorizar(self.repo, self.auditoria)
                    orden_dto = accion.ejecutar(dto)
                
                case "DELIVER":
                    dto = entregar_dto(data)
                    accion = EntregarOrden(self.repo, self.auditoria)
                    orden_dto = accion.ejecutar(dto)
                
                case "CANCEL":
                    dto = cancelar_dto(data)
                    accion = CancelarOrden(self.repo, self.auditoria)
                    orden_dto = accion.ejecutar(dto)
                
                case _:
                    msg = f"Operación desconocida: {op}"
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
            
            todos_evts = orden_dto.events
            nuevos_evts = todos_evts[evts_ant:] if evts_ant < len(todos_evts) else []
            
            return orden_dto, nuevos_evts, None
        
        except ErrorDominio as e:
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
                    todos_evts = ord_dto.events
                    nuevos_evts = todos_evts[evts_ant:] if evts_ant < len(todos_evts) else []
                    return ord_dto, nuevos_evts, err
            
            return None, [], err
        except Exception as e:
            ctx = obtener_contexto_log()
            logger.error(
                f"Error inesperado {op}: {str(e)}",
                extra={
                    **ctx,
                    "op": op,
                    "order_id": order_id,
                    "operacion": op,
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            return None, [], ErrorDTO(op=op, order_id=order_id, code="INTERNAL_ERROR", message=str(e))

