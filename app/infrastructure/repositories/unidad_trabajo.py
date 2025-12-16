from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Session

from ...application.ports import UnidadTrabajo

if TYPE_CHECKING:
    from .repositorio_orden import RepositorioOrden

from .repositorio_cliente import RepositorioClienteSQL
from .repositorio_vehiculo import RepositorioVehiculoSQL
from .repositorio_servicio import RepositorioServicioSQL
from .repositorio_evento import RepositorioEventoSQL


class UnidadTrabajoSQL(UnidadTrabajo):
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self._repo_orden: Optional["RepositorioOrden"] = None
        self._repo_cliente: Optional[RepositorioClienteSQL] = None
        self._repo_vehiculo: Optional[RepositorioVehiculoSQL] = None
        self._repo_servicio: Optional[RepositorioServicioSQL] = None
        self._repo_evento: Optional[RepositorioEventoSQL] = None
    
    def obtener_repositorio_orden(self) -> "RepositorioOrden":
        if self._repo_orden is None:
            from .repositorio_orden import RepositorioOrden
            self._repo_orden = RepositorioOrden(self.sesion, self)
        return self._repo_orden
    
    def obtener_repositorio_cliente(self) -> RepositorioClienteSQL:
        if self._repo_cliente is None:
            self._repo_cliente = RepositorioClienteSQL(self.sesion)
        return self._repo_cliente
    
    def obtener_repositorio_vehiculo(self) -> RepositorioVehiculoSQL:
        if self._repo_vehiculo is None:
            self._repo_vehiculo = RepositorioVehiculoSQL(self.sesion)
        return self._repo_vehiculo
    
    def obtener_repositorio_servicio(self) -> RepositorioServicioSQL:
        if self._repo_servicio is None:
            self._repo_servicio = RepositorioServicioSQL(self.sesion)
        return self._repo_servicio
    
    def obtener_repositorio_evento(self) -> RepositorioEventoSQL:
        if self._repo_evento is None:
            self._repo_evento = RepositorioEventoSQL(self.sesion)
        return self._repo_evento

