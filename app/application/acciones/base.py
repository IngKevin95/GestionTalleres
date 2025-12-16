from typing import List
from ...domain.entidades import Orden, Evento
from ..ports import RepositorioOrden, AlmacenEventos


class AccionBase:
    def __init__(self, repo: RepositorioOrden, auditoria: AlmacenEventos):
        self.repo = repo
        self.auditoria = auditoria
    
    def _registrar_eventos_nuevos(self, orden: Orden, idx_anterior: int) -> None:
        """Registra solo los eventos nuevos generados por la acción."""
        eventos_nuevos = orden.eventos[idx_anterior:]
        for evt in eventos_nuevos:
            self.auditoria.registrar(evt)
    
    def _obtener_indice_eventos_anterior(self, orden: Orden) -> int:
        """Obtiene el índice de eventos antes de ejecutar la acción."""
        return len(orden.eventos)

