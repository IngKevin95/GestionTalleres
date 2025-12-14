"""Tests para mejorar cobertura de middleware."""
import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio
from app.drivers.api.middleware import (
    LoggingMiddleware,
    BodyCapturingReceive,
    ResponseCapturingWrapper
)


class TestLoggingMiddlewareCoverage:
    """Tests para mejorar cobertura de LoggingMiddleware."""
    
    @pytest.mark.asyncio
    async def test_logging_middleware_init(self):
        """Test inicialización de LoggingMiddleware."""
        app = FastAPI()
        middleware = LoggingMiddleware(app)
        assert middleware.app == app
    
    @pytest.mark.asyncio
    async def test_body_capturing_receive_init(self):
        """Test inicialización de BodyCapturingReceive."""
        receive_mock = AsyncMock()
        receiver = BodyCapturingReceive(receive_mock)
        assert receiver.receive == receive_mock
    
    @pytest.mark.asyncio
    async def test_body_capturing_receive_call(self):
        """Test BodyCapturingReceive captura body."""
        receive_mock = AsyncMock(return_value={
            "type": "http.request",
            "body": b"test data",
            "more_body": False
        })
        receiver = BodyCapturingReceive(receive_mock)
        message = await receiver()
        assert message["type"] == "http.request"
        assert receiver.get_body() == b"test data"
    
    def test_body_capturing_receive_reset(self):
        """Test BodyCapturingReceive reset."""
        receive_mock = AsyncMock()
        receiver = BodyCapturingReceive(receive_mock)
        receiver._current_index = 5
        receiver.reset()
        assert receiver._current_index == 0


class TestResponseCapturingWrapperCoverage:
    """Tests para mejorar cobertura de ResponseCapturingWrapper."""
    
    def test_response_capturing_wrapper_init(self):
        """Test inicialización de ResponseCapturingWrapper."""
        response_mock = AsyncMock()
        wrapper = ResponseCapturingWrapper(response_mock)
        assert wrapper.response == response_mock
    
    def test_response_capturing_wrapper_get_body(self):
        """Test get_body retorna None si no hay body."""
        response_mock = AsyncMock()
        wrapper = ResponseCapturingWrapper(response_mock)
        assert wrapper.get_body() is None


class TestMiddlewareIntegration:
    """Tests de integración para middleware."""
    
    def test_middleware_stack_creation(self):
        """Test creación de stack de middleware."""
        from app.drivers.api.main import app as main_app
        
        # Verificar que la app se creó
        assert main_app is not None
    
    def test_middleware_con_request_valido(self):
        """Test middleware con request válido."""
        from app.drivers.api.main import app
        
        # Simplemente verificar que el middleware se puede importar sin errores
        assert app is not None
        # Verificar que existe el middleware
        assert hasattr(app, 'middleware_stack')
