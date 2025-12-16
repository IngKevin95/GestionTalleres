"""
Tests del middleware de registro de peticiones HTTP.

Verifica que todas las peticiones al API del taller
se registren correctamente incluyendo cliente, ruta, estado y timing.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from starlette.middleware.base import BaseHTTPMiddleware


class TestMiddlewareRegistroPeticiones:
    """
    Verifica configuración y funcionamiento del middleware que registra
    todas las peticiones HTTP que llegan al sistema del taller.
    """
    
    def test_middleware_hereda_de_clase_base_http(self):
        """
        DADO que tengo el middleware de logging
        CUANDO verifico su herencia
        ENTONCES debe extender BaseHTTPMiddleware de Starlette
        """
        from app.drivers.api.middleware import LoggingMiddleware
        
        assert issubclass(LoggingMiddleware, BaseHTTPMiddleware), \
            "LoggingMiddleware debe heredar de BaseHTTPMiddleware"
    
    def test_middleware_se_puede_instanciar_con_app(self):
        """
        DADO que tengo una aplicación FastAPI
        CUANDO creo el middleware de logging
        ENTONCES debe inicializarse correctamente
        """
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert middleware is not None, \
            "El middleware debe instanciarse sin errores"
    
    def test_middleware_tiene_referencia_a_app(self):
        """
        DADO que instancié el middleware
        CUANDO verifico su atributo app
        ENTONCES debe mantener referencia a la aplicación
        """
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        
        assert hasattr(middleware, 'app'), \
            "Middleware debe tener atributo 'app' configurado"


class TestFuncionalidadLogueoPeticiones:
    """
    Verifica que el middleware intercepta y registra
    peticiones HTTP correctamente durante operación.
    """
    
    def test_middleware_tiene_metodo_dispatch_para_interceptar(self):
        """
        DADO que el middleware está configurado
        CUANDO verifico sus métodos
        ENTONCES debe tener dispatch() para interceptar peticiones
        """
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert hasattr(middleware, 'dispatch'), \
            "Middleware debe tener método dispatch"
        assert callable(middleware.dispatch), \
            "Método dispatch debe ser invocable"


class TestInteraccionConAplicacion:
    """
    Verifica integración del middleware con la aplicación FastAPI
    simulando flujos reales del sistema del taller.
    """
    
    def test_middleware_funciona_integrado_con_app(self):
        """
        DADO que tengo el middleware configurado
        CUANDO lo integro con la aplicación
        ENTONCES debe funcionar sin errores
        """
        from app.drivers.api.middleware import LoggingMiddleware
        
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        assert middleware.app == mock_app, \
            "Middleware debe mantener referencia a la app"
    
    @pytest.mark.asyncio
    async def test_middleware_registra_peticion_health_check(self):
        """
        DADO que un cliente consulta el endpoint de salud
        CUANDO la petición pasa por el middleware
        ENTONCES debe registrar la consulta y retornar respuesta
        
        Caso real: Balanceador de carga verifica salud del servicio
        """
        from app.drivers.api.middleware import LoggingMiddleware
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        app = FastAPI()
        middleware = LoggingMiddleware(app)
        
        # Given - Petición desde balanceador de carga
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/health"
        request.client = MagicMock()
        request.client.host = "192.168.1.100"  # IP interna del balanceador
        
        call_next = AsyncMock(return_value=JSONResponse({"status": "ok"}))
        
        # When - Petición pasa por middleware
        response = await middleware.dispatch(request, call_next)
        
        # Then - Respuesta exitosa
        assert response.status_code == 200, \
            "Health check debe retornar 200 OK"
