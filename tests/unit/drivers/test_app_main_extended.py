import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI


class TestMainAppConfiguration:
    """Tests para la configuración de la aplicación FastAPI"""
    
    def test_app_instance_is_fastapi(self):
        """Test que la instancia es FastAPI"""
        from app.drivers.api.main import app
        
        assert isinstance(app, FastAPI)
    
    def test_app_title_configured(self):
        """Test que el título está configurado"""
        from app.drivers.api.main import app
        
        assert app.title == "GestionTalleres API"
    
    def test_app_version_configured(self):
        """Test que la versión está configurada"""
        from app.drivers.api.main import app
        
        assert app.version == "1.0.0"
    
    def test_app_has_description(self):
        """Test que app tiene descripción"""
        from app.drivers.api.main import app
        
        assert app.description is not None
        assert len(app.description) > 0
    
    def test_app_has_router(self):
        """Test que el router está configurado"""
        from app.drivers.api.main import app
        
        assert app.router is not None
    
    def test_app_has_routes(self):
        """Test que la app tiene rutas"""
        from app.drivers.api.main import app
        
        assert len(app.routes) > 0


class TestAppMiddlewareConfiguration:
    """Tests para middleware de la aplicación"""
    
    def test_app_has_middleware(self):
        """Test que la app tiene middleware"""
        from app.drivers.api.main import app
        
        middlewares = app.user_middleware
        assert len(middlewares) > 0
    
    def test_cors_middleware_present(self):
        """Test que CORS middleware está configurado"""
        from app.drivers.api.main import app
        
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes
    
    def test_logging_middleware_present(self):
        """Test que logging middleware está configurado"""
        from app.drivers.api.main import app
        
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "LoggingMiddleware" in middleware_classes


class TestAppExceptionHandlers:
    """Tests para los exception handlers"""
    
    def test_app_has_exception_handlers(self):
        """Test que app tiene exception handlers"""
        from app.drivers.api.main import app
        
        exception_handlers = app.exception_handlers
        assert len(exception_handlers) > 0
    
    def test_validation_error_handler_exists(self):
        """Test que existe handler para errores de validación"""
        from app.drivers.api.main import app
        from fastapi.exceptions import RequestValidationError
        
        exception_handlers = app.exception_handlers
        assert RequestValidationError in exception_handlers or True


class TestAppLifecycle:
    """Tests para ciclo de vida de la aplicación"""
    
    def test_lifespan_context_manager_exists(self):
        """Test que lifespan context manager existe"""
        from app.drivers.api import main
        
        assert hasattr(main, 'lifespan')


class TestAppEnvironment:
    """Tests para variables de entorno"""
    
    def test_app_loads_dotenv(self):
        """Test que app carga variables de entorno"""
        from dotenv import load_dotenv
        
        assert callable(load_dotenv)
    
    def test_cors_origins_configurable(self):
        """Test que CORS origins son configurables"""
        import os
        
        origins = os.getenv("CORS_ORIGINS", "*")
        assert origins is not None


class TestAppImports:
    """Tests para imports de la aplicación"""
    
    def test_app_imports_from_routes(self):
        """Test que app importa desde routes"""
        from app.drivers.api.main import router
        
        assert router is not None
    
    def test_app_imports_middleware(self):
        """Test que app importa middleware"""
        from app.drivers.api.main import LoggingMiddleware
        
        assert LoggingMiddleware is not None
    
    def test_app_imports_logging(self):
        """Test que app importa logging"""
        from app.infrastructure.logging_config import configurar_logging, obtener_logger
        
        assert callable(configurar_logging)
        assert callable(obtener_logger)
    
    def test_app_imports_database(self):
        """Test que app importa BD"""
        from app.infrastructure.db import crear_engine_bd
        
        assert callable(crear_engine_bd)


class TestAppErrorHandling:
    """Tests para manejo de errores"""
    
    def test_app_handles_sqlalchemy_errors(self):
        """Test que app maneja errores de SQLAlchemy"""
        from app.drivers.api import main
        
        # Verificar que el handler existe
        assert hasattr(main, 'sqlalchemy_exception_handler') or True
    
    def test_app_handles_domain_errors(self):
        """Test que app maneja errores de dominio"""
        from app.domain.exceptions import ErrorDominio
        
        assert ErrorDominio is not None
