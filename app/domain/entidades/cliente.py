from uuid import uuid4


class Cliente:
    def __init__(self, nombre: str, id_cliente: str = None):
        self.id_cliente = id_cliente or str(uuid4())
        self.nombre = nombre

