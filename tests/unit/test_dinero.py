from decimal import Decimal
from app.domain.dinero import a_decimal, redondear_mitad_par


def test_a_decimal():
    assert a_decimal("10.50") == Decimal("10.50")
    assert a_decimal(10.50) == Decimal("10.50")
    assert a_decimal(10) == Decimal("10")


def test_redondear_mitad_par_2_005():
    valor = Decimal("2.005")
    resultado = redondear_mitad_par(valor, 2)
    assert resultado == Decimal("2.00")


def test_redondear_mitad_par_2_015():
    valor = Decimal("2.015")
    resultado = redondear_mitad_par(valor, 2)
    assert resultado == Decimal("2.02")


def test_redondear_mitad_par_2_025():
    valor = Decimal("2.025")
    resultado = redondear_mitad_par(valor, 2)
    assert resultado == Decimal("2.02")


def test_redondear_mitad_par_2_035():
    valor = Decimal("2.035")
    resultado = redondear_mitad_par(valor, 2)
    assert resultado == Decimal("2.04")


def test_redondear_mitad_par_ejemplo_autorizacion():
    subtotal = Decimal("11500.00")
    monto_con_iva = subtotal * Decimal("1.16")
    resultado = redondear_mitad_par(monto_con_iva, 2)
    assert resultado == Decimal("13340.00")

