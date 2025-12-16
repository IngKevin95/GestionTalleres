from decimal import Decimal
from ...domain.exceptions import ErrorDominio
from ...domain.enums import CodigoError
from ...domain.dinero import redondear_mitad_par
from .base import AccionBase
from ..dtos import AutorizarDTO, ReautorizarDTO, IntentarCompletarDTO, OrdenDTO
from ..mappers import orden_a_dto


class Autorizar(AccionBase):
    def ejecutar(self, dto: AutorizarDTO) -> OrdenDTO:
        o = self.repo.obtener(dto.order_id)
        if o is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        idx_ant = self._obtener_indice_eventos_anterior(o)
        subtotal = sum(s.calcular_subtotal_estimado() for s in o.servicios)
        monto = redondear_mitad_par(subtotal * Decimal('1.16'), 2)
        o.autorizar(monto)
        
        self._registrar_eventos_nuevos(o, idx_ant)
        self.repo.guardar(o)
        return orden_a_dto(o)


class Reautorizar(AccionBase):
    def ejecutar(self, dto: ReautorizarDTO) -> OrdenDTO:
        orden = self.repo.obtener(dto.order_id)
        if orden is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        idx_ant = self._obtener_indice_eventos_anterior(orden)
        orden.reautorizar(dto.nuevo_monto_autorizado)
        
        self._registrar_eventos_nuevos(orden, idx_ant)
        self.repo.guardar(orden)
        return orden_a_dto(orden)


class IntentarCompletar(AccionBase):
    def ejecutar(self, dto: IntentarCompletarDTO) -> OrdenDTO:
        orden = self.repo.obtener(dto.order_id)
        if orden is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        idx_ant = self._obtener_indice_eventos_anterior(orden)
        try:
            orden.intentar_completar()
        except ErrorDominio as e:
            if e.codigo == CodigoError.REQUIRES_REAUTH:
                self._registrar_eventos_nuevos(orden, idx_ant)
                self.repo.guardar(orden)
            raise
        
        self._registrar_eventos_nuevos(orden, idx_ant)
        self.repo.guardar(orden)
        return orden_a_dto(orden)

