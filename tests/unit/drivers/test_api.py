"""Tests para main, middleware y dependencias de API."""
import pytest
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from unittest.mock import Mock
from app.drivers.api.main import app
from app.drivers.api.middleware import LoggingMiddleware
from app.drivers.api.dependencies import obtener_action_service, obtener_sesion


class TestMainApp:
    """Tests para FastAPI app principal."""
    
    def test_app_es_fastapi(self):
        """Test que app es FastAPI instance."""
        assert isinstance(app, FastAPI)
    
    def test_app_tiene_rutas(self):
        """Test que app tiene rutas."""
        routes = list(app.routes)
        assert len(routes) > 0
    
    def test_app_tiene_router(self):
        """Test que app tiene router."""
        assert app.router is not None
    
    def test_app_title(self):
        """Test que app tiene título."""
        assert app.title == "GestionTalleres API"


class TestLoggingMiddleware:
    """Tests para LoggingMiddleware."""
    
    def test_logging_middleware_es_base_http_middleware(self):
        """Test que LoggingMiddleware hereda de BaseHTTPMiddleware."""
        assert issubclass(LoggingMiddleware, BaseHTTPMiddleware)
    
    def test_logging_middleware_import(self):
        """Test importar LoggingMiddleware."""
        from app.drivers.api.middleware import LoggingMiddleware


class TestDependencies:
    """Tests para dependencias inyectables."""
    
    def test_obtener_action_service_callable(self):
        """Test que obtener_action_service es callable."""
        assert callable(obtener_action_service)
    
    def test_obtener_sesion_callable(self):
        """Test que obtener_sesion es callable."""
        assert callable(obtener_sesion)
