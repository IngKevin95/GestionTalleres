from uuid import uuid4
from datetime import datetime

from ...domain.entidades import Orden, Evento
from ...domain.exceptions import ErrorDominio
from ...domain.enums import CodigoError
from ...domain.zona_horaria import ahora
from ..ports import RepositorioOrden, AlmacenEventos
from ..dtos import CrearOrdenDTO, CancelarDTO, EntregarDTO, OrdenDTO
from ..mappers import orden_a_dto


class CrearOrden:
    def __init__(self, repositorio: RepositorioOrden, auditoria: AlmacenEventos):
        self.repositorio = repositorio
        self.auditoria = auditoria
    
    def ejecutar(self, dto: CrearOrdenDTO) -> OrdenDTO:
        id_orden = dto.order_id if dto.order_id else f"ORD-{uuid4().hex[:8].upper()}"
        
        orden_existente = self.repositorio.obtener(id_orden)
        if orden_existente:
            return orden_a_dto(orden_existente)
        
        orden = Orden(id_orden, dto.cliente, dto.vehiculo, dto.timestamp)
        orden.eventos.append(Evento("CREATED", ahora(), {}))
        
        self.repositorio.guardar(orden)
        for evt in orden.eventos:
            self.auditoria.registrar(evt)
        return orden_a_dto(orden)


class CancelarOrden:
    def __init__(self, repo: RepositorioOrden, auditoria: AlmacenEventos):
        self.repo = repo
        self.auditoria = auditoria
    
    def ejecutar(self, dto: CancelarDTO) -> OrdenDTO:
        o = self.repo.obtener(dto.order_id)
        if o is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"No existe orden {dto.order_id}")
        
        idx_prev = len(o.eventos)
        o.cancelar(dto.motivo)
        
        self.repo.guardar(o)
        for evt in o.eventos[idx_prev:]:
            self.auditoria.registrar(evt)
        return orden_a_dto(o)


class EntregarOrden:
    def __init__(self, repositorio: RepositorioOrden, audit: AlmacenEventos):
        self.repositorio = repositorio
        self.audit = audit
    
    def ejecutar(self, dto: EntregarDTO) -> OrdenDTO:
        orden = self.repositorio.obtener(dto.order_id)
        if orden is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        orden.entregar()
        
        for evt in orden.eventos:
            self.audit.registrar(evt)
        
        self.repositorio.guardar(orden)
        return orden_a_dto(orden)

