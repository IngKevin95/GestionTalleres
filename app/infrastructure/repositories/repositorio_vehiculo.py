from typing import Optional, List
from sqlalchemy.orm import Session

from ...domain.entidades import Vehiculo
from ..models.vehiculo_model import VehiculoModel


class RepositorioVehiculoSQL:
    def __init__(self, sesion: Session):
        self.sesion = sesion
    
    def buscar_o_crear_por_descripcion(self, descripcion: str, id_cliente: int) -> Vehiculo:
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
                anio=modelo.anio,
                id_vehiculo=modelo.id_vehiculo
            )
        
        vehiculo = Vehiculo(descripcion=descripcion, id_cliente=id_cliente)
        modelo = VehiculoModel(
            descripcion=vehiculo.descripcion,
            marca=vehiculo.marca,
            modelo=vehiculo.modelo,
            anio=vehiculo.anio,
            id_cliente=vehiculo.id_cliente
        )
        self.sesion.add(modelo)
        self.sesion.flush()
        vehiculo.id_vehiculo = modelo.id_vehiculo
        
        return vehiculo
    
    def obtener(self, id_vehiculo: int) -> Optional[Vehiculo]:
        m = self.sesion.query(VehiculoModel).filter(VehiculoModel.id_vehiculo == id_vehiculo).first()
        if m is None:
            return None
        
        return Vehiculo(
            descripcion=m.descripcion,
            id_cliente=m.id_cliente,
            marca=m.marca,
            modelo=m.modelo,
            anio=m.anio,
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
                anio=m.anio,
                id_vehiculo=m.id_vehiculo
            ))
        return vehiculos
    
    def listar_por_cliente(self, id_cliente: int) -> List[Vehiculo]:
        modelos = self.sesion.query(VehiculoModel).filter(VehiculoModel.id_cliente == id_cliente).all()
        resultado = []
        for m in modelos:
            resultado.append(Vehiculo(
                descripcion=m.descripcion,
                id_cliente=m.id_cliente,
                marca=m.marca,
                modelo=m.modelo,
                anio=m.anio,
                id_vehiculo=m.id_vehiculo
            ))
        return resultado
    
    def guardar(self, vehiculo: Vehiculo) -> None:
        if vehiculo.id_vehiculo is not None:
            m = self.sesion.query(VehiculoModel).filter(VehiculoModel.id_vehiculo == vehiculo.id_vehiculo).first()
            if m:
                m.descripcion = vehiculo.descripcion
                m.marca = vehiculo.marca
                m.modelo = vehiculo.modelo
                m.anio = vehiculo.anio
                m.id_cliente = vehiculo.id_cliente
            else:
                nuevo = VehiculoModel(
                    id_vehiculo=vehiculo.id_vehiculo,
                    descripcion=vehiculo.descripcion,
                    marca=vehiculo.marca,
                    modelo=vehiculo.modelo,
                    anio=vehiculo.anio,
                    id_cliente=vehiculo.id_cliente
                )
                self.sesion.add(nuevo)
        else:
            nuevo = VehiculoModel(
                descripcion=vehiculo.descripcion,
                marca=vehiculo.marca,
                modelo=vehiculo.modelo,
                anio=vehiculo.anio,
                id_cliente=vehiculo.id_cliente
            )
            self.sesion.add(nuevo)
            self.sesion.flush()
            vehiculo.id_vehiculo = nuevo.id_vehiculo
        self.sesion.commit()

