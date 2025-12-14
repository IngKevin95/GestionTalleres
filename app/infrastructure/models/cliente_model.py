from sqlalchemy import Column, String, Integer
from .base import Base


class ClienteModel(Base):
    __tablename__ = "clientes"
    
    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    identificacion = Column(String, nullable=True, unique=True)
    correo = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    celular = Column(String, nullable=True)

