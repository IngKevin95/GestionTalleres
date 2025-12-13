from decimal import Decimal
from typing import List, Optional
from uuid import uuid4
from .component import Componente


class Servicio:
    def __init__(self, descripcion: str, costo_mano_obra_estimado: Decimal, componentes: List[Componente] = None):
        self.id_servicio = str(uuid4())
        self.descripcion = descripcion
        self.costo_mano_obra_estimado = costo_mano_obra_estimado
        self.componentes = componentes or []
        self.completado = False
        self.costo_real: Optional[Decimal] = None

    def calcular_subtotal_estimado(self) -> Decimal:
        subtotal = self.costo_mano_obra_estimado
        for componente in self.componentes:
            subtotal += componente.costo_estimado
        return subtotal

    def calcular_costo_real(self) -> Decimal:
        if self.costo_real is not None:
            return self.costo_real
        
        # Si no hay costo real, calcular sumando componentes
        total = self.costo_mano_obra_estimado
        for componente in self.componentes:
            if componente.costo_real is not None:
                total += componente.costo_real
            else:
                total += componente.costo_estimado
        
        return total

