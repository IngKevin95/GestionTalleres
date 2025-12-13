from typing import Optional, List
from sqlalchemy.orm import Session

from ...domain.entidades import Vehiculo
from ..models.vehiculo_model import VehiculoModel


class RepositorioVehiculoSQL:
    def __init__(self, sesion: Session):
        self.sesion = sesion
    
    def buscar_o_crear_por_descripcion(self, descripcion: str, id_cliente: str) -> Vehiculo:
        modelo = self.sesion.query(VehiculoModel).filter(
            VehiculoModel.descripcion == descripcion,
            VehiculoModel.id_cliente == id_cliente
        ).first()
        
        if modelo:
            return Vehiculo(
                descripcion=modelo.descripcion,
                id_cliente=modelo.id_cliente,
                marca=modelo.marca,
                modelo=modelo.modelo,
                año=modelo.año,
                id_vehiculo=modelo.id_vehiculo
            )
        
        vehiculo = Vehiculo(descripcion=descripcion, id_cliente=id_cliente)
        modelo = VehiculoModel(
            id_vehiculo=vehiculo.id_vehiculo,
            descripcion=vehiculo.descripcion,
            marca=vehiculo.marca,
            modelo=vehiculo.modelo,
            año=vehiculo.año,
            id_cliente=vehiculo.id_cliente
        )
        self.sesion.add(modelo)
        self.sesion.flush()
        
        return vehiculo
    
    def obtener(self, id_vehiculo: str) -> Optional[Vehiculo]:
        m = self.sesion.query(VehiculoModel).filter(VehiculoModel.id_vehiculo == id_vehiculo).first()
        if m is None:
            return None
        
        return Vehiculo(
            descripcion=m.descripcion,
            id_cliente=m.id_cliente,
            marca=m.marca,
            modelo=m.modelo,
            año=m.año,
            id_vehiculo=m.id_vehiculo
        )
    
    def listar(self) -> List[Vehiculo]:
        modelos = self.sesion.query(VehiculoModel).all()
        vehiculos = []
        for m in modelos:
            vehiculos.append(Vehiculo(
                descripcion=m.descripcion,
                id_cliente=m.id_cliente,
                marca=m.marca,
                modelo=m.modelo,
                año=m.año,
                id_vehiculo=m.id_vehiculo
            ))
        return vehiculos
    
    def listar_por_cliente(self, id_cliente: str) -> List[Vehiculo]:
        modelos = self.sesion.query(VehiculoModel).filter(VehiculoModel.id_cliente == id_cliente).all()
        resultado = []
        for m in modelos:
            resultado.append(Vehiculo(
                descripcion=m.descripcion,
                id_cliente=m.id_cliente,
                marca=m.marca,
                modelo=m.modelo,
                año=m.año,
                id_vehiculo=m.id_vehiculo
            ))
        return resultado
    
    def guardar(self, vehiculo: Vehiculo) -> None:
        m = self.sesion.query(VehiculoModel).filter(VehiculoModel.id_vehiculo == vehiculo.id_vehiculo).first()
        if m:
            m.descripcion = vehiculo.descripcion
            m.marca = vehiculo.marca
            m.modelo = vehiculo.modelo
            m.año = vehiculo.año
            m.id_cliente = vehiculo.id_cliente
        else:
            nuevo = VehiculoModel(
                id_vehiculo=vehiculo.id_vehiculo,
                descripcion=vehiculo.descripcion,
                marca=vehiculo.marca,
                modelo=vehiculo.modelo,
                año=vehiculo.año,
                id_cliente=vehiculo.id_cliente
            )
            self.sesion.add(nuevo)
        self.sesion.commit()

