"""Tests para utilidades de dominio."""
import pytest
from decimal import Decimal
from app.domain.dinero import a_decimal, redondear_mitad_par


class TestConversorDinero:
    """Tests para conversión de dinero."""
    
    def test_a_decimal_desde_string(self):
        """Test convertir string a Decimal."""
        resultado = a_decimal("1000.50")
        assert resultado == Decimal("1000.50")
    
    def test_a_decimal_desde_float(self):
        """Test convertir float a Decimal."""
        resultado = a_decimal(1000.50)
        assert isinstance(resultado, Decimal)
    
    def test_a_decimal_desde_int(self):
        """Test convertir int a Decimal."""
        resultado = a_decimal(1000)
        assert resultado == Decimal("1000")


class TestRedondeador:
    """Tests para redondeo de dinero."""
    
    def test_redondear_sin_decimales(self):
        """Test redondear sin cambio."""
        resultado = redondear_mitad_par(Decimal("100"), 0)
        assert resultado == Decimal("100")
    
    def test_redondear_un_decimal(self):
        """Test redondear a un decimal."""
        resultado = redondear_mitad_par(Decimal("100.5"), 1)
        assert isinstance(resultado, Decimal)
