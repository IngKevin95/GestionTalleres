from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
    from ..infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
    from ..infrastructure.repositories.repositorio_servicio import RepositorioServicioSQL
    from ..infrastructure.repositories.repositorio_evento import RepositorioEventoSQL

from ..domain.entidades import Orden, Evento


class RepositorioOrden(ABC):
    @abstractmethod
    def obtener(self, order_id: str) -> Optional[Orden]:
        pass
    
    @abstractmethod
    def guardar(self, orden: Orden) -> None:
        pass


class AlmacenEventos(ABC):
    @abstractmethod
    def registrar(self, evento: Evento) -> None:
        pass


class UnidadTrabajo(ABC):
    @abstractmethod
    def obtener_repositorio_orden(self) -> "RepositorioOrden":
        pass
    
    @abstractmethod
    def obtener_repositorio_cliente(self) -> "RepositorioClienteSQL":
        pass
    
    @abstractmethod
    def obtener_repositorio_vehiculo(self) -> "RepositorioVehiculoSQL":
        pass
    
    @abstractmethod
    def obtener_repositorio_servicio(self) -> "RepositorioServicioSQL":
        pass
    
    @abstractmethod
    def obtener_repositorio_evento(self) -> "RepositorioEventoSQL":
        pass

