from ..domain.entidades import Evento
from ..application.ports import AlmacenEventos

from .logging_config import obtener_logger


logger = obtener_logger("app.infrastructure.logger")


class AlmacenEventosLogger(AlmacenEventos):
    def __init__(self):
        # No requiere inicialización
        pass
    
    def registrar(self, evento: Evento) -> None:
        logger.info(
            "Evento de dominio registrado",
            extra={
                "categoria": "evento_dominio",
                "tipo": evento.tipo,
                "timestamp": evento.timestamp.isoformat(),
                "metadata": evento.metadatos
            }
        )

