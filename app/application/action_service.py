from typing import List, Dict, Any, Optional, Tuple

from ..domain.exceptions import ErrorDominio
from ..domain.enums import CodigoError
from .ports import RepositorioOrden, AlmacenEventos
from .dtos import OrdenDTO, EventoDTO, ErrorDTO
from .mappers import (
    json_a_crear_orden_dto, json_a_agregar_servicio_dto,
    json_a_establecer_estado_diagnosticado_dto, json_a_autorizar_dto,
    json_a_establecer_estado_en_proceso_dto, json_a_establecer_costo_real_dto,
    json_a_intentar_completar_dto, json_a_reautorizar_dto,
    json_a_entregar_dto, json_a_cancelar_dto, orden_a_dto, evento_a_dto
)
from .acciones import (
    CrearOrden, AgregarServicio, EstablecerEstadoDiagnosticado,
    Autorizar, EstablecerEstadoEnProceso, EstablecerCostoReal,
    IntentarCompletar, Reautorizar, EntregarOrden, CancelarOrden
)
from ..infrastructure.logging_config import obtener_logger


logger = obtener_logger("app.application.action_service")


class ActionService:
    def __init__(self, repo: RepositorioOrden, auditoria: AlmacenEventos):
        self.repo = repo
        self.auditoria = auditoria
    
    def procesar_comando(self, comando: Dict[str, Any]) -> Tuple[Optional[OrdenDTO], List[EventoDTO], Optional[ErrorDTO]]:
        op = comando.get("op")
        data = comando.get("data", {})
        ts_comando = comando.get("ts")
        order_id = data.get("order_id")
        if isinstance(order_id, (int, float)):
            order_id = str(order_id)
        
        evts_ant = 0
        if order_id:
            orden_ant = self.repo.obtener(order_id)
            if orden_ant:
                evts_ant = len(orden_ant.eventos)
        
        try:
            match op:
                case "CREATE_ORDER":
                    dto = json_a_crear_orden_dto(data, ts_comando)
                    action = CrearOrden(self.repo, self.auditoria, None, None)
                    orden_dto = action.ejecutar(dto)
                    logger.info(f"Orden creada exitosamente: {orden_dto.order_id}")
                
                case "ADD_SERVICE":
                    dto = json_a_agregar_servicio_dto(data)
                    action = AgregarServicio(self.repo, self.auditoria)
                    orden_dto = action.ejecutar(dto)
                    logger.info(f"Servicio agregado a orden: {order_id}")
                
                case "SET_STATE_DIAGNOSED":
                    dto = json_a_establecer_estado_diagnosticado_dto(data)
                    action = EstablecerEstadoDiagnosticado(self.repo, self.auditoria)
                    orden_dto = action.ejecutar(dto)
                    logger.info(f"Estado DIAGNOSED establecido para orden: {order_id}")
                
                case "AUTHORIZE":
                    dto = json_a_autorizar_dto(data, ts_comando)
                    action = Autorizar(self.repo, self.auditoria)
                    orden_dto = action.ejecutar(dto)
                    logger.info(f"Orden {order_id} autorizada: {orden_dto.authorized_amount}")
                
                case "SET_STATE_IN_PROGRESS":
                    dto = json_a_establecer_estado_en_proceso_dto(data)
                    action = EstablecerEstadoEnProceso(self.repo, self.auditoria)
                    orden_dto = action.ejecutar(dto)
                    logger.info(f"Estado IN_PROGRESS establecido para orden: {order_id}")
                
                case "SET_REAL_COST":
                    dto = json_a_establecer_costo_real_dto(data)
                    action = EstablecerCostoReal(self.repo, self.auditoria)
                    orden_dto = action.ejecutar(dto)
                    logger.info(f"Costo real establecido para orden: {order_id}")
                
                case "TRY_COMPLETE":
                    dto = json_a_intentar_completar_dto(data)
                    action = IntentarCompletar(self.repo, self.auditoria)
                    orden_dto = action.ejecutar(dto)
                    logger.info(f"Intento de completar orden: {order_id}, nuevo estado: {orden_dto.status}")
                
                case "REAUTHORIZE":
                    dto = json_a_reautorizar_dto(data, ts_comando)
                    action = Reautorizar(self.repo, self.auditoria)
                    orden_dto = action.ejecutar(dto)
                    logger.info(f"Orden reautorizada: {order_id}, nuevo monto: {orden_dto.authorized_amount}")
                
                case "DELIVER":
                    dto = json_a_entregar_dto(data)
                    action = EntregarOrden(self.repo, self.auditoria)
                    orden_dto = action.ejecutar(dto)
                    logger.info(f"Orden entregada: {order_id}")
                
                case "CANCEL":
                    dto = json_a_cancelar_dto(data)
                    action = CancelarOrden(self.repo, self.auditoria)
                    orden_dto = action.ejecutar(dto)
                    logger.info(f"Orden cancelada: {order_id}")
                
                case _:
                    error_msg = f"Operación desconocida: {op}"
                    logger.error(error_msg)
                    return None, [], ErrorDTO(
                        op=op,
                        order_id=order_id,
                        code=CodigoError.INVALID_OPERATION.value,
                        message=error_msg
                    )
            
            todos = orden_dto.events
            nuevos = todos[evts_ant:] if evts_ant < len(todos) else []
            
            return orden_dto, nuevos, None
        
        except ErrorDominio as e:
            logger.error(f"Error en {op}: {e.mensaje}", exc_info=True)
            error_dto = ErrorDTO(op=op, order_id=order_id, code=e.codigo.value, message=e.mensaje)
            
            if e.codigo == CodigoError.REQUIRES_REAUTH:
                orden = self.repo.obtener(order_id)
                if orden:
                    orden_dto = orden_a_dto(orden)
                    todos = orden_dto.events
                    nuevos = todos[evts_ant:] if evts_ant < len(todos) else []
                    return orden_dto, nuevos, error_dto
            
            return None, [], error_dto
        except Exception as e:
            logger.error(f"Error inesperado en {op}: {str(e)}", exc_info=True)
            error_dto = ErrorDTO(op=op, order_id=order_id, code="INTERNAL_ERROR", message=str(e))
            return None, [], error_dto

