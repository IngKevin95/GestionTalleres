from decimal import Decimal
from typing import List, Optional
from .component import Componente


class Servicio:
    def __init__(self, descripcion: str, costo_mano_obra_estimado: Decimal, componentes: List[Componente] = None):
        from ..exceptions import ErrorDominio
        from ..enums import CodigoError
        
        if costo_mano_obra_estimado < 0:
            raise ErrorDominio(CodigoError.INVALID_AMOUNT, f"Costo de mano de obra estimado debe ser positivo, se recibió: {costo_mano_obra_estimado}")
        
        self.id_servicio: Optional[int] = None
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
        """
        Calcula el costo real del servicio.
        
        Si hay un costo_real establecido explícitamente, lo retorna.
        Si no, calcula sumando:
        - Costo de mano de obra estimado
        - Costos reales de componentes (si existen) o costos estimados (si no)
        """
        if self.costo_real is not None:
            return self.costo_real
        
        total = self.costo_mano_obra_estimado
        for componente in self.componentes:
            if componente.costo_real is not None:
                total += componente.costo_real
            else:
                total += componente.costo_estimado
        
        return total

