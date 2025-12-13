from decimal import Decimal
from typing import Optional
from uuid import uuid4


class Componente:
    def __init__(self, descripcion: str, costo_estimado: Decimal, costo_real: Optional[Decimal] = None):
        self.id_componente = str(uuid4())
        self.descripcion = descripcion
        self.costo_estimado = costo_estimado
        self.costo_real = costo_real

