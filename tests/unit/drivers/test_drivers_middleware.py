from unittest.mock import Mock, AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pytest
from app.drivers.api.middleware import LoggingMiddleware


def test_logging_middleware_init():
    app_mock = Mock()
    middleware = LoggingMiddleware(app_mock)
    
    assert middleware.app == app_mock


@pytest.mark.asyncio
async def test_logging_middleware_dispatch_exitoso():
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/test"
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    
    response_mock = JSONResponse({"status": "ok"})
    call_next = AsyncMock(return_value=response_mock)
    
    response = await middleware.dispatch(request, call_next)
    
    assert response.status_code == 200
    call_next.assert_called_once_with(request)


@pytest.mark.asyncio
async def test_logging_middleware_dispatch_con_error():
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/test"
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    
    call_next = AsyncMock(side_effect=ValueError("Error de prueba"))
    
    with pytest.raises(ValueError):
        await middleware.dispatch(request, call_next)


@pytest.mark.asyncio
async def test_logging_middleware_sin_client():
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

