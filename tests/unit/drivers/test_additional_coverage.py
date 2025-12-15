"""Tests adicionales para mejorar cobertura."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal


class TestHealthResponseSchema:
    """Tests para HealthResponse schema."""
    
    def test_health_response_creation(self):
        """Test crear HealthResponse."""
        from app.drivers.api.schemas import HealthResponse
        
        response = HealthResponse(
            status="ok",
            api="operativa",
            database="conectada",
            tablas=["ordenes"],
            tablas_faltantes=[],
            mensaje=None
        )
        assert response.status == "ok"
        assert response.api == "operativa"
    
    def test_health_response_model_dump(self):
        """Test model_dump de HealthResponse."""
        from app.drivers.api.schemas import HealthResponse
        
        response = HealthResponse(
            status="ok",
            api="operativa",
            database="conectada",
            tablas=["ordenes"],
            tablas_faltantes=[],
            mensaje=None
        )
        dumped = response.model_dump()
        assert dumped["status"] == "ok"
        assert "api" in dumped


class TestCommandsRequestSchema:
    """Tests para CommandsRequest schema."""
    
    def test_commands_request_valid(self):
        """Test CommandsRequest con datos válidos."""
        from app.drivers.api.schemas import CommandsRequest
        
        request = CommandsRequest(
            commands=[{"command": "CREATE_ORDER", "customer": "Juan"}]
        )
        assert len(request.commands) == 1
    
    def test_commands_request_empty_fails(self):
        """Test CommandsRequest falla con lista vacía."""
        from app.drivers.api.schemas import CommandsRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            CommandsRequest(commands=[])
    
    def test_commands_request_model_dump(self):
        """Test model_dump de CommandsRequest."""
        from app.drivers.api.schemas import CommandsRequest
        
        request = CommandsRequest(
            commands=[{"command": "TEST"}]
        )
        dumped = request.model_dump()
        assert "commands" in dumped


class TestCommandsResponseSchema:
    """Tests para CommandsResponse schema."""
    
    def test_commands_response_creation(self):
        """Test crear CommandsResponse."""
        from app.drivers.api.schemas import CommandsResponse
        
        response = CommandsResponse(
            orders=[],
            events=[]
        )
        assert response.orders == []
        assert response.events == []


class TestSetStateRequestSchema:
    """Tests para SetStateRequest schema."""
    
    def test_set_state_request_valid(self):
        """Test SetStateRequest con datos válidos."""
        from app.drivers.api.schemas import SetStateRequest
        
        request = SetStateRequest(state="diagnosticado")
        assert request.state == "diagnosticado"


class TestMainApp:
    """Tests para app principal."""
    
    def test_app_instance_exists(self):
        """Test que app FastAPI existe."""
        from app.drivers.api.main import app
        from fastapi import FastAPI
        
        assert isinstance(app, FastAPI)
    
    def test_app_has_routes(self):
        """Test que app tiene rutas."""
        from app.drivers.api.main import app
        
        routes = [route for route in app.routes]
        assert len(routes) > 0
    
    def test_app_router_exists(self):
        """Test que app tiene router."""
        from app.drivers.api.main import app
        
        assert app.router is not None


class TestLoggingMiddleware:
    """Tests para middleware de logging."""
    
    def test_logging_middleware_import(self):
        """Test importar LoggingMiddleware."""
        from app.drivers.api.middleware import LoggingMiddleware
        
        assert LoggingMiddleware is not None
    
    def test_logging_middleware_base_http(self):
        """Test que LoggingMiddleware es middleware válido."""
        from app.drivers.api.middleware import LoggingMiddleware
        from starlette.middleware.base import BaseHTTPMiddleware
        
        assert issubclass(LoggingMiddleware, BaseHTTPMiddleware)


class TestDependencies:
    """Tests para dependencias inyectables."""
    
    def test_obtener_action_service_callable(self):
        """Test que obtener_action_service es callable."""
        from app.drivers.api.dependencies import obtener_action_service
        
        assert callable(obtener_action_service)
    
    def test_obtener_sesion_callable(self):
        """Test que obtener_sesion es callable."""
        from app.drivers.api.dependencies import obtener_sesion
        
        assert callable(obtener_sesion)


class TestInfrastructureDatabase:
    """Tests para infraestructura de BD."""
    
    def test_obtener_url_bd_default(self):
        """Test obtener_url_bd con valores default."""
        from app.infrastructure.db import obtener_url_bd
        from unittest.mock import patch
        
        with patch.dict('os.environ', {}, clear=True):
            url = obtener_url_bd()
            assert "postgresql" in url
    
    def test_crear_engine_bd_callable(self):
        """Test que crear_engine_bd es callable."""
        from app.infrastructure.db import crear_engine_bd
        
        assert callable(crear_engine_bd)


class TestLoggingConfiguration:
    """Tests para configuración de logging."""
    
    def test_configurar_logging_callable(self):
        """Test que configurar_logging es callable."""
        from app.infrastructure.logging_config import configurar_logging
        
        assert callable(configurar_logging)
    
    def test_obtener_logger_callable(self):
        """Test que obtener_logger es callable."""
        from app.infrastructure.logging_config import obtener_logger
        
        assert callable(obtener_logger)
    
    def test_obtener_logger_returns_logger(self):
        """Test que obtener_logger retorna logger válido."""
        from app.infrastructure.logging_config import obtener_logger
        import logging
        
        logger = obtener_logger("test")
        assert isinstance(logger, logging.Logger)


class TestInfrastructureModels:
    """Tests para modelos de infraestructura."""
    
    def test_base_model_import(self):
        """Test importar Base model."""
        from app.infrastructure.models.base import Base
        
        assert Base is not None
    
    def test_orden_model_import(self):
        """Test importar OrdenModel."""
        from app.infrastructure.models.orden_model import OrdenModel
        
        assert OrdenModel is not None
    
    def test_cliente_model_import(self):
        """Test importar ClienteModel."""
        from app.infrastructure.models.cliente_model import ClienteModel
        
        assert ClienteModel is not None
    
    def test_vehiculo_model_import(self):
        """Test importar VehiculoModel."""
        from app.infrastructure.models.vehiculo_model import VehiculoModel
        
        assert VehiculoModel is not None
    
    def test_servicio_model_import(self):
        """Test importar ServicioModel."""
        from app.infrastructure.models.servicio_model import ServicioModel
        
        assert ServicioModel is not None
    
    def test_componente_model_import(self):
        """Test importar ComponenteModel."""
        from app.infrastructure.models.componente_model import ComponenteModel
        
        assert ComponenteModel is not None
    
    def test_evento_model_import(self):
        """Test importar EventoModel."""
        from app.infrastructure.models.evento_model import EventoModel
        
        assert EventoModel is not None


class TestRepositoriesImports:
    """Tests para importar repositorios."""
    
    def test_repositorio_orden_import(self):
        """Test importar RepositorioOrden."""
        from app.infrastructure.repositories.repositorio_orden import RepositorioOrden
        
        assert RepositorioOrden is not None
    
    def test_repositorio_cliente_import(self):
        """Test importar RepositorioClienteSQL."""
        from app.infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
        
        assert RepositorioClienteSQL is not None
    
    def test_repositorio_vehiculo_import(self):
        """Test importar RepositorioVehiculoSQL."""
        from app.infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
        
        assert RepositorioVehiculoSQL is not None
    
    def test_repositorio_servicio_import(self):
        """Test importar RepositorioServicioSQL."""
        from app.infrastructure.repositories.repositorio_servicio import RepositorioServicioSQL
        
        assert RepositorioServicioSQL is not None
    
    def test_repositorio_evento_import(self):
        """Test importar RepositorioEventoSQL."""
        from app.infrastructure.repositories.repositorio_evento import RepositorioEventoSQL
        
        assert RepositorioEventoSQL is not None


class TestApplicationDTOs:
    """Tests para DTOs de aplicación."""
    
    def test_crear_orden_dto_import(self):
        """Test importar CrearOrdenDTO."""
        from app.application.dtos import CrearOrdenDTO
        
        assert CrearOrdenDTO is not None
    
    def test_agregar_servicio_dto_import(self):
        """Test importar AgregarServicioDTO."""
        from app.application.dtos import AgregarServicioDTO
        
        assert AgregarServicioDTO is not None


class TestApplicationMappers:
    """Tests para mappers de aplicación."""
    
    def test_crear_orden_dto_callable(self):
        from app.application.mappers import crear_orden_dto
        assert callable(crear_orden_dto)


class TestApplicationPorts:
    """Tests para puertos de aplicación."""
    
    def test_repositories_port_import(self):
        """Test importar RepositorioOrden port."""
        from app.application.ports import RepositorioOrden
        
        assert RepositorioOrden is not None


class TestDomainExceptions:
    """Tests para excepciones de dominio."""
    
    def test_error_dominio_import(self):
        """Test importar ErrorDominio."""
        from app.domain.exceptions import ErrorDominio
        
        assert ErrorDominio is not None
    
    def test_error_dominio_creation(self):
        """Test crear ErrorDominio."""
        from app.domain.exceptions import ErrorDominio
        from app.domain.enums.error_code import CodigoError
        
        error = ErrorDominio(
            codigo=CodigoError.INVALID_STATE,
            mensaje="Test error"
        )
        assert error.codigo == CodigoError.INVALID_STATE
        assert error.mensaje == "Test error"


class TestDomainEnums:
    """Tests para enums de dominio."""
    
    def test_order_status_import(self):
        """Test importar EstadoOrden."""
        from app.domain.enums.order_status import EstadoOrden
        
        assert EstadoOrden is not None
    
    def test_error_code_import(self):
        """Test importar CodigoError."""
        from app.domain.enums.error_code import CodigoError
        
        assert CodigoError is not None


class TestDomainEntidades:
    """Tests para entidades de dominio."""
    
    def test_orden_import(self):
        """Test importar Orden."""
        from app.domain.entidades.order import Orden
        
        assert Orden is not None
    
    def test_cliente_import(self):
        """Test importar Cliente."""
        from app.domain.entidades.cliente import Cliente
        
        assert Cliente is not None
    
    def test_vehiculo_import(self):
        """Test importar Vehiculo."""
        from app.domain.entidades.vehiculo import Vehiculo
        
        assert Vehiculo is not None
    
    def test_servicio_import(self):
        """Test importar Servicio."""
        from app.domain.entidades.service import Servicio
        
        assert Servicio is not None
    
    def test_componente_import(self):
        """Test importar Componente."""
        from app.domain.entidades.component import Componente
        
        assert Componente is not None
    
    def test_evento_import(self):
        """Test importar Evento."""
        from app.domain.entidades.event import Evento
        
        assert Evento is not None


class TestDomainMoney:
    """Tests para dinero de dominio."""
    
    def test_dinero_import(self):
        """Test importar módulo dinero."""
        from app.domain import dinero
        
        assert dinero is not None


class TestDomainTimezone:
    """Tests para timezone de dominio."""
    
    def test_zona_horaria_import(self):
        """Test importar zona_horaria."""
        from app.domain.zona_horaria import obtener_zona_horaria
        
        assert callable(obtener_zona_horaria)


class TestApplicationAcciones:
    """Tests para acciones de aplicación."""
    
    def test_acciones_orden_import(self):
        """Test importar acciones orden."""
        from app.application.acciones.orden import CrearOrden
        
        assert CrearOrden is not None
    
    def test_acciones_estados_import(self):
        """Test importar acciones estados."""
        from app.application.acciones.estados import EstablecerEstadoDiagnosticado
        
        assert EstablecerEstadoDiagnosticado is not None
    
    def test_acciones_autorizacion_import(self):
        """Test importar acciones autorizacion."""
        from app.application.acciones.autorizacion import Autorizar
        
        assert Autorizar is not None
    
    def test_acciones_servicios_import(self):
        """Test importar acciones servicios."""
        from app.application.acciones.servicios import AgregarServicio
        
        assert AgregarServicio is not None


class TestActionService:
    """Tests para action service."""
    
    def test_action_service_import(self):
        """Test importar ActionService."""
        from app.application.action_service import ActionService
        
        assert ActionService is not None
