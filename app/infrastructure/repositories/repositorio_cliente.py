from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.orm import load_only

from ...domain.entidades import Cliente
from ..models.cliente_model import ClienteModel


class RepositorioClienteSQL:
    def __init__(self, sesion: Session):
        self.sesion = sesion
    
    def buscar_o_crear_por_nombre(self, nombre: str) -> Cliente:
        cliente_existente = self.buscar_por_nombre(nombre)
        if cliente_existente:
            return cliente_existente
        
        cliente = Cliente(nombre=nombre)
        try:
            modelo = ClienteModel(nombre=cliente.nombre)
            self.sesion.add(modelo)
            self.sesion.flush()
            cliente.id_cliente = modelo.id_cliente
            self.sesion.commit()
        except Exception:
            self.sesion.rollback()
            raise
        
        return cliente
    
    def buscar_por_identificacion(self, identificacion: str) -> Optional[Cliente]:
        try:
            m = self.sesion.query(ClienteModel).filter(ClienteModel.identificacion == identificacion).first()
        except Exception:
            m = None
        
        if m is None:
            return None
        
        return Cliente(
            nombre=m.nombre,
            id_cliente=m.id_cliente,
            identificacion=m.identificacion,
            correo=m.correo,
            direccion=m.direccion,
            celular=m.celular
        )
    
    def buscar_por_nombre(self, nombre: str) -> Optional[Cliente]:
        try:
            m = self.sesion.query(ClienteModel).filter(ClienteModel.nombre == nombre).first()
        except Exception:
            m = None
        
        if m is None:
            return None
        
        return Cliente(
            nombre=m.nombre,
            id_cliente=m.id_cliente,
            identificacion=m.identificacion,
            correo=m.correo,
            direccion=m.direccion,
            celular=m.celular
        )
    
    def buscar_por_criterio(self, id_cliente: Optional[int] = None, identificacion: Optional[str] = None, nombre: Optional[str] = None) -> Optional[Cliente]:
        if id_cliente is not None:
            return self.obtener(id_cliente)
        elif identificacion is not None:
            return self.buscar_por_identificacion(identificacion)
        elif nombre is not None:
            return self.buscar_por_nombre(nombre)
        return None
    
    def buscar_o_crear_por_criterio(self, id_cliente: Optional[int] = None, identificacion: Optional[str] = None, nombre: Optional[str] = None, correo: Optional[str] = None, direccion: Optional[str] = None, celular: Optional[str] = None) -> Cliente:
        cliente_existente = self.buscar_por_criterio(id_cliente=id_cliente, identificacion=identificacion, nombre=nombre)
        if cliente_existente:
            return cliente_existente
        
        if nombre is None:
            raise ValueError("nombre es requerido para crear un nuevo cliente")
        
        cliente = Cliente(nombre=nombre, identificacion=identificacion, correo=correo, direccion=direccion, celular=celular)
        try:
            modelo = ClienteModel(
                nombre=cliente.nombre,
                identificacion=cliente.identificacion,
                correo=cliente.correo,
                direccion=cliente.direccion,
                celular=cliente.celular
            )
            self.sesion.add(modelo)
            self.sesion.flush()
            cliente.id_cliente = modelo.id_cliente
            self.sesion.commit()
            return cliente
        except Exception as e:
            self.sesion.rollback()
            raise
    
    def obtener(self, id_cliente: int) -> Optional[Cliente]:
        try:
            m = self.sesion.query(ClienteModel).filter(ClienteModel.id_cliente == id_cliente).first()
        except Exception:
            m = None
        
        if m is None:
            return None
        
        return Cliente(
            nombre=m.nombre,
            id_cliente=m.id_cliente,
            identificacion=m.identificacion,
            correo=m.correo,
            direccion=m.direccion,
            celular=m.celular
        )
    
    def listar(self) -> List[Cliente]:
        try:
            modelos = self.sesion.query(ClienteModel).all()
        except Exception:
            modelos = []
        
        clientes = []
        for m in modelos:
            clientes.append(Cliente(
                nombre=m.nombre,
                id_cliente=m.id_cliente,
                identificacion=m.identificacion,
                correo=m.correo,
                direccion=m.direccion,
                celular=m.celular
            ))
        return clientes
    
    def guardar(self, cliente: Cliente) -> None:
        try:
            if cliente.id_cliente is not None:
                m = self.sesion.query(ClienteModel).filter(ClienteModel.id_cliente == cliente.id_cliente).first()
                if m:
                    m.nombre = cliente.nombre
                    m.identificacion = cliente.identificacion
                    m.correo = cliente.correo
                    m.direccion = cliente.direccion
                    m.celular = cliente.celular
                else:
                    nuevo = ClienteModel(
                        id_cliente=cliente.id_cliente,
                        nombre=cliente.nombre,
                        identificacion=cliente.identificacion,
                        correo=cliente.correo,
                        direccion=cliente.direccion,
                        celular=cliente.celular
                    )
                    self.sesion.add(nuevo)
            else:
                nuevo = ClienteModel(
                    nombre=cliente.nombre,
                    identificacion=cliente.identificacion,
                    correo=cliente.correo,
                    direccion=cliente.direccion,
                    celular=cliente.celular
                )
                self.sesion.add(nuevo)
                self.sesion.flush()
                cliente.id_cliente = nuevo.id_cliente
            self.sesion.commit()
        except Exception:
            self.sesion.rollback()
            raise

