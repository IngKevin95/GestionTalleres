from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ...domain.entidades import Vehiculo
from ...domain.exceptions import ErrorDominio
from ...domain.enums import CodigoError
from ..models.vehiculo_model import VehiculoModel


class RepositorioVehiculoSQL:
    def __init__(self, sesion: Session):
        self.sesion = sesion
    
    def buscar_por_placa(self, placa: str) -> Optional[Vehiculo]:
        modelo = self.sesion.query(VehiculoModel).filter(VehiculoModel.placa == placa).first()
        if modelo is None:
            return None
        
        return Vehiculo(
            placa=modelo.placa,
            id_cliente=modelo.id_cliente,
            marca=modelo.marca,
            modelo=modelo.modelo,
            anio=modelo.anio,
            kilometraje=modelo.kilometraje,
            id_vehiculo=modelo.id_vehiculo
        )
    
    def buscar_por_criterio(self, id_vehiculo: Optional[int] = None, placa: Optional[str] = None) -> Optional[Vehiculo]:
        if id_vehiculo is not None:
            return self.obtener(id_vehiculo)
        elif placa is not None:
            return self.buscar_por_placa(placa)
        return None
    
    def buscar_o_crear_por_placa(self, placa: str, id_cliente: int, marca: Optional[str] = None, modelo: Optional[str] = None, anio: Optional[int] = None, kilometraje: Optional[int] = None) -> Vehiculo:
        from ..models.cliente_model import ClienteModel
        modelo_vehiculo = self.sesion.query(VehiculoModel).filter(VehiculoModel.placa == placa).first()
        if modelo_vehiculo:
            if modelo_vehiculo.id_cliente != id_cliente:
                cliente_actual = self.sesion.query(ClienteModel).filter(ClienteModel.id_cliente == modelo_vehiculo.id_cliente).first()
                nombre_cliente_actual = cliente_actual.nombre if cliente_actual else f"ID {modelo_vehiculo.id_cliente}"
                raise ErrorDominio(
                    CodigoError.PLACA_ASOCIADA_OTRO_CLIENTE,
                    f"La placa {placa} ya está asociada al cliente '{nombre_cliente_actual}' (ID: {modelo_vehiculo.id_cliente}). No se puede asociar a otro cliente."
                )
            return Vehiculo(
                placa=modelo_vehiculo.placa,
                id_cliente=modelo_vehiculo.id_cliente,
                marca=modelo_vehiculo.marca,
                modelo=modelo_vehiculo.modelo,
                anio=modelo_vehiculo.anio,
                kilometraje=modelo_vehiculo.kilometraje,
                id_vehiculo=modelo_vehiculo.id_vehiculo
            )
        
        vehiculo = Vehiculo(placa=placa, id_cliente=id_cliente, marca=marca, modelo=modelo, anio=anio, kilometraje=kilometraje)
        modelo_db = VehiculoModel(
            placa=vehiculo.placa,
            marca=vehiculo.marca,
            modelo=vehiculo.modelo,
            anio=vehiculo.anio,
            kilometraje=vehiculo.kilometraje,
            id_cliente=vehiculo.id_cliente
        )
        try:
            self.sesion.add(modelo_db)
            self.sesion.flush()
            vehiculo.id_vehiculo = modelo_db.id_vehiculo
            self.sesion.commit()
        except IntegrityError as e:
            self.sesion.rollback()
            if "placa" in str(e.orig).lower() or "unique" in str(e.orig).lower():
                vehiculo_existente = self.buscar_por_placa(placa)
                if vehiculo_existente and vehiculo_existente.id_cliente != id_cliente:
                    modelo_existente = self.sesion.query(VehiculoModel).filter(VehiculoModel.placa == placa).first()
                    nombre_cliente_actual = modelo_existente.cliente.nombre if modelo_existente and modelo_existente.cliente else "desconocido"
                    raise ErrorDominio(
                        CodigoError.PLACA_ASOCIADA_OTRO_CLIENTE,
                        f"La placa {placa} ya está asociada al cliente '{nombre_cliente_actual}' (ID: {vehiculo_existente.id_cliente}). No se puede asociar a otro cliente."
                    )
            raise
        except Exception:
            self.sesion.rollback()
            raise
        
        return vehiculo
    
    def obtener(self, id_vehiculo: int) -> Optional[Vehiculo]:
        m = self.sesion.query(VehiculoModel).filter(VehiculoModel.id_vehiculo == id_vehiculo).first()
        if m is None:
            return None
        
        return Vehiculo(
            placa=m.placa,
            id_cliente=m.id_cliente,
            marca=m.marca,
            modelo=m.modelo,
            anio=m.anio,
            kilometraje=m.kilometraje,
            id_vehiculo=m.id_vehiculo
        )
    
    def listar(self) -> List[Vehiculo]:
        modelos = self.sesion.query(VehiculoModel).all()
        vehiculos = []
        for m in modelos:
            vehiculos.append(Vehiculo(
                placa=m.placa,
                id_cliente=m.id_cliente,
                marca=m.marca,
                modelo=m.modelo,
                anio=m.anio,
                kilometraje=m.kilometraje,
                id_vehiculo=m.id_vehiculo
            ))
        return vehiculos
    
    def listar_por_cliente(self, id_cliente: int) -> List[Vehiculo]:
        modelos = self.sesion.query(VehiculoModel).filter(VehiculoModel.id_cliente == id_cliente).all()
        resultado = []
        for m in modelos:
            resultado.append(Vehiculo(
                placa=m.placa,
                id_cliente=m.id_cliente,
                marca=m.marca,
                modelo=m.modelo,
                anio=m.anio,
                kilometraje=m.kilometraje,
                id_vehiculo=m.id_vehiculo
            ))
        return resultado
    
    def guardar(self, vehiculo: Vehiculo) -> None:
        try:
            if vehiculo.id_vehiculo is not None:
                m = self.sesion.query(VehiculoModel).filter(VehiculoModel.id_vehiculo == vehiculo.id_vehiculo).first()
                if m:
                    m.placa = vehiculo.placa
                    m.marca = vehiculo.marca
                    m.modelo = vehiculo.modelo
                    m.anio = vehiculo.anio
                    m.kilometraje = vehiculo.kilometraje
                    m.id_cliente = vehiculo.id_cliente
                else:
                    nuevo = VehiculoModel(
                        id_vehiculo=vehiculo.id_vehiculo,
                        placa=vehiculo.placa,
                        marca=vehiculo.marca,
                        modelo=vehiculo.modelo,
                        anio=vehiculo.anio,
                        kilometraje=vehiculo.kilometraje,
                        id_cliente=vehiculo.id_cliente
                    )
                    self.sesion.add(nuevo)
            else:
                nuevo = VehiculoModel(
                    placa=vehiculo.placa,
                    marca=vehiculo.marca,
                    modelo=vehiculo.modelo,
                    anio=vehiculo.anio,
                    kilometraje=vehiculo.kilometraje,
                    id_cliente=vehiculo.id_cliente
                )
                self.sesion.add(nuevo)
                self.sesion.flush()
                vehiculo.id_vehiculo = nuevo.id_vehiculo
            self.sesion.commit()
        except Exception:
            self.sesion.rollback()
            raise

