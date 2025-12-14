"""Tests para excepciones de dominio."""
import pytest
from app.domain.exceptions import ErrorDominio
from app.domain.enums.error_code import CodigoError


class TestErrorDominioException:
    """Tests para excepción ErrorDominio."""
    
    def test_error_dominio_creation(self):
        """Test crear ErrorDominio."""
        error = ErrorDominio(
            codigo=CodigoError.ORDER_NOT_FOUND,
            mensaje="Orden no encontrada"
        )
        assert error.codigo == CodigoError.ORDER_NOT_FOUND
        assert error.mensaje == "Orden no encontrada"
    
    def test_error_dominio_es_exception(self):
        """Test que ErrorDominio es Exception."""
        error = ErrorDominio(
            codigo=CodigoError.ORDER_NOT_FOUND,
            mensaje="Test"
        )
        assert isinstance(error, Exception)
    
    def test_error_dominio_mensaje_en_str(self):
        """Test que mensaje aparece en str."""
        error = ErrorDominio(
            codigo=CodigoError.ORDER_NOT_FOUND,
            mensaje="Orden no encontrada"
        )
        assert "Orden no encontrada" in str(error)
