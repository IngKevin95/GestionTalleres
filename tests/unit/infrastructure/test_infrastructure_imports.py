"""Tests para imports y funcionalidad básica de la capa de infraestructura."""
import pytest
from unittest.mock import Mock


class TestInfrastructureDatabase:
    """Tests para infraestructura de BD."""
    
    def test_obtener_url_bd_default(self):
        """Test obtener_url_bd con valores default."""
        from app.infrastructure.db import obtener_url_bd
        
        url = obtener_url_bd()
        assert "postgresql" in url
    
    def test_crear_engine_bd_callable(self):
        """Test que crear_engine_bd es callable."""
        from app.infrastructure.db import crear_engine_bd
        
        assert callable(crear_engine_bd)


class TestLoggingConfiguration:
    """Tests para configuración de logging."""
    
    def test_configurar_logging_callable(self):
        """Test que configurar_logging es callable."""
        from app.infrastructure.logging_config import configurar_logging
        
        assert callable(configurar_logging)
    
    def test_obtener_logger_callable(self):
        """Test que obtener_logger es callable."""
        from app.infrastructure.logging_config import obtener_logger
        
        assert callable(obtener_logger)
    
    def test_obtener_logger_returns_logger(self):
        """Test que obtener_logger retorna logger válido."""
        from app.infrastructure.logging_config import obtener_logger
        import logging
        
        logger = obtener_logger("test")
        assert isinstance(logger, logging.Logger)
    
    def test_obtener_logger_con_nombre_largo(self):
        """Test obtener_logger con nombre largo."""
        from app.infrastructure.logging_config import obtener_logger
        
        logger = obtener_logger("app.drivers.api.routes.create_order")
        assert "create_order" in logger.name
    
    def test_configurar_logging_execution(self):
        """Test que configurar_logging se ejecuta sin error."""
        from app.infrastructure.logging_config import configurar_logging
        
        try:
            configurar_logging()
        except Exception as e:
            pytest.fail(f"configurar_logging lanzó excepción: {e}")


class TestInfrastructureModels:
    """Tests para modelos de infraestructura."""
    
    def test_base_model_import(self):
        """Test importar Base model."""
        from app.infrastructure.models.base import Base
        
        assert Base is not None
    
    def test_orden_model_import(self):
        """Test importar OrdenModel."""
        from app.infrastructure.models.orden_model import OrdenModel
        
        assert OrdenModel is not None
    
    def test_cliente_model_import(self):
        """Test importar ClienteModel."""
        from app.infrastructure.models.cliente_model import ClienteModel
        
        assert ClienteModel is not None
    
    def test_vehiculo_model_import(self):
        """Test importar VehiculoModel."""
        from app.infrastructure.models.vehiculo_model import VehiculoModel
        
        assert VehiculoModel.__name__ == "VehiculoModel"
    
    def test_servicio_model_import(self):
        """Test importar ServicioModel."""
        from app.infrastructure.models.servicio_model import ServicioModel
        
        assert ServicioModel is not None
    
    def test_componente_model_import(self):
        """Test importar ComponenteModel."""
        from app.infrastructure.models.componente_model import ComponenteModel
        
        assert ComponenteModel is not None
    
    def test_evento_model_import(self):
        """Test importar EventoModel."""
        from app.infrastructure.models.evento_model import EventoModel
        
        assert EventoModel is not None


class TestRepositoriesImports:
    """Tests para importar repositorios."""
    
    def test_repositorio_orden_import(self):
        """Test importar RepositorioOrden."""
        from app.infrastructure.repositories.repositorio_orden import RepositorioOrden
        
        assert RepositorioOrden is not None
    
    def test_repositorio_cliente_import(self):
        """Test importar RepositorioClienteSQL."""
        from app.infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
        
        assert RepositorioClienteSQL is not None
    
    def test_repositorio_vehiculo_import(self):
        """Test importar RepositorioVehiculoSQL."""
        from app.infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
        
        assert RepositorioVehiculoSQL.__name__ == "RepositorioVehiculoSQL"
    
    def test_repositorio_servicio_import(self):
        """Test importar RepositorioServicioSQL."""
        from app.infrastructure.repositories.repositorio_servicio import RepositorioServicioSQL
        
        assert RepositorioServicioSQL is not None
    
    def test_repositorio_evento_import(self):
        """Test importar RepositorioEventoSQL."""
        from app.infrastructure.repositories.repositorio_evento import RepositorioEventoSQL
        
        assert RepositorioEventoSQL is not None


class TestRepositoryEdgeCases:
    """Tests para casos edge en repositorios."""
    
    def test_repositorio_cliente_obtener_no_existe(self):
        """Test obtener cliente que no existe."""
        from app.infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
        
        sesion = Mock()
        sesion.query.return_value.filter.return_value.first.return_value = None
        
        repo = RepositorioClienteSQL(sesion)
        resultado = repo.obtener("NO_EXISTE")
        
        assert resultado is None
    
    def test_repositorio_vehiculo_obtener_no_existe(self):
        """Test obtener vehículo que no existe."""
        from app.infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
        
        sesion = Mock()
        sesion.query.return_value.filter.return_value.first.return_value = None
        
        repo = RepositorioVehiculoSQL(sesion)
        resultado = repo.obtener("NO_EXISTE")
        
        assert resultado is None
    
    def test_repositorio_orden_obtener_no_existe(self):
        """Test obtener orden no existente."""
        from app.infrastructure.repositories.repositorio_orden import RepositorioOrden
        
        sesion = Mock()
        sesion.query.return_value.filter.return_value.first.return_value = None
        
        repo = RepositorioOrden(sesion)
        resultado = repo.obtener("NO_EXISTE")
        
        assert resultado is None


class TestInfrastructureLogger:
    """Tests para logger de infraestructura."""
    
    def test_almacen_eventos_logger_import(self):
        """Test AlmacenEventosLogger importable."""
        from app.infrastructure.logger import AlmacenEventosLogger
        
        assert AlmacenEventosLogger is not None
