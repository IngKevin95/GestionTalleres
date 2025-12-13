from .enums import CodigoError


class ErrorDominio(Exception):
    def __init__(self, codigo: CodigoError, mensaje: str):
        self.codigo = codigo
        self.mensaje = mensaje
        super().__init__(mensaje)

