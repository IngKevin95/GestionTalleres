from sqlalchemy import Column, String
from .base import Base


class ClienteModel(Base):
    __tablename__ = "clientes"
    
    id_cliente = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)

