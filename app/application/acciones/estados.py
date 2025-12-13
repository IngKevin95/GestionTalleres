from ...domain.exceptions import ErrorDominio
from ...domain.enums import CodigoError
from ..ports import RepositorioOrden, AlmacenEventos
from ..dtos import EstablecerEstadoDiagnosticadoDTO, EstablecerEstadoEnProcesoTDTO, OrdenDTO
from ..mappers import orden_a_dto


class EstablecerEstadoDiagnosticado:
    def __init__(self, repo: RepositorioOrden, auditoria: AlmacenEventos):
        self.repo = repo
        self.auditoria = auditoria
    
    def ejecutar(self, dto: EstablecerEstadoDiagnosticadoDTO) -> OrdenDTO:
        orden = self.repo.obtener(dto.order_id)
        if orden is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        orden.establecer_estado_diagnosticado()
        
        for evt in orden.eventos:
            self.auditoria.registrar(evt)
        
        self.repo.guardar(orden)
        return orden_a_dto(orden)


class EstablecerEstadoEnProceso:
    def __init__(self, repositorio: RepositorioOrden, audit: AlmacenEventos):
        self.repositorio = repositorio
        self.audit = audit
    
    def ejecutar(self, dto: EstablecerEstadoEnProcesoTDTO) -> OrdenDTO:
        o = self.repositorio.obtener(dto.order_id)
        if not o:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        eventos_antes = len(o.eventos)
        o.establecer_estado_en_proceso()
        eventos_nuevos = o.eventos[eventos_antes:]
        
        self.repositorio.guardar(o)
        for evento in eventos_nuevos:
            self.audit.registrar(evento)
        
        return orden_a_dto(o)

