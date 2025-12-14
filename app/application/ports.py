from abc import ABC, abstractmethod
from typing import Optional
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

