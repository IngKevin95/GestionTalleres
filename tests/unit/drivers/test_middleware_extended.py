import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from starlette.middleware.base import BaseHTTPMiddleware


class TestLoggingMiddlewareClass:
    """Tests para la clase LoggingMiddleware"""
    
    def test_logging_middleware_is_base_http_middleware(self):
        """Test que LoggingMiddleware hereda de BaseHTTPMiddleware"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        assert issubclass(LoggingMiddleware, BaseHTTPMiddleware)
    
    def test_logging_middleware_can_instantiate(self):
        """Test que LoggingMiddleware se puede instanciar"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert middleware is not None
    
    def test_logging_middleware_has_app_attribute(self):
        """Test que middleware tiene atributo app"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert hasattr(middleware, 'app')




class TestLoggingMiddlewareMethods:
    """Tests para métodos de LoggingMiddleware"""
    
    def test_logging_middleware_has_dispatch(self):
        """Test que LoggingMiddleware tiene método dispatch"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert hasattr(middleware, 'dispatch')
        assert callable(middleware.dispatch)


class TestLoggingMiddlewareIntegration:
    """Tests de integración para LoggingMiddleware"""
    
    def test_middleware_with_app(self):
        """Test que middleware funciona con app"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert middleware.app == mock_app
    
    @pytest.mark.asyncio
    async def test_middleware_with_different_paths(self):
        """Test que middleware funciona con diferentes paths"""
        from app.drivers.api.middleware import LoggingMiddleware
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        app = FastAPI()
        middleware = LoggingMiddleware(app)
        
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/health"
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        
        call_next = AsyncMock(return_value=JSONResponse({"status": "ok"}))
        
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
