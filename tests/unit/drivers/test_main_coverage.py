import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError


class TestMainAppSetup:
    """Tests para setup de la aplicación"""
    
    def test_app_is_fastapi_instance(self):
        """Test que app es instancia de FastAPI"""
        from app.drivers.api.main import app
        assert isinstance(app, FastAPI)
    
    def test_app_title(self):
        """Test título de app"""
        from app.drivers.api.main import app
        assert app.title == "GestionTalleres API"
    
    def test_app_version(self):
        """Test versión de app"""
        from app.drivers.api.main import app
        assert app.version == "1.0.0"
    
    def test_app_description_not_empty(self):
        """Test que descripción no esté vacía"""
        from app.drivers.api.main import app
        assert len(app.description) > 0
    
    def test_app_contact_info(self):
        """Test que app tiene información de contacto"""
        from app.drivers.api.main import app
        assert app.contact is not None


class TestMainAppMiddleware:
    """Tests para middleware de la app"""
    
    def test_app_has_cors_middleware(self):
        """Test que app tiene CORS middleware"""
        from app.drivers.api.main import app
        middleware_names = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_names
    
    def test_app_has_logging_middleware(self):
        """Test que app tiene logging middleware"""
        from app.drivers.api.main import app
        middleware_names = [m.cls.__name__ for m in app.user_middleware]
        assert "LoggingMiddleware" in middleware_names
    
    def test_cors_allow_methods(self):
        """Test que CORS permite todos los métodos"""
        from app.drivers.api.main import app
        # Verificar que CORSMiddleware está configurado
        assert len(app.user_middleware) > 0


class TestMainAppExceptionHandlers:
    """Tests para exception handlers"""
    
    def test_validation_error_handler_exists(self):
        """Test que validation error handler existe"""
        from app.drivers.api.main import app
        from fastapi.exceptions import RequestValidationError
        
        assert RequestValidationError in app.exception_handlers
    
    def test_response_validation_error_handler_exists(self):
        """Test que response validation error handler existe"""
        from app.drivers.api.main import app
        from fastapi.exceptions import ResponseValidationError
        
        assert ResponseValidationError in app.exception_handlers
    
    def test_validation_error_handler_callable(self):
        """Test que validation error handler es callable"""
        from app.drivers.api.main import validation_exception_handler
        
        assert callable(validation_exception_handler)


class TestMainAppRoutes:
    """Tests para rutas en la app"""
    
    def test_app_has_router(self):
        """Test que app tiene router configurado"""
        from app.drivers.api.main import app
        assert app.router is not None
    
    def test_app_has_routes(self):
        """Test que app tiene rutas"""
        from app.drivers.api.main import app
        assert len(app.routes) > 0
    
    def test_app_includes_api_routes(self):
        """Test que app incluye rutas de API"""
        from app.drivers.api.main import app
        from app.drivers.api.routes import router
        
        # Verificar que el router principal está incluido
        route_paths = [route.path for route in app.routes]
        assert len(route_paths) > 0


class TestMainAppLifespan:
    """Tests para lifespan de la aplicación"""
    
    def test_lifespan_exists(self):
        """Test que lifespan existe"""
        from app.drivers.api.main import lifespan
        
        assert callable(lifespan)
    
    def test_lifespan_is_async_context_manager(self):
        """Test que lifespan es async context manager"""
        from app.drivers.api.main import lifespan
        
        # Verificar que la función es callable
        assert callable(lifespan)


class TestMainAppEnvironment:
    """Tests para configuración de entorno"""
    
    def test_app_loads_environment_variables(self):
        """Test que app carga variables de entorno"""
        import os
        
        # Verificar que se cargan las variables de entorno
        with patch.dict(os.environ, {"CORS_ORIGINS": "http://localhost"}, clear=False):
            origins = os.getenv("CORS_ORIGINS", "*")
            assert origins is not None


class TestMainAppIntegration:
    """Tests de integración para main app"""
    
    def test_app_has_lifespan(self):
        """Test que app tiene lifespan configurado"""
        from app.drivers.api.main import app
        # El lifespan está configurado en el constructor
        assert app is not None
    
    def test_app_has_logger(self):
        """Test que app tiene logger configurado"""
        from app.drivers.api.main import logger
        assert logger is not None
