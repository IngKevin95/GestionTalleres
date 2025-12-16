from typing import Optional
from .enums import CodigoError


class ErrorDominio(Exception):
    def __init__(self, codigo: CodigoError, mensaje: str, contexto: Optional[dict] = None):
        self.codigo = codigo
        self.mensaje = mensaje
        self.contexto = contexto or {}
        super().__init__(mensaje)
    
    @classmethod
    def con_contexto(cls, codigo: CodigoError, mensaje: str, **kwargs):
        return cls(codigo, mensaje, contexto=kwargs)

