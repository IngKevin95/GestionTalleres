from ...domain.entidades import Servicio, Componente
from ...domain.exceptions import ErrorDominio
from ...domain.enums import CodigoError
from ...domain.dinero import a_decimal
from .base import AccionBase
from ..dtos import AgregarServicioDTO, EstablecerCostoRealDTO, OrdenDTO
from ..mappers import orden_a_dto


class AgregarServicio(AccionBase):
    
    def ejecutar(self, dto: AgregarServicioDTO) -> OrdenDTO:
        orden = self.repo.obtener(dto.order_id)
        if orden is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        comps = self._crear_componentes(dto.componentes)
        srv = Servicio(
            descripcion=dto.descripcion,
            costo_mano_obra_estimado=dto.costo_mano_obra,
            componentes=comps
        )
        
        orden.agregar_servicio(srv)
        self.repo.guardar(orden)
        return orden_a_dto(orden)
    
    def _crear_componentes(self, componentes_data):
        comps = []
        for comp_data in componentes_data:
            costo = a_decimal(comp_data.get("estimated_cost", 0))
            if costo < 0:
                raise ErrorDominio(
                    CodigoError.INVALID_AMOUNT,
                    f"Costo estimado debe ser positivo, se recibió: {costo}"
                )
            comps.append(Componente(
                descripcion=comp_data.get("description", ""),
                costo_estimado=costo
            ))
        return comps


class EstablecerCostoReal(AccionBase):
    
    def ejecutar(self, dto: EstablecerCostoRealDTO) -> OrdenDTO:
        orden = self.repo.obtener(dto.order_id)
        if not orden:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        idx_ant = self._obtener_indice_eventos_anterior(orden)
        servicio_id, servicio = self._obtener_servicio_id_y_objeto(orden, dto)
        orden.establecer_costo_real(servicio_id, dto.costo_real, dto.componentes_reales)
        
        if dto.completed is not None and servicio:
            servicio.completado = dto.completed
        
        self._registrar_eventos_nuevos(orden, idx_ant)
        self.repo.guardar(orden)
        return orden_a_dto(orden)
    
    def _obtener_servicio_id_y_objeto(self, orden, dto):
        if dto.service_index is not None:
            if dto.service_index < 1 or dto.service_index > len(orden.servicios):
                raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Índice {dto.service_index} inválido")
            servicio = orden.servicios[dto.service_index - 1]
            return servicio.id_servicio, servicio
        
        if not dto.servicio_id:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, "Falta service_id o service_index")
        
        servicio = next((s for s in orden.servicios if s.id_servicio == dto.servicio_id), None)
        return dto.servicio_id, servicio

