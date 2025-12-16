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
    
    def test_error_dominio_con_contexto(self):
        """Test ErrorDominio con contexto adicional."""
        contexto = {"order_id": "ORD-001", "user": "admin"}
        error = ErrorDominio(
            codigo=CodigoError.ORDER_NOT_FOUND,
            mensaje="Orden no encontrada",
            contexto=contexto
        )
        assert error.contexto == contexto
        assert error.contexto["order_id"] == "ORD-001"
    
    def test_error_dominio_sin_contexto_retrocompatible(self):
        """Test que ErrorDominio sin contexto funciona (retrocompatibilidad)."""
        error = ErrorDominio(
            codigo=CodigoError.ORDER_NOT_FOUND,
            mensaje="Orden no encontrada"
        )
        assert error.contexto == {}
    
    def test_error_dominio_con_contexto_vacio(self):
        """Test ErrorDominio con contexto None se convierte en dict vacío."""
        error = ErrorDominio(
            codigo=CodigoError.ORDER_NOT_FOUND,
            mensaje="Orden no encontrada",
            contexto=None
        )
        assert error.contexto == {}
    
    def test_error_dominio_metodo_con_contexto(self):
        """Test método de clase con_contexto."""
        error = ErrorDominio.con_contexto(
            codigo=CodigoError.INVALID_OPERATION,
            mensaje="Operación inválida",
            order_id="ORD-001",
            operation="CREATE"
        )
        assert error.codigo == CodigoError.INVALID_OPERATION
        assert error.mensaje == "Operación inválida"
        assert error.contexto["order_id"] == "ORD-001"
        assert error.contexto["operation"] == "CREATE"