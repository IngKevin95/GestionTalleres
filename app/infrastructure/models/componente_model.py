from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class ComponenteModel(Base):
    __tablename__ = "componentes"
    
    id_componente = Column(Integer, primary_key=True, autoincrement=True)
    id_servicio = Column(Integer, ForeignKey("servicios.id_servicio", ondelete="CASCADE"), nullable=False)
    descripcion = Column(String, nullable=False)
    costo_estimado = Column(String, nullable=False)
    costo_real = Column(String, nullable=True)
    
    servicio = relationship("ServicioModel", back_populates="componentes")

