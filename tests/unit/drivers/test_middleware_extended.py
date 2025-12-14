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


class TestBodyCapturingReceiveClass:
    """Tests para la clase BodyCapturingReceive"""
    
    def test_body_capturing_receive_can_instantiate(self):
        """Test que BodyCapturingReceive se puede instanciar"""
        from app.drivers.api.middleware import BodyCapturingReceive
        
        mock_receive = MagicMock()
        receiver = BodyCapturingReceive(mock_receive)
        
        assert receiver is not None
    
    def test_body_capturing_receive_has_get_body_method(self):
        """Test que BodyCapturingReceive tiene método get_body"""
        from app.drivers.api.middleware import BodyCapturingReceive
        
        mock_receive = MagicMock()
        receiver = BodyCapturingReceive(mock_receive)
        
        assert hasattr(receiver, 'get_body')
        assert callable(receiver.get_body)
    
    def test_body_capturing_receive_has_reset_method(self):
        """Test que BodyCapturingReceive tiene método reset"""
        from app.drivers.api.middleware import BodyCapturingReceive
        
        mock_receive = MagicMock()
        receiver = BodyCapturingReceive(mock_receive)
        
        assert hasattr(receiver, 'reset')
        assert callable(receiver.reset)
    
    def test_body_capturing_receive_get_body_returns_bytes(self):
        """Test que get_body retorna bytes"""
        from app.drivers.api.middleware import BodyCapturingReceive
        
        mock_receive = MagicMock()
        receiver = BodyCapturingReceive(mock_receive)
        
        body = receiver.get_body()
        
        assert isinstance(body, bytes)
    
    def test_body_capturing_receive_reset_works(self):
        """Test que reset funciona"""
        from app.drivers.api.middleware import BodyCapturingReceive
        
        mock_receive = MagicMock()
        receiver = BodyCapturingReceive(mock_receive)
        receiver._current_index = 5
        
        receiver.reset()
        
        assert receiver._current_index == 0


class TestResponseCapturingWrapperClass:
    """Tests para la clase ResponseCapturingWrapper"""
    
    def test_response_capturing_wrapper_can_instantiate(self):
        """Test que ResponseCapturingWrapper se puede instanciar"""
        from app.drivers.api.middleware import ResponseCapturingWrapper
        
        mock_response = MagicMock()
        wrapper = ResponseCapturingWrapper(mock_response)
        
        assert wrapper is not None
    
    def test_response_capturing_wrapper_has_get_body_method(self):
        """Test que wrapper tiene método get_body"""
        from app.drivers.api.middleware import ResponseCapturingWrapper
        
        mock_response = MagicMock()
        wrapper = ResponseCapturingWrapper(mock_response)
        
        assert hasattr(wrapper, 'get_body')
        assert callable(wrapper.get_body)
    
    def test_response_capturing_wrapper_stores_response(self):
        """Test que wrapper almacena respuesta"""
        from app.drivers.api.middleware import ResponseCapturingWrapper
        
        mock_response = MagicMock()
        wrapper = ResponseCapturingWrapper(mock_response)
        
        assert hasattr(wrapper, 'response')


class TestLoggingMiddlewareMethods:
    """Tests para métodos de LoggingMiddleware"""
    
    def test_obtener_info_request_exists(self):
        """Test que método _obtener_info_request existe"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert hasattr(middleware, '_obtener_info_request')
        assert callable(middleware._obtener_info_request)
    
    def test_obtener_body_request_exists(self):
        """Test que método _obtener_body_request existe"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert hasattr(middleware, '_obtener_body_request')
        assert callable(middleware._obtener_body_request)
    
    def test_extraer_body_json_exists(self):
        """Test que método _extraer_body_json existe"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert hasattr(middleware, '_extraer_body_json')
        assert callable(middleware._extraer_body_json)
    
    def test_obtener_body_response_exists(self):
        """Test que método _obtener_body_response existe"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert hasattr(middleware, '_obtener_body_response')
        assert callable(middleware._obtener_body_response)
    
    def test_obtener_info_request_returns_dict(self):
        """Test que _obtener_info_request retorna diccionario"""
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
        
        assert isinstance(info, dict)
        assert "metodo" in info
        assert "path" in info
    
    def test_obtener_body_request_returns_dict(self):
        """Test que _obtener_body_request retorna diccionario"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        body = middleware._obtener_body_request("/health", "GET")
        
        assert isinstance(body, dict)
    
    def test_extraer_body_json_returns_dict(self):
        """Test que _extraer_body_json retorna diccionario"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        mock_response = MagicMock()
        result = middleware._extraer_body_json(mock_response)
        
        assert isinstance(result, dict)
    
    def test_obtener_body_response_returns_dict(self):
        """Test que _obtener_body_response retorna diccionario"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        mock_response = MagicMock()
        result = middleware._obtener_body_response("/health", mock_response)
        
        assert isinstance(result, dict)


class TestLoggingMiddlewareIntegration:
    """Tests de integración para LoggingMiddleware"""
    
    def test_middleware_with_app(self):
        """Test que middleware funciona con app"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert middleware.app == mock_app
    
    def test_middleware_with_different_paths(self):
        """Test que middleware funciona con diferentes paths"""
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        paths = ["/health", "/ordenes", "/clientes", "/comandos"]
        
        for path in paths:
            body = middleware._obtener_body_request(path, "GET")
            assert isinstance(body, dict)
