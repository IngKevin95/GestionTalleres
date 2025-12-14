from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, fecha_creacion_default


class OrdenModel(Base):
    __tablename__ = "ordenes"
    
    id_orden = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente", ondelete="RESTRICT"), nullable=False)
    id_vehiculo = Column(Integer, ForeignKey("vehiculos.id_vehiculo", ondelete="RESTRICT"), nullable=False)
    estado = Column(String, nullable=False)
    monto_autorizado = Column(String, nullable=True)
    version_autorizacion = Column(Integer, default=0)
    total_real = Column(String, default="0")
    fecha_creacion = Column(DateTime, default=fecha_creacion_default)
    fecha_cancelacion = Column(DateTime, nullable=True)
    
    cliente = relationship("ClienteModel", backref="ordenes")
    vehiculo = relationship("VehiculoModel", backref="ordenes")
    servicios = relationship("ServicioModel", back_populates="orden", cascade="all, delete-orphan")
    eventos = relationship("EventoModel", back_populates="orden", cascade="all, delete-orphan")

