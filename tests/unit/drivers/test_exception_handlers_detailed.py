"""Tests detallados para exception handlers con diferentes paths."""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.domain.exceptions import ErrorDominio
from app.domain.enums.error_code import CodigoError
from app.infrastructure.logging_config import request_id_var


@pytest.mark.asyncio
async def test_validation_exception_handler_con_request_id():
    """Test RequestValidationError handler con request_id."""
    from app.drivers.api.main import validation_exception_handler
    
    request_id_var.set("req-test-123")
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/orders"
    request.body = AsyncMock(return_value=b'{"invalid": "data"}')
    
    error_detail = [
        {"loc": ("body", "order_id"), "type": "missing", "msg": "Field required"}
    ]
    exc = RequestValidationError(error_detail)
    
    with patch('app.drivers.api.main.logger') as mock_logger:
        response = await validation_exception_handler(request, exc)
        
        assert response.status_code == 422
        import json
        content = json.loads(response.body.decode())
        assert "request_id" in content
        assert content["request_id"] == "req-test-123"
        assert "X-Request-ID" in response.headers
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_validation_exception_handler_sin_request_id():
    """Test RequestValidationError handler sin request_id."""
    from app.drivers.api.main import validation_exception_handler
    
    request_id_var.set(None)
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/orders"
    request.body = AsyncMock(return_value=b'{}')
    
    error_detail = [
        {"loc": ("body", "order_id"), "type": "missing", "msg": "Field required"}
    ]
    exc = RequestValidationError(error_detail)
    
    response = await validation_exception_handler(request, exc)
    
    assert response.status_code == 422
    import json
    content = json.loads(response.body.decode())
    assert "request_id" not in content or content.get("request_id") is None


@pytest.mark.asyncio
async def test_validation_exception_handler_diferentes_tipos_error():
    """Test RequestValidationError handler con diferentes tipos de error."""
    from app.drivers.api.main import validation_exception_handler
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/orders"
    request.body = AsyncMock(return_value=b'{}')
    
    error_detail = [
        {"loc": ("body", "name"), "type": "string_too_short", "msg": "String too short"},
        {"loc": ("body", "email"), "type": "missing", "msg": "Field required"},
        {"loc": ("body", "age"), "type": "value_error", "msg": "Invalid value"},
        {"loc": ("body", "other"), "type": "unknown_type", "msg": "Other error"}
    ]
    exc = RequestValidationError(error_detail)
    
    response = await validation_exception_handler(request, exc)
    
    assert response.status_code == 422
    import json
    content = json.loads(response.body.decode())
    assert len(content["detail"]) == 4
    assert any("requerido y no puede estar vacío" in msg for msg in content["detail"])
    assert any("es requerido" in msg for msg in content["detail"])


@pytest.mark.asyncio
async def test_validation_exception_handler_body_decode_error():
    """Test RequestValidationError handler cuando body no es JSON válido."""
    from app.drivers.api.main import validation_exception_handler
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/orders"
    request.body = AsyncMock(return_value=b'not json {invalid}')
    
    error_detail = [{"loc": ("body",), "type": "value_error", "msg": "Invalid"}]
    exc = RequestValidationError(error_detail)
    
    response = await validation_exception_handler(request, exc)
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_validation_exception_handler_body_vacio():
    """Test RequestValidationError handler cuando body está vacío."""
    from app.drivers.api.main import validation_exception_handler
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/orders"
    request.body = AsyncMock(return_value=b'')
    
    error_detail = [{"loc": ("body",), "type": "missing", "msg": "Field required"}]
    exc = RequestValidationError(error_detail)
    
    response = await validation_exception_handler(request, exc)
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_error_dominio_handler_sin_contexto():
    """Test ErrorDominio handler sin contexto."""
    from app.drivers.api.main import error_dominio_handler
    
    request_id_var.set("req-456")
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/orders/ORD-001"
    
    exc = ErrorDominio(CodigoError.ORDER_NOT_FOUND, "Orden no encontrada")
    
    with patch('app.drivers.api.main.logger') as mock_logger:
        response = await error_dominio_handler(request, exc)
        
        assert response.status_code == 400
        import json
        content = json.loads(response.body.decode())
        assert content["detail"] == "Orden no encontrada"
        assert content["code"] == "ORDER_NOT_FOUND"
        assert "context" not in content
        assert "X-Request-ID" in response.headers
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_error_dominio_handler_con_contexto():
    """Test ErrorDominio handler con contexto."""
    from app.drivers.api.main import error_dominio_handler
    
    request_id_var.set("req-789")
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/orders/ORD-001"
    
    contexto = {"order_id": "ORD-001", "user": "admin"}
    exc = ErrorDominio(CodigoError.INVALID_OPERATION, "Operación inválida", contexto=contexto)
    
    response = await error_dominio_handler(request, exc)
    
    assert response.status_code == 400
    import json
    content = json.loads(response.body.decode())
    assert "context" in content
    assert content["context"]["order_id"] == "ORD-001"


@pytest.mark.asyncio
async def test_error_dominio_handler_sin_request_id():
    """Test ErrorDominio handler sin request_id."""
    from app.drivers.api.main import error_dominio_handler
    
    request_id_var.set(None)
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/orders/ORD-001"
    
    exc = ErrorDominio(CodigoError.ORDER_NOT_FOUND, "Orden no encontrada")
    
    response = await error_dominio_handler(request, exc)
    
    assert response.status_code == 400
    import json
    content = json.loads(response.body.decode())
    assert "request_id" not in content or content.get("request_id") is None


@pytest.mark.asyncio
async def test_sqlalchemy_error_handler_diferentes_casos():
    """Test SQLAlchemyError handler con diferentes tipos de error."""
    from app.drivers.api.main import sqlalchemy_error_handler
    
    request_id_var.set("req-sql-123")
    
    request = MagicMock()
    request.method = "POST"
    request.url.path = "/orders"
    
    casos = [
        ("does not exist", 503, "Error estructura BD"),
        ("no existe", 503, "Error estructura BD"),
        ("connection", 503, "Error de conexión"),
        ("otro error", 503, "Error en la base de datos")
    ]
    
    for msg, expected_status, expected_detail in casos:
        exc = SQLAlchemyError(msg)
        response = await sqlalchemy_error_handler(request, exc)
        
        assert response.status_code == expected_status
        import json
        content = json.loads(response.body.decode())
        assert expected_detail in content["detail"]


@pytest.mark.asyncio
async def test_value_error_handler_sin_request_id():
    """Test ValueError handler sin request_id."""
    from app.drivers.api.main import value_error_handler
    
    request_id_var.set(None)
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/test"
    
    exc = ValueError("Valor inválido")
    
    response = await value_error_handler(request, exc)
    
    assert response.status_code == 400
    import json
    content = json.loads(response.body.decode())
    assert content["detail"] == "Valor inválido"


@pytest.mark.asyncio
async def test_key_error_handler_con_request_id():
    """Test KeyError handler con request_id."""
    from app.drivers.api.main import key_error_handler
    
    request_id_var.set("req-key-456")
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/test"
    
    exc = KeyError("missing_key")
    
    with patch('app.drivers.api.main.logger') as mock_logger:
        response = await key_error_handler(request, exc)
        
        assert response.status_code == 400
        import json
        content = json.loads(response.body.decode())
        assert "missing_key" in content["detail"]
        assert "X-Request-ID" in response.headers
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_response_validation_error_handler():
    """Test ResponseValidationError handler."""
    from app.drivers.api.main import response_validation_error_handler
    from fastapi.exceptions import ResponseValidationError
    
    request_id_var.set("req-resp-789")
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/orders"
    
    exc = ResponseValidationError([{"loc": ("response",), "msg": "Invalid response"}])
    
    with patch('app.drivers.api.main.logger') as mock_logger:
        response = await response_validation_error_handler(request, exc)
        
        assert response.status_code == 500
        assert "X-Request-ID" in response.headers
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_generic_exception_handler_con_request_id():
    """Test generic exception handler con request_id."""
    from app.drivers.api.main import generic_exception_handler
    
    request_id_var.set("req-gen-999")
    
    request = MagicMock()
    request.method = "GET"
    request.url.path = "/test"
    
    exc = RuntimeError("Error inesperado")
    
    with patch('app.drivers.api.main.logger') as mock_logger:
        response = await generic_exception_handler(request, exc)
        
        assert response.status_code == 500
        import json
        content = json.loads(response.body.decode())
        assert content["detail"] == "Error interno del servidor"
        assert "X-Request-ID" in response.headers
        mock_logger.error.assert_called_once()

