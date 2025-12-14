from typing import Optional


class Vehiculo:
    def __init__(self, descripcion: str, id_cliente: int, marca: Optional[str] = None, modelo: Optional[str] = None, anio: Optional[int] = None, kilometraje: Optional[int] = None, id_vehiculo: Optional[int] = None):
        self.id_vehiculo = id_vehiculo
        self.descripcion = descripcion
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.kilometraje = kilometraje
        self.id_cliente = id_cliente

