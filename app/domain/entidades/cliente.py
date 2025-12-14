from typing import Optional


class Cliente:
    def __init__(self, nombre: str, id_cliente: Optional[int] = None, identificacion: Optional[str] = None, correo: Optional[str] = None, direccion: Optional[str] = None, celular: Optional[str] = None):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.identificacion = identificacion
        self.correo = correo
        self.direccion = direccion
        self.celular = celular

