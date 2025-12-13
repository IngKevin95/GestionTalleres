from decimal import Decimal, ROUND_HALF_EVEN


def a_decimal(valor) -> Decimal:
    return Decimal(str(valor))


def redondear_mitad_par(valor: Decimal, decimales: int = 2) -> Decimal:
    if decimales <= 0:
        return valor.quantize(Decimal('1'), rounding=ROUND_HALF_EVEN)
    
    # Construir string de cuantización
    cadena = '0.' + '0' * (decimales - 1) + '1'
    return valor.quantize(Decimal(cadena), rounding=ROUND_HALF_EVEN)

