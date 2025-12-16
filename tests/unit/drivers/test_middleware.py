"""Tests para middleware de la API."""
import pytest


import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


def test_middleware_hereda_base():
    from app.drivers.api.middleware import LoggingMiddleware
    assert issubclass(LoggingMiddleware, BaseHTTPMiddleware)


@pytest.mark.asyncio
async def test_middleware_dispatch():
    from app.drivers.api.middleware import LoggingMiddleware
    
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
async def test_middleware_sin_cliente():
    from app.drivers.api.middleware import LoggingMiddleware
    
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/test"
    request.client = None
    
    call_next = AsyncMock(return_value=JSONResponse({"status": "ok"}))
    
    response = await middleware.dispatch(request, call_next)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_middleware_con_excepcion():
    from app.drivers.api.middleware import LoggingMiddleware
    
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/error"
    request.client = MagicMock()
    request.client.host = "10.0.0.1"
    
    error = RuntimeError("Error simulado")
    call_next = AsyncMock(side_effect=error)
    
    with pytest.raises(RuntimeError):
        await middleware.dispatch(request, call_next)
