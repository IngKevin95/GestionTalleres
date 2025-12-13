from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class ServicioModel(Base):
    __tablename__ = "servicios"
    
    id_servicio = Column(String, primary_key=True)
    id_orden = Column(String, ForeignKey("ordenes.id_orden", ondelete="CASCADE"), nullable=False)
    descripcion = Column(String, nullable=False)
    costo_mano_obra_estimado = Column(String, nullable=False)
    costo_real = Column(String, nullable=True)
    completado = Column(Integer, default=0)
    
    orden = relationship("OrdenModel", back_populates="servicios")
    componentes = relationship("ComponenteModel", back_populates="servicio", cascade="all, delete-orphan")

