from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.orm import load_only

from ...domain.entidades import Cliente
from ..models.cliente_model import ClienteModel


class RepositorioClienteSQL:
    def __init__(self, sesion: Session):
        self.sesion = sesion
    
    def buscar_o_crear_por_nombre(self, nombre: str) -> Cliente:
        try:
            modelo = self.sesion.query(ClienteModel).options(load_only(ClienteModel.id_cliente, ClienteModel.nombre)).filter(ClienteModel.nombre == nombre).first()
        except Exception:
            modelo = None
        
        if modelo:
            return Cliente(
                nombre=modelo.nombre,
                id_cliente=modelo.id_cliente,
                identificacion=None,
                correo=None,
                direccion=None,
                celular=None
            )
        
        cliente = Cliente(nombre=nombre)
        try:
            modelo = ClienteModel(nombre=cliente.nombre)
            self.sesion.add(modelo)
            self.sesion.flush()
            cliente.id_cliente = modelo.id_cliente
        except Exception:
            self.sesion.rollback()
            raise
        
        return cliente
    
    def obtener(self, id_cliente: int) -> Optional[Cliente]:
        try:
            m = self.sesion.query(ClienteModel).options(load_only(ClienteModel.id_cliente, ClienteModel.nombre)).filter(ClienteModel.id_cliente == id_cliente).first()
        except Exception:
            m = None
        
        if m is None:
            return None
        
        return Cliente(
            nombre=m.nombre,
            id_cliente=m.id_cliente,
            identificacion=None,
            correo=None,
            direccion=None,
            celular=None
        )
    
    def listar(self) -> List[Cliente]:
        try:
            modelos = self.sesion.query(ClienteModel).options(load_only(ClienteModel.id_cliente, ClienteModel.nombre)).all()
        except Exception:
            modelos = []
        
        clientes = []
        for m in modelos:
            clientes.append(Cliente(
                nombre=m.nombre,
                id_cliente=m.id_cliente,
                identificacion=None,
                correo=None,
                direccion=None,
                celular=None
            ))
        return clientes
    
    def guardar(self, cliente: Cliente) -> None:
        try:
            if cliente.id_cliente is not None:
                m = self.sesion.query(ClienteModel).filter(ClienteModel.id_cliente == cliente.id_cliente).first()
                if m:
                    m.nombre = cliente.nombre
                else:
                    nuevo = ClienteModel(
                        id_cliente=cliente.id_cliente,
                        nombre=cliente.nombre
                    )
                    self.sesion.add(nuevo)
            else:
                nuevo = ClienteModel(nombre=cliente.nombre)
                self.sesion.add(nuevo)
                self.sesion.flush()
                cliente.id_cliente = nuevo.id_cliente
            self.sesion.commit()
        except Exception:
            self.sesion.rollback()
            raise

