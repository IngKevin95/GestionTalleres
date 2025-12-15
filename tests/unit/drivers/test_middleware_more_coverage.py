import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from starlette.middleware.base import BaseHTTPMiddleware




class TestLoggingMiddleware:
    """Tests para LoggingMiddleware"""
    
    def test_logging_middleware_init(self):
        """Test inicialización de LoggingMiddleware"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert middleware.app == mock_app
    
    def test_logging_middleware_is_base_http_middleware(self):
        """Test que LoggingMiddleware hereda de BaseHTTPMiddleware"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        assert issubclass(LoggingMiddleware, BaseHTTPMiddleware)
    
    @pytest.mark.asyncio
    async def test_logging_middleware_dispatch_exitoso(self):
        """Test dispatch exitoso"""
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
    
    @pytest.mark.asyncio
    async def test_logging_middleware_sin_cliente(self):
        """Test dispatch sin cliente"""
        from app.drivers.api.middleware import LoggingMiddleware
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        app = FastAPI()
        middleware = LoggingMiddleware(app)
        
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/ordenes"
        request.client = None
        
        call_next = AsyncMock(return_value=JSONResponse({"status": "ok"}))
        
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200


class TestMiddlewareIntegration:
    """Tests de integración para middleware"""
    
    def test_middleware_with_app_and_request(self):
        """Test middleware con app y request"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert middleware.app is not None
        assert hasattr(middleware, '_obtener_info_request')
        assert hasattr(middleware, '_extraer_body_json')
    
    @pytest.mark.asyncio
    async def test_middleware_request_info_fields(self):
        """Test que middleware funciona con diferentes métodos"""
        from app.drivers.api.middleware import LoggingMiddleware
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        app = FastAPI()
        middleware = LoggingMiddleware(app)
        
        request = MagicMock()
        request.method = "DELETE"
        request.url.path = "/ordenes/123"
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        
        call_next = AsyncMock(return_value=JSONResponse({"status": "ok"}))
        
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
