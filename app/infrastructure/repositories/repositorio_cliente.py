from typing import Optional, List
from sqlalchemy.orm import Session

from ...domain.entidades import Cliente
from ..models.cliente_model import ClienteModel


class RepositorioClienteSQL:
    def __init__(self, sesion: Session):
        self.sesion = sesion
    
    def buscar_o_crear_por_nombre(self, nombre: str) -> Cliente:
        modelo = self.sesion.query(ClienteModel).filter(ClienteModel.nombre == nombre).first()
        
        if modelo:
            return Cliente(nombre=modelo.nombre, id_cliente=modelo.id_cliente)
        
        cliente = Cliente(nombre=nombre)
        modelo = ClienteModel(
            id_cliente=cliente.id_cliente,
            nombre=cliente.nombre
        )
        self.sesion.add(modelo)
        self.sesion.flush()
        
        return cliente
    
    def obtener(self, id_cliente: str) -> Optional[Cliente]:
        m = self.sesion.query(ClienteModel).filter(ClienteModel.id_cliente == id_cliente).first()
        if m is None:
            return None
        
        return Cliente(nombre=m.nombre, id_cliente=m.id_cliente)
    
    def listar(self) -> List[Cliente]:
        modelos = self.sesion.query(ClienteModel).all()
        clientes = []
        for m in modelos:
            clientes.append(Cliente(nombre=m.nombre, id_cliente=m.id_cliente))
        return clientes
    
    def guardar(self, cliente: Cliente) -> None:
        m = self.sesion.query(ClienteModel).filter(ClienteModel.id_cliente == cliente.id_cliente).first()
        if m:
            m.nombre = cliente.nombre
        else:
            nuevo = ClienteModel(id_cliente=cliente.id_cliente, nombre=cliente.nombre)
            self.sesion.add(nuevo)
        self.sesion.commit()

