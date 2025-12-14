"""Tests para middleware de la API."""
import pytest


class TestLoggingMiddleware:
    """Tests para middleware de logging."""
    
    def test_logging_middleware_import(self):
        """Test importar LoggingMiddleware."""
        from app.drivers.api.middleware import LoggingMiddleware
    
    def test_logging_middleware_base_http(self):
        """Test que LoggingMiddleware es middleware válido."""
        from app.drivers.api.middleware import LoggingMiddleware
        from starlette.middleware.base import BaseHTTPMiddleware
        
        assert issubclass(LoggingMiddleware, BaseHTTPMiddleware)
