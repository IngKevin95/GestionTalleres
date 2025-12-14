"""
Tests adicionales para aumentar la cobertura al 80%.
Enfocados en areas con baja cobertura: repositorios y modelos.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from decimal import Decimal

from app.infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
from app.infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
from app.infrastructure.models.cliente_model import ClienteModel
from app.infrastructure.models.vehiculo_model import VehiculoModel


@pytest.fixture
def mock_session():
    """Crear una sesión mock"""
    return MagicMock(spec=Session)


class TestRepositorioClienteCobertura:
    """Tests adicionales para RepositorioClienteSQL"""
    
    def test_obtener_cliente_no_existe(self, mock_session):
        """Probar obtener cliente que no existe"""
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        repo = RepositorioClienteSQL(mock_session)
        result = repo.obtener("CLIENTE-NO-EXISTE")
        
        assert result is None


class TestRepositorioVehiculoCobertura:
    """Tests adicionales para RepositorioVehiculoSQL"""
    
    def test_obtener_vehiculo_no_existe(self, mock_session):
        """Probar obtener vehículo que no existe"""
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        repo = RepositorioVehiculoSQL(mock_session)
        result = repo.obtener("VEH-NO-EXISTE")
        
        assert result is None
    
    def test_listar_vehiculos_por_cliente(self, mock_session):
        """Probar listar vehículos de un cliente"""
        vehiculo_mock = MagicMock()
        vehiculo_mock.id_vehiculo = "VEH-001"
        vehiculo_mock.descripcion = "Toyota"
        mock_session.query.return_value.filter.return_value.all.return_value = [vehiculo_mock]
        
        repo = RepositorioVehiculoSQL(mock_session)
        result = repo.listar_por_cliente("CUST-001")
        
        assert len(result) == 1
        assert result[0].id_vehiculo == "VEH-001"


class TestLoggingConfigCobertura:
    """Tests para aumentar cobertura de logging_config"""
    
    def test_obtener_logger_con_nombres_diferentes(self):
        """Probar obtener múltiples loggers con diferentes nombres"""
        from app.infrastructure.logging_config import obtener_logger
        
        logger1 = obtener_logger("test_logger_1")
        logger2 = obtener_logger("test_logger_2")
        
        assert logger1 is not None
        assert logger2 is not None
        assert logger1.name != logger2.name


class TestBaseModelCobertura:
    """Tests para mejorar cobertura del modelo base"""
    
    def test_fecha_creacion_default_function(self):
        """Probar la función de fecha creación default"""
        from app.infrastructure.models.base import fecha_creacion_default
        
        result = fecha_creacion_default()
        assert result is not None


class TestMainCobertura:
    """Tests para mejorar cobertura del módulo main"""
    
    def test_app_creation(self):
        """Probar que la aplicación se crea correctamente"""
        from app.drivers.api.main import app
        
        assert app is not None
        assert hasattr(app, 'router')
