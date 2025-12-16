from ...domain.exceptions import ErrorDominio
from ...domain.enums import CodigoError
from .base import AccionBase
from ..dtos import EstablecerEstadoDiagnosticadoDTO, EstablecerEstadoEnProcesoTDTO, OrdenDTO
from ..mappers import orden_a_dto


class EstablecerEstadoDiagnosticado(AccionBase):
    def ejecutar(self, dto: EstablecerEstadoDiagnosticadoDTO) -> OrdenDTO:
        orden = self.repo.obtener(dto.order_id)
        if orden is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        idx_ant = self._obtener_indice_eventos_anterior(orden)
        orden.establecer_estado_diagnosticado()
        
        self._registrar_eventos_nuevos(orden, idx_ant)
        self.repo.guardar(orden)
        return orden_a_dto(orden)


class EstablecerEstadoEnProceso(AccionBase):
    def ejecutar(self, dto: EstablecerEstadoEnProcesoTDTO) -> OrdenDTO:
        o = self.repo.obtener(dto.order_id)
        if not o:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        idx_ant = self._obtener_indice_eventos_anterior(o)
        o.establecer_estado_en_proceso()
        
        self.repo.guardar(o)
        self._registrar_eventos_nuevos(o, idx_ant)
        
        return orden_a_dto(o)

