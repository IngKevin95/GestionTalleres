"""Tests para enumeraciones de dominio."""
import pytest
from app.domain.enums.order_status import EstadoOrden
from app.domain.enums.error_code import CodigoError


class TestEstadoOrdenEnum:
    """Tests para enumeración EstadoOrden."""
    
    def test_estado_creada_existe(self):
        """Test que CREATED existe en enum."""
        assert hasattr(EstadoOrden, 'CREATED')
    
    def test_estado_diagnosticado_existe(self):
        """Test que DIAGNOSED existe en enum."""
        assert hasattr(EstadoOrden, 'DIAGNOSED')
    
    def test_enum_values_validos(self):
        """Test que enum tiene valores válidos."""
        assert EstadoOrden.CREATED is not None


class TestCodigoErrorEnum:
    """Tests para enumeración CodigoError."""
    
    def test_codigo_error_existe(self):
        """Test que CodigoError es importable."""
        assert CodigoError is not None
    
    def test_codigo_error_valores(self):
        """Test que CodigoError tiene valores."""
        assert len(list(CodigoError)) > 0
