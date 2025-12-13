from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class ComponenteModel(Base):
    __tablename__ = "componentes"
    
    id_componente = Column(String, primary_key=True)
    id_servicio = Column(String, ForeignKey("servicios.id_servicio", ondelete="CASCADE"), nullable=False)
    descripcion = Column(String, nullable=False)
    costo_estimado = Column(String, nullable=False)
    costo_real = Column(String, nullable=True)
    
    servicio = relationship("ServicioModel", back_populates="componentes")

