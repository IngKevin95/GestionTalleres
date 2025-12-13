from decimal import Decimal
from ...domain.exceptions import ErrorDominio
from ...domain.enums import CodigoError
from ...domain.dinero import redondear_mitad_par
from ..ports import RepositorioOrden, AlmacenEventos
from ..dtos import AutorizarDTO, ReautorizarDTO, IntentarCompletarDTO, OrdenDTO
from ..mappers import orden_a_dto


class Autorizar:
    def __init__(self, repo: RepositorioOrden, auditoria: AlmacenEventos):
        self.repo = repo
        self.auditoria = auditoria
    
    def ejecutar(self, dto: AutorizarDTO) -> OrdenDTO:
        o = self.repo.obtener(dto.order_id)
        if o is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        idx_ant = len(o.eventos)
        subtotal = sum(s.calcular_subtotal_estimado() for s in o.servicios)
        monto = redondear_mitad_par(subtotal * Decimal('1.16'), 2)
        o.autorizar(monto)
        
        for evt in o.eventos[idx_ant:]:
            self.auditoria.registrar(evt)
        
        self.repo.guardar(o)
        return orden_a_dto(o)


class Reautorizar:
    def __init__(self, repositorio: RepositorioOrden, audit: AlmacenEventos):
        self.repositorio = repositorio
        self.audit = audit
    
    def ejecutar(self, dto: ReautorizarDTO) -> OrdenDTO:
        orden = self.repositorio.obtener(dto.order_id)
        if orden is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        orden.reautorizar(dto.nuevo_monto_autorizado)
        
        for evt in orden.eventos:
            self.audit.registrar(evt)
        
        self.repositorio.guardar(orden)
        return orden_a_dto(orden)


class IntentarCompletar:
    def __init__(self, repo: RepositorioOrden, auditoria: AlmacenEventos):
        self.repo = repo
        self.auditoria = auditoria
    
    def ejecutar(self, dto: IntentarCompletarDTO) -> OrdenDTO:
        orden = self.repo.obtener(dto.order_id)
        if orden is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        idx_ant = len(orden.eventos)
        try:
            orden.intentar_completar()
        except ErrorDominio as e:
            if e.codigo == CodigoError.REQUIRES_REAUTH:
                for evt in orden.eventos[idx_ant:]:
                    self.auditoria.registrar(evt)
                self.repo.guardar(orden)
            raise
        
        for evt in orden.eventos[idx_ant:]:
            self.auditoria.registrar(evt)
        self.repo.guardar(orden)
        return orden_a_dto(orden)

