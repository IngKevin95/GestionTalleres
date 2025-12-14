from sqlalchemy import Column, String, Integer
from .base import Base


class ClienteModel(Base):
    __tablename__ = "clientes"
    
    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)

