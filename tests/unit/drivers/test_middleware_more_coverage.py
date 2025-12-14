import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from starlette.middleware.base import BaseHTTPMiddleware


class TestMiddlewareClasses:
    """Tests para las clases de middleware"""
    
    def test_body_capturing_receive_init(self):
        """Test inicialización de BodyCapturingReceive"""
        from app.drivers.api.middleware import BodyCapturingReceive
        
        mock_receive = MagicMock()
        receiver = BodyCapturingReceive(mock_receive)
        
        assert receiver._body == b""
        assert receiver._messages == []
        assert receiver._all_consumed == False
        assert receiver._current_index == 0
    
    def test_body_capturing_receive_get_body(self):
        """Test get_body de BodyCapturingReceive"""
        from app.drivers.api.middleware import BodyCapturingReceive
        
        mock_receive = MagicMock()
        receiver = BodyCapturingReceive(mock_receive)
        
        body = receiver.get_body()
        assert body == b""
    
    def test_body_capturing_receive_reset(self):
        """Test reset de BodyCapturingReceive"""
        from app.drivers.api.middleware import BodyCapturingReceive
        
        mock_receive = MagicMock()
        receiver = BodyCapturingReceive(mock_receive)
        receiver._current_index = 5
        
        receiver.reset()
        assert receiver._current_index == 0
    
    def test_response_capturing_wrapper_init(self):
        """Test inicialización de ResponseCapturingWrapper"""
        from app.drivers.api.middleware import ResponseCapturingWrapper
        
        mock_response = MagicMock()
        wrapper = ResponseCapturingWrapper(mock_response)
        
        assert wrapper.response == mock_response
        assert wrapper._body is None
    
    def test_response_capturing_wrapper_get_body(self):
        """Test get_body de ResponseCapturingWrapper"""
        from app.drivers.api.middleware import ResponseCapturingWrapper
        
        mock_response = MagicMock()
        wrapper = ResponseCapturingWrapper(mock_response)
        
        body = wrapper.get_body()
        assert body is None


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
    
    def test_obtener_info_request_method(self):
        """Test método _obtener_info_request"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url.path = "/health"
        mock_request.query_params = {}
        mock_request.client = MagicMock()
        mock_request.client.host = "127.0.0.1"
        
        info = middleware._obtener_info_request(mock_request)
        
        assert info["metodo"] == "GET"
        assert info["path"] == "/health"
        assert info["client_ip"] == "127.0.0.1"
    
    def test_obtener_info_request_sin_cliente(self):
        """Test _obtener_info_request sin cliente"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/ordenes"
        mock_request.query_params = {}
        mock_request.client = None
        
        info = middleware._obtener_info_request(mock_request)
        
        assert info["client_ip"] == "unknown"
    
    def test_obtener_body_request_commands_endpoint(self):
        """Test _obtener_body_request para /commands"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        body = middleware._obtener_body_request("/commands", "POST")
        
        assert isinstance(body, dict)
    
    def test_obtener_body_request_otros_endpoints(self):
        """Test _obtener_body_request para otros endpoints"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        body = middleware._obtener_body_request("/ordenes", "GET")
        
        assert body == {}
    
    def test_extraer_body_json_empty(self):
        """Test _extraer_body_json con response vacío"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        mock_response = MagicMock()
        result = middleware._extraer_body_json(mock_response)
        
        assert result == {}
    
    def test_extraer_body_json_with_json_response(self):
        """Test _extraer_body_json con JSONResponse"""
        from app.drivers.api.middleware import LoggingMiddleware
        from fastapi.responses import JSONResponse
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        response = JSONResponse(content={"status": "ok"})
        result = middleware._extraer_body_json(response)
        
        # El resultado debe ser un diccionario
        assert isinstance(result, dict)
    
    def test_obtener_body_response_commands(self):
        """Test _obtener_body_response para /commands"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        mock_response = MagicMock()
        result = middleware._obtener_body_response("/commands", mock_response)
        
        assert isinstance(result, dict)
    
    def test_obtener_body_response_otros(self):
        """Test _obtener_body_response para otros paths"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        mock_response = MagicMock()
        result = middleware._obtener_body_response("/salud", mock_response)
        
        assert result == {}


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
    
    def test_body_capturing_receive_call(self):
        """Test llamada de BodyCapturingReceive"""
        from app.drivers.api.middleware import BodyCapturingReceive
        
        async def test_func():
            mock_receive = AsyncMock()
            mock_receive.return_value = {
                "type": "http.request",
                "body": b"test",
                "more_body": False
            }
            
            receiver = BodyCapturingReceive(mock_receive)
            result = await receiver()
            
            assert result["type"] == "http.request"
            assert receiver.get_body() == b"test"
        
        import asyncio
        asyncio.run(test_func())
    
    def test_middleware_request_info_fields(self):
        """Test que info del request tiene todos los campos"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.method = "DELETE"
        mock_request.url.path = "/ordenes/123"
        mock_request.query_params = {"force": "true"}
        mock_request.client = MagicMock()
        mock_request.client.host = "192.168.1.1"
        
        info = middleware._obtener_info_request(mock_request)
        
        assert "metodo" in info
        assert "path" in info
        assert "query_params" in info
        assert "client_ip" in info
        assert info["metodo"] == "DELETE"
