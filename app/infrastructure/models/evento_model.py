from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class EventoModel(Base):
    __tablename__ = "eventos"
    
    id_evento = Column(Integer, primary_key=True, autoincrement=True)
    id_orden = Column(String, ForeignKey("ordenes.id_orden", ondelete="CASCADE"), nullable=False)
    tipo = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    metadatos_json = Column(Text, nullable=True)
    
    orden = relationship("OrdenModel", back_populates="eventos")

