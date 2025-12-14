from typing import Optional
from uuid import uuid4


class Vehiculo:
    def __init__(self, descripcion: str, id_cliente: str, marca: Optional[str] = None, modelo: Optional[str] = None, anio: Optional[int] = None, id_vehiculo: str = None):
        self.id_vehiculo = id_vehiculo or str(uuid4())
        self.descripcion = descripcion
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.id_cliente = id_cliente

