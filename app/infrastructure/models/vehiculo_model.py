from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class VehiculoModel(Base):
    __tablename__ = "vehiculos"
    
    id_vehiculo = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String, nullable=False)
    marca = Column(String, nullable=True)
    modelo = Column(String, nullable=True)
    anio = Column(Integer, nullable=True)
    kilometraje = Column(Integer, nullable=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente", ondelete="CASCADE"), nullable=False)
    
    cliente = relationship("ClienteModel", backref="vehiculos")

