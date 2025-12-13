from datetime import datetime
from typing import Dict, Any


class Evento:
    def __init__(self, tipo: str, timestamp: datetime, metadatos: Dict[str, Any] = None):
        self.tipo = tipo
        self.timestamp = timestamp
        self.metadatos = metadatos or {}

