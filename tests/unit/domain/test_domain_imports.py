"""Tests para imports y funcionalidad básica de la capa de dominio."""
import pytest
from unittest.mock import Mock
from decimal import Decimal


class TestDomainEntidades:
    """Tests para entidades de dominio."""
    
    def test_orden_import(self):
        """Test importar Orden."""
        from app.domain.entidades.order import Orden
        
        assert Orden is not None
    
    def test_cliente_import(self):
        """Test importar Cliente."""
        from app.domain.entidades.cliente import Cliente
        
        assert Cliente is not None
    
    def test_vehiculo_import(self):
        """Test importar Vehiculo."""
        from app.domain.entidades.vehiculo import Vehiculo
        
        assert Vehiculo.__name__ == "Vehiculo"
    
    def test_servicio_import(self):
        """Test importar Servicio."""
        from app.domain.entidades.service import Servicio
        
        assert Servicio is not None
    
    def test_componente_import(self):
        """Test importar Componente."""
        from app.domain.entidades.component import Componente
        
        assert Componente is not None
    
    def test_evento_import(self):
        """Test importar Evento."""
        from app.domain.entidades.event import Evento
        
        assert Evento is not None


class TestDomainExceptions:
    """Tests para excepciones de dominio."""
    
    def test_error_dominio_import(self):
        """Test importar ErrorDominio."""
        from app.domain.exceptions import ErrorDominio
        
        assert ErrorDominio is not None
    
    def test_error_dominio_creation(self):
        """Test crear ErrorDominio."""
        from app.domain.exceptions import ErrorDominio
        from app.domain.enums.error_code import CodigoError
        
        error = ErrorDominio(
            codigo=CodigoError.INVALID_STATE,
            mensaje="Test error"
        )
        assert error.codigo == CodigoError.INVALID_STATE
        assert error.mensaje == "Test error"


class TestDomainEnums:
    """Tests para enums de dominio."""
    
    def test_order_status_import(self):
        """Test importar EstadoOrden."""
        from app.domain.enums.order_status import EstadoOrden
        
        assert EstadoOrden is not None
    
    def test_error_code_import(self):
        """Test importar CodigoError."""
        from app.domain.enums.error_code import CodigoError
        
        assert CodigoError is not None


class TestDomainValueObjects:
    """Tests para value objects de dominio."""
    
    def test_dinero_import(self):
        """Test importar módulo dinero."""
        from app.domain import dinero
        
        assert dinero is not None
    
    def test_zona_horaria_import(self):
        """Test importar zona_horaria."""
        from app.domain.zona_horaria import obtener_zona_horaria
        
        assert callable(obtener_zona_horaria)
