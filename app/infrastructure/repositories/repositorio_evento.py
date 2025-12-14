from typing import List
import json
from sqlalchemy.orm import Session

from ...domain.entidades import Evento
from ..models.evento_model import EventoModel


class RepositorioEventoSQL:
    def __init__(self, sesion: Session):
        self.sesion = sesion
    
    def guardar_eventos(self, id_orden: int, eventos: List[Evento], eventos_existentes: List[EventoModel]) -> None:
        for i, evt in enumerate(eventos):
            if i < len(eventos_existentes):
                em = eventos_existentes[i]
                em.tipo = evt.tipo
                em.timestamp = evt.timestamp
                em.metadatos_json = json.dumps(evt.metadatos) if evt.metadatos else None
            else:
                nuevo = EventoModel(
                    id_orden=id_orden,
                    tipo=evt.tipo,
                    timestamp=evt.timestamp,
                    metadatos_json=json.dumps(evt.metadatos) if evt.metadatos else None
                )
                self.sesion.add(nuevo)
                eventos_existentes.append(nuevo)
        
        if len(eventos) < len(eventos_existentes):
            for em in eventos_existentes[len(eventos):]:
                self.sesion.delete(em)
                eventos_existentes.remove(em)
    
    def deserializar_eventos(self, eventos_modelo: List[EventoModel]) -> List[Evento]:
        resultado = []
        ordenados = sorted(eventos_modelo, key=lambda x: x.timestamp)
        for em in ordenados:
            meta = json.loads(em.metadatos_json) if em.metadatos_json else {}
            evt = Evento(tipo=em.tipo, timestamp=em.timestamp, metadatos=meta)
            resultado.append(evt)
        return resultado

