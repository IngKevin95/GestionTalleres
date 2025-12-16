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


@pytest.mark.asyncio
async def test_logging_middleware_genera_request_id():
    """Test que el middleware genera un request_id único."""
    from app.infrastructure.logging_config import request_id_var
    
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/test"
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.headers = {}
    
    response_mock = JSONResponse({"status": "ok"})
    call_next = AsyncMock(return_value=response_mock)
    
    response = await middleware.dispatch(request, call_next)
    
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) == 8
    req_id = request_id_var.get(None)
    assert req_id is not None
    assert req_id == response.headers["X-Request-ID"]


@pytest.mark.asyncio
async def test_logging_middleware_usa_request_id_header_existente():
    """Test que el middleware usa X-Request-ID del header si existe."""
    from app.infrastructure.logging_config import request_id_var
    
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/test"
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.headers = {"X-Request-ID": "custom-id-123"}
    
    response_mock = JSONResponse({"status": "ok"})
    call_next = AsyncMock(return_value=response_mock)
    
    response = await middleware.dispatch(request, call_next)
    
    assert response.headers["X-Request-ID"] == "custom-id-123"
    req_id = request_id_var.get(None)
    assert req_id == "custom-id-123"


@pytest.mark.asyncio
async def test_logging_middleware_request_id_en_logs():
    """Test que el request_id se incluye en los logs."""
    from app.infrastructure.logging_config import request_id_var
    from unittest.mock import patch
    
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/orders"
    request.client = MagicMock()
    request.client.host = "192.168.1.1"
    request.headers = {}
    
    response_mock = JSONResponse({"status": "created"}, status_code=201)
    call_next = AsyncMock(return_value=response_mock)
    
    with patch('app.drivers.api.middleware.logger') as mock_logger:
        await middleware.dispatch(request, call_next)
        
        assert mock_logger.info.call_count >= 2
        call_args = mock_logger.info.call_args_list
        for call in call_args:
            extra = call.kwargs.get('extra', {})
            assert 'request_id' in extra
            assert len(extra['request_id']) == 8


@pytest.mark.asyncio
async def test_logging_middleware_request_id_en_error():
    """Test que el request_id se incluye en logs de error."""
    from app.infrastructure.logging_config import request_id_var
    from unittest.mock import patch
    
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/test"
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.headers = {}
    
    call_next = AsyncMock(side_effect=RuntimeError("Error de prueba"))
    
    with patch('app.drivers.api.middleware.logger_errores') as mock_logger:
        with pytest.raises(RuntimeError):
            await middleware.dispatch(request, call_next)
        
        mock_logger.error.assert_called_once()
        call_kwargs = mock_logger.error.call_args.kwargs
        extra = call_kwargs.get('extra', {})
        assert 'request_id' in extra
        assert len(extra['request_id']) == 8


@pytest.mark.asyncio
async def test_logging_middleware_request_id_se_propaga():
    """Test que el request_id se propaga correctamente en el contexto."""
    from app.infrastructure.logging_config import request_id_var
    
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/orders"
    request.client = MagicMock()
    request.client.host = "192.168.1.1"
    request.headers = {}
    
    response_mock = JSONResponse({"status": "created"}, status_code=201)
    call_next = AsyncMock(return_value=response_mock)
    
    await middleware.dispatch(request, call_next)
    
    req_id = request_id_var.get(None)
    assert req_id is not None
    assert len(req_id) == 8


@pytest.mark.asyncio
async def test_logging_middleware_diferentes_metodos():
    """Test middleware con diferentes métodos HTTP."""
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    metodos = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    
    for metodo in metodos:
        request = MagicMock()
        request.method = metodo
        request.url.path = "/test"
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        
        response_mock = JSONResponse({"status": "ok"})
        call_next = AsyncMock(return_value=response_mock)
        
        response = await middleware.dispatch(request, call_next)
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_logging_middleware_diferentes_status_codes():
    """Test middleware con diferentes códigos de estado."""
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    
    status_codes = [200, 201, 400, 404, 500]
    
    for status in status_codes:
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/test"
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        
        response_mock = JSONResponse({"status": "ok"}, status_code=status)
        call_next = AsyncMock(return_value=response_mock)
        
        response = await middleware.dispatch(request, call_next)
        
        assert response.status_code == status
        assert "X-Request-ID" in response.headers

