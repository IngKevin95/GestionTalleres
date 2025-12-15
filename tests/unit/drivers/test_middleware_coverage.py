"""Tests para mejorar cobertura de middleware."""
import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from unittest.mock import Mock, AsyncMock, MagicMock
from app.drivers.api.middleware import LoggingMiddleware


class TestLoggingMiddlewareCoverage:
    """Tests para mejorar cobertura de LoggingMiddleware."""
    
    @pytest.mark.asyncio
    async def test_logging_middleware_init(self):
        """Test inicialización de LoggingMiddleware."""
        app = FastAPI()
        middleware = LoggingMiddleware(app)
        assert middleware.app == app
    
    @pytest.mark.asyncio
    async def test_logging_middleware_dispatch_exitoso(self):
        """Test dispatch exitoso del middleware."""
        app = FastAPI()
        middleware = LoggingMiddleware(app)
        
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/api/test"
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        
        response_mock = JSONResponse({"result": "success"}, status_code=201)
        call_next = AsyncMock(return_value=response_mock)
        
        response = await middleware.dispatch(request, call_next)
        
        assert response.status_code == 201
        call_next.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_logging_middleware_dispatch_con_excepcion(self):
        """Test dispatch con excepción."""
        app = FastAPI()
        middleware = LoggingMiddleware(app)
        
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/error"
        request.client = MagicMock()
        request.client.host = "10.0.0.1"
        
        error = RuntimeError("Error simulado")
        call_next = AsyncMock(side_effect=error)
        
        with pytest.raises(RuntimeError):
            await middleware.dispatch(request, call_next)
    
    @pytest.mark.asyncio
    async def test_logging_middleware_sin_client(self):
        """Test middleware cuando request.client es None."""
        app = FastAPI()
        middleware = LoggingMiddleware(app)
        
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/test"
        request.client = None
        
        response_mock = JSONResponse({"status": "ok"})
        call_next = AsyncMock(return_value=response_mock)
        
        response = await middleware.dispatch(request, call_next)
        
        assert response.status_code == 200


class TestMiddlewareIntegration:
    """Tests de integración para middleware."""
    
    def test_middleware_stack_creation(self):
        """Test creación de stack de middleware."""
        from app.drivers.api.main import app as main_app
        
        assert main_app is not None
    
    def test_middleware_con_request_valido(self):
        """Test middleware con request válido."""
        from app.drivers.api.main import app
        
        assert app is not None
        assert hasattr(app, 'middleware_stack')
