from decimal import Decimal
import os
from unittest.mock import patch
from app.domain.dinero import a_decimal, redondear_mitad_par
from app.domain.exceptions import ErrorDominio
from app.domain.enums import CodigoError
from app.domain.zona_horaria import obtener_zona_horaria, ahora


def test_a_decimal_con_string():
    resultado = a_decimal("10.50")
    assert resultado == Decimal("10.50")


def test_a_decimal_con_float():
    resultado = a_decimal(10.50)
    assert resultado == Decimal("10.50")


def test_a_decimal_con_int():
    resultado = a_decimal(10)
    assert resultado == Decimal("10")


def test_redondear_mitad_par_decimales_cero():
    valor = Decimal("10.5")
    resultado = redondear_mitad_par(valor, 0)
    assert resultado == Decimal("10")


def test_redondear_mitad_par_un_decimal():
    valor = Decimal("10.55")
    resultado = redondear_mitad_par(valor, 1)
    assert resultado == Decimal("10.6")


def test_redondear_mitad_par_tres_decimales():
    valor = Decimal("10.5555")
    resultado = redondear_mitad_par(valor, 3)
    assert isinstance(resultado, Decimal)


def test_error_dominio():
    error = ErrorDominio(CodigoError.ORDER_NOT_FOUND, "Orden no encontrada")
    assert error.codigo == CodigoError.ORDER_NOT_FOUND
    assert error.mensaje == "Orden no encontrada"
    assert str(error) == "Orden no encontrada"


def test_obtener_zona_horaria_default():
    with patch.dict(os.environ, {}, clear=True):
        tz = obtener_zona_horaria()
        assert tz is not None


def test_obtener_zona_horaria_custom():
    with patch.dict(os.environ, {"TIMEZONE": "America/New_York"}):
        tz = obtener_zona_horaria()
        assert tz is not None


def test_obtener_zona_horaria_invalida():
    with patch.dict(os.environ, {"TIMEZONE": "Zona/Invalida"}):
        tz = obtener_zona_horaria()
        assert tz is not None


def test_ahora():
    fecha = ahora()
    assert fecha is not None
    assert hasattr(fecha, 'year')

