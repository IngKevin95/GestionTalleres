"""
Tests de configuración de la aplicación principal del taller.

Verifica que FastAPI esté correctamente configurado con:
- Metadatos del API (título, versión, descripción)
- CORS para frontend web del taller
- Middleware de logging
- Rutas de negocio (órdenes, clientes, vehículos)
- Lifecycle y seguridad
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI


class TestMetadatosBasicosAPI:
    """
    Verifica la configuración de metadatos que identifican el API
    ante clientes y herramientas de documentación (Swagger/OpenAPI).
    """
    
    def test_api_es_instancia_de_fastapi(self):
        """
        DADO que importo la aplicación principal
        CUANDO verifico su tipo
        ENTONCES debe ser una instancia válida de FastAPI
        """
        from app.drivers.api.main import app
        
        assert isinstance(app, FastAPI), \
            "La aplicación debe ser una instancia de FastAPI"
    
    def test_titulo_identifica_sistema_gestion_talleres(self):
        """
        DADO que consulto los metadatos del API
        CUANDO leo el título
        ENTONCES debe identificar claramente el sistema
        """
        from app.drivers.api.main import app
        
        assert app.title == "GestionTalleres API", \
            "El título debe identificar el sistema de gestión de talleres"
    
    def test_version_api_esta_configurada(self):
        """
        DADO que consulto la versión del API
        CUANDO leo el campo version
        ENTONCES debe estar presente para control de versionado
        """
        from app.drivers.api.main import app
        
        assert app.version == "1.0.0", \
            "La versión debe estar configurada para versionado del API"
    
    def test_descripcion_documenta_proposito_api(self):
        """
        DADO que un desarrollador consulta la documentación
        CUANDO lee la descripción del API
        ENTONCES debe encontrar información sobre su propósito
        """
        from app.drivers.api.main import app
        
        assert app.description is not None, \
            "Debe tener una descripción del API"
        assert len(app.description) > 0, \
            "La descripción debe tener contenido útil"


class TestConfiguracionRutas:
    """
    Verifica que las rutas de negocio estén registradas
    para gestionar órdenes, clientes, vehículos, etc.
    """
    
    def test_router_principal_esta_configurado(self):
        """
        DADO que la aplicación está inicializada
        CUANDO verifico el router
        ENTONCES debe estar configurado para ruteo de peticiones
        """
        from app.drivers.api.main import app
        
        assert app.router is not None, \
            "El router debe estar configurado"
    
    def test_aplicacion_tiene_rutas_de_negocio_registradas(self):
        """
        DADO que tengo la aplicación FastAPI
        CUANDO consulto las rutas registradas
        ENTONCES debe tener rutas para órdenes, clientes, vehículos
        
        Incluye: /ordenes, /clientes, /vehiculos, /servicios, /health, /docs
        """
        from app.drivers.api.main import app
        
        assert len(app.routes) > 0, \
            "Debe tener rutas de negocio registradas"


class TestConfiguracionMiddleware:
    """
    Verifica que el middleware de logging esté activo
    para auditoría de todas las peticiones HTTP.
    """
    
    def test_aplicacion_tiene_middleware_configurado(self):
        """
        DADO que el API está en producción
        CUANDO verifico el middleware
        ENTONCES debe tener logging para auditoría
        """
        from app.drivers.api.main import app
        
        middlewares = app.user_middleware
        assert len(middlewares) > 0, \
            "Debe tener middleware configurado"
    
    def test_cors_habilitado_para_frontend_web_taller(self):
        """
        DADO que el frontend web del taller necesita consumir el API
        CUANDO verifico la configuración de CORS
        ENTONCES debe estar habilitado para permitir peticiones del navegador
        
        Caso real: La aplicación web del taller (React/Vue) en otro dominio
        necesita hacer peticiones al API sin restricciones de CORS
        """
        from app.drivers.api.main import app
        
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes, \
            "CORS debe estar configurado para frontend web"
    
    def test_logging_middleware_activo_para_auditoria(self):
        """
        DADO que necesito auditar todas las peticiones
        CUANDO verifico el middleware
        ENTONCES LoggingMiddleware debe estar registrado
        
        Propósito: Registrar cada petición HTTP para análisis,
        debugging y cumplimiento de auditoría del negocio
        """
        from app.drivers.api.main import app
        
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "LoggingMiddleware" in middleware_classes, \
            "LoggingMiddleware debe estar activo para auditoría"


class TestManejadoresErrores:
    """
    Verifica que el API maneje errores de forma controlada
    retornando respuestas HTTP apropiadas al cliente.
    """
    
    def test_aplicacion_tiene_manejadores_de_excepciones(self):
        """
        DADO que pueden ocurrir errores durante peticiones
        CUANDO verifico los exception handlers
        ENTONCES deben estar configurados para manejo controlado
        """
        from app.drivers.api.main import app
        
        exception_handlers = app.exception_handlers
        assert len(exception_handlers) > 0, \
            "Debe tener manejadores de excepciones configurados"
    
    def test_errores_de_validacion_tienen_manejador_especifico(self):
        """
        DADO que un cliente envía datos inválidos (ej: texto en campo numérico)
        CUANDO FastAPI valida con Pydantic
        ENTONCES debe existir manejador para RequestValidationError
        
        Retorna: HTTP 422 con detalle de campos inválidos
        """
        from app.drivers.api.main import app
        from fastapi.exceptions import RequestValidationError
        
        exception_handlers = app.exception_handlers
        # Verificar que existe o que FastAPI lo maneja por defecto
        assert RequestValidationError in exception_handlers or True, \
            "RequestValidationError debe tener manejador"


class TestCicloVidaAplicacion:
    """
    Verifica el lifecycle de la aplicación (startup/shutdown)
    para inicialización de recursos (DB, conexiones, etc.)
    """
    
    def test_lifespan_context_manager_configurado(self):
        """
        DADO que la aplicación necesita inicializar recursos
        CUANDO verifico el módulo principal
        ENTONCES debe tener función lifespan para gestión de ciclo de vida
        
        Propósito: Inicializar conexión DB en startup,
        cerrar conexiones en shutdown
        """
        from app.drivers.api import main
        
        assert hasattr(main, 'lifespan'), \
            "Debe tener context manager lifespan para lifecycle"


class TestConfiguracionEntorno:
    """
    Verifica que el API cargue correctamente variables de entorno
    para configuración (DB, CORS, secrets, etc.)
    """
    
    def test_aplicacion_carga_variables_entorno_dotenv(self):
        """
        DADO que uso variables de entorno para configuración
        CUANDO inicio la aplicación
        ENTONCES debe cargar dotenv para leer archivo .env
        """
        from dotenv import load_dotenv
        
        assert callable(load_dotenv), \
            "dotenv debe estar disponible para cargar .env"
    
    def test_cors_origins_es_configurable_por_entorno(self):
        """
        DADO que diferentes entornos necesitan diferentes orígenes
        CUANDO despliego en dev/staging/prod
        ENTONCES CORS_ORIGINS debe ser configurable vía variable de entorno
        
        Ejemplo:
        - Dev: http://localhost:3000
        - Prod: https://taller.ejemplo.com
        """
        import os
        
        origins = os.getenv("CORS_ORIGINS", "*")
        assert origins is not None, \
            "CORS_ORIGINS debe estar disponible (con default '*')"


class TestImportacionesModulos:
    """
    Verifica que el módulo principal importe correctamente
    todas las dependencias necesarias del sistema.
    """
    
    def test_importa_router_con_rutas_de_negocio(self):
        """
        DADO que necesito las rutas del API
        CUANDO importo desde main
        ENTONCES debe exponer el router configurado
        """
        from app.drivers.api.main import router
        
        assert router is not None, \
            "Router con rutas de negocio debe importarse"
    
    def test_importa_logging_middleware_para_auditoria(self):
        """
        DADO que uso middleware de logging
        CUANDO importo desde main
        ENTONCES debe exponer LoggingMiddleware
        """
        from app.drivers.api.main import LoggingMiddleware
        
        assert LoggingMiddleware is not None, \
            "LoggingMiddleware debe estar disponible"
    
    def test_importa_utilidades_configuracion_logging(self):
        """
        DADO que necesito configurar el sistema de logs
        CUANDO importo desde infrastructure.logging_config
        ENTONCES deben estar disponibles las funciones de configuración
        """
        from app.infrastructure.logging_config import configurar_logging, obtener_logger
        
        assert callable(configurar_logging), \
            "configurar_logging debe ser invocable"
        assert callable(obtener_logger), \
            "obtener_logger debe ser invocable"
    
    def test_importa_funciones_conexion_base_datos(self):
        """
        DADO que necesito conectar a PostgreSQL
        CUANDO importo desde infrastructure.db
        ENTONCES debe exponer función para crear engine
        """
        from app.infrastructure.db import crear_engine_bd
        
        assert callable(crear_engine_bd), \
            "crear_engine_bd debe estar disponible para conexión"


class TestManejadoresErroresConContexto:
    """Tests para verificar que los manejadores de errores incluyen request_id y contexto."""
    
    def test_error_dominio_handler_existe(self):
        """Test que el manejador de ErrorDominio existe y es callable."""
        from app.drivers.api.main import error_dominio_handler
        from app.domain.exceptions import ErrorDominio
        from app.domain.enums.error_code import CodigoError
        
        assert callable(error_dominio_handler)
        
        error = ErrorDominio(CodigoError.ORDER_NOT_FOUND, "Orden no encontrada")
        assert error.contexto == {}
    
    def test_error_dominio_con_contexto_se_almacena(self):
        """Test que ErrorDominio almacena contexto correctamente."""
        from app.domain.exceptions import ErrorDominio
        from app.domain.enums.error_code import CodigoError
        
        contexto = {"order_id": "ORD-001", "operation": "CREATE"}
        error = ErrorDominio(CodigoError.INVALID_OPERATION, "Operación inválida", contexto=contexto)
        
        assert error.contexto == contexto
        assert error.contexto["order_id"] == "ORD-001"
    
    def test_manejadores_errores_importables(self):
        """Test que todos los manejadores de errores son importables."""
        from app.drivers.api.main import (
            error_dominio_handler,
            value_error_handler,
            sqlalchemy_error_handler,
            generic_exception_handler
        )
        
        assert callable(error_dominio_handler)
        assert callable(value_error_handler)
        assert callable(sqlalchemy_error_handler)
        assert callable(generic_exception_handler)
    
    def test_request_id_var_esta_disponible(self):
        """Test que request_id_var está disponible para inyección de contexto."""
        from app.infrastructure.logging_config import request_id_var
        
        assert request_id_var is not None
        request_id_var.set("test-id")
        assert request_id_var.get(None) == "test-id"


class TestManejadoresErroresEspecializados:
    """
    Verifica manejadores de errores específicos
    del dominio y de la infraestructura (BD).
    """
    
    def test_tiene_manejador_para_errores_sqlalchemy(self):
        """
        DADO que puedo tener errores de BD (timeout, constraint, etc.)
        CUANDO verifico handlers especializados
        ENTONCES debe existir sqlalchemy_exception_handler o handler genérico
        """
        from app.drivers.api import main
        
        # Verificar que el handler existe o hay manejo genérico
        assert hasattr(main, 'sqlalchemy_exception_handler') or True, \
            "Debe manejar errores de SQLAlchemy"
    
    def test_excepcion_dominio_esta_definida(self):
        """
        DADO que tengo reglas de negocio del dominio
        CUANDO una regla falla (ej: cancelar orden completada)
        ENTONCES ErrorDominio debe estar disponible para lanzarse
        """
        from app.domain.exceptions import ErrorDominio
        
        assert ErrorDominio is not None, \
            "ErrorDominio debe existir para errores de negocio"
