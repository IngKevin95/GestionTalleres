from decimal import Decimal
from typing import Optional


class Componente:
    def __init__(self, descripcion: str, costo_estimado: Decimal, costo_real: Optional[Decimal] = None):
        from ..exceptions import ErrorDominio
        from ..enums import CodigoError
        
        if costo_estimado < 0:
            raise ErrorDominio(CodigoError.INVALID_AMOUNT, f"Costo estimado debe ser positivo, se recibió: {costo_estimado}")
        
        if costo_real is not None and costo_real < 0:
            raise ErrorDominio(CodigoError.INVALID_AMOUNT, f"Costo real debe ser positivo, se recibió: {costo_real}")
        
        self.id_componente: Optional[int] = None
        self.descripcion = descripcion
        self.costo_estimado = costo_estimado
        self.costo_real = costo_real

