from typing import Optional


class Cliente:
    def __init__(self, nombre: str, id_cliente: Optional[int] = None):
        self.id_cliente = id_cliente
        self.nombre = nombre

