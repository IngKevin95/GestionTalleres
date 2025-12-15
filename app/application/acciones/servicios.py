from ...domain.entidades import Servicio, Componente
from ...domain.exceptions import ErrorDominio
from ...domain.enums import CodigoError
from ...domain.dinero import a_decimal
from ..ports import RepositorioOrden, AlmacenEventos
from ..dtos import AgregarServicioDTO, EstablecerCostoRealDTO, OrdenDTO
from ..mappers import orden_a_dto


class AgregarServicio:
    def __init__(self, repo: RepositorioOrden, auditoria: AlmacenEventos):
        self.repo = repo
        self.auditoria = auditoria
    
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


class EstablecerCostoReal:
    def __init__(self, repo: RepositorioOrden, auditoria: AlmacenEventos):
        self.repo = repo
        self.auditoria = auditoria
    
    def ejecutar(self, dto: EstablecerCostoRealDTO) -> OrdenDTO:
        orden = self.repo.obtener(dto.order_id)
        if not orden:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        servicio_id = self._obtener_servicio_id(orden, dto)
        orden.establecer_costo_real(servicio_id, dto.costo_real, dto.componentes_reales)
        
        if dto.completed is not None:
            servicio = next((s for s in orden.servicios if s.id_servicio == servicio_id), None)
            if servicio:
                servicio.completado = dto.completed
        
        self.repo.guardar(orden)
        return orden_a_dto(orden)
    
    def _obtener_servicio_id(self, orden, dto):
        if dto.service_index:
            if dto.service_index < 1 or dto.service_index > len(orden.servicios):
                raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Índice {dto.service_index} inválido")
            return orden.servicios[dto.service_index - 1].id_servicio
        
        if not dto.servicio_id:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, "Falta service_id o service_index")
        
        return dto.servicio_id

