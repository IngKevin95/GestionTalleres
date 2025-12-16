"""Tests funcionales para rutas HTTP principales."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime

from app.drivers.api.routes import router, root
from app.application.dtos import (
    OrdenDTO, EventoDTO, ErrorDTO, CrearOrdenDTO, 
    AgregarServicioDTO, AutorizarDTO
)
from app.domain.enums import EstadoOrden, CodigoError
from app.domain.entidades import Orden, Cliente, Vehiculo


# ============================================================================
# Tests para endpoints simples (GET /, GET /health)
# ============================================================================

def test_root_endpoint():
    result = root()
    assert result is not None
    assert "message" in result
    assert result["message"] == "GestionTalleres API"
    assert "version" in result
    assert result["version"] == "1.0.0"


# ============================================================================
# Tests para estructura de router
# ============================================================================

def test_router_exists():
    assert router is not None
    assert len(router.routes) > 0


def test_router_has_get_methods():
    """Test que router tiene métodos GET."""
    methods = set()
    for route in router.routes:
        if hasattr(route, 'methods'):
            methods.update(route.methods)
    
    assert 'GET' in methods


def test_router_has_post_methods():
    """Test que router tiene métodos POST."""
    methods = set()
    for route in router.routes:
        if hasattr(route, 'methods'):
            methods.update(route.methods)
    
    assert 'POST' in methods


# ============================================================================
# Tests de mappers y conversiones
# ============================================================================

def test_orden_a_dto_mapping():
    """Test conversión Orden a OrdenDTO."""
    from app.application.mappers import orden_a_dto
    from app.domain.zona_horaria import ahora
    
    orden = Orden(
        order_id="ORD-001",
        cliente="Juan",
        vehiculo="Auto",
        fecha_creacion=ahora()
    )
    
    dto = orden_a_dto(orden)
    assert dto.order_id == "ORD-001"
    assert dto.status == "CREATED"


def test_cliente_a_dto_mapping():
    """Test conversión Cliente a DTO."""
    from app.application.mappers import cliente_a_dto
    
    cliente = Cliente(
        nombre="Juan Pérez",
        id_cliente=1  # ID debe ser int, no string
    )
    
    dto = cliente_a_dto(cliente)
    assert dto.id_cliente == 1
    assert dto.nombre == "Juan Pérez"


def test_vehiculo_a_dto_mapping():
    """Test conversión Vehiculo a DTO."""
    from app.application.mappers import vehiculo_a_dto
    
    vehiculo = Vehiculo(
        placa="ABC-123",  # placa, no descripcion
        id_cliente=1,  # int, no string
        marca="Toyota",
        modelo="Corolla",
        anio=2020,
        id_vehiculo=1  # int, no string
    )
    
    dto = vehiculo_a_dto(vehiculo)
    assert dto.id_vehiculo == 1
    assert dto.marca == "Toyota"
    assert dto.modelo == "Corolla"
    assert dto.anio == 2020


# ============================================================================
# Tests para JSON to DTO conversions
# ============================================================================

def test_crear_orden_dto():
    from app.application.mappers import crear_orden_dto
    
    data = {
        "order_id": "ORD-001",
        "customer": "Juan",
        "vehicle": "Auto"
    }
    
    dto = crear_orden_dto(data)
    assert dto.order_id == "ORD-001"
    assert dto.customer.nombre == "Juan"
    assert dto.vehicle.placa == "Auto"
    assert dto.timestamp is not None


def test_agregar_servicio_dto():
    from app.application.mappers import agregar_servicio_dto
    
    data = {
        "order_id": "ORD-001",
        "description": "Cambio de aceite",
        "labor_estimated_cost": "500.00"
    }
    
    dto = agregar_servicio_dto(data)
    assert dto.order_id == "ORD-001"
    assert dto.descripcion == "Cambio de aceite"


def test_autorizar_dto():
    from app.application.mappers import autorizar_dto
    
    data = {"order_id": "ORD-001"}
    
    dto = autorizar_dto(data)
    assert dto.order_id == "ORD-001"
    assert dto.timestamp is not None


def test_costo_real_dto():
    from app.application.mappers import costo_real_dto
    from decimal import Decimal
    
    data = {
        "order_id": "ORD-001",
        "real_cost": "1200.00"
    }
    
    dto = costo_real_dto(data)
    assert dto.order_id == "ORD-001"
    assert dto.costo_real == Decimal("1200.00")


def test_entregar_dto():
    from app.application.mappers import entregar_dto
    
    data = {"order_id": "ORD-001"}
    
    dto = entregar_dto(data)
    assert dto.order_id == "ORD-001"


def test_cancelar_dto():
    from app.application.mappers import cancelar_dto
    
    data = {
        "order_id": "ORD-001",
        "reason": "Cliente cambió de opinión"
    }
    
    dto = cancelar_dto(data)
    assert dto.order_id == "ORD-001"
    assert dto.motivo == "Cliente cambió de opinión"


def test_reautorizar_dto():
    from app.application.mappers import reautorizar_dto
    from decimal import Decimal
    
    data = {
        "order_id": "ORD-001",
        "new_authorized_amount": "1500.00"
    }
    
    dto = reautorizar_dto(data)
    assert dto.order_id == "ORD-001"
    assert dto.nuevo_monto_autorizado == Decimal("1500.00")


def test_intentar_completar_dto():
    from app.application.mappers import intentar_completar_dto
    
    data = {"order_id": "ORD-001"}
    
    dto = intentar_completar_dto(data)
    assert dto.order_id == "ORD-001"


# ============================================================================
# Tests para funciones de rutas - integración básica
# ============================================================================

def test_routes_dependencies_import():
    """Test que dependencias se importan correctamente."""
    from app.drivers.api.dependencies import (
        obtener_action_service,
        obtener_repositorio,
        obtener_repositorio_cliente,
        obtener_repositorio_vehiculo
    )
    assert callable(obtener_action_service)
    assert callable(obtener_repositorio)
    assert callable(obtener_repositorio_cliente)
    assert callable(obtener_repositorio_vehiculo)


def test_routes_schemas_import():
    """Test que esquemas se importan correctamente."""
    from app.drivers.api.schemas import (
        HealthResponse, CommandsRequest, CommandsResponse
    )


def test_routes_dtos_import():
    """Test que DTOs se importan correctamente."""
    from app.drivers.api.routes import (
        OrdenDTO, EventoDTO, ErrorDTO, CrearOrdenDTO
    )
    assert OrdenDTO is not None
    assert EventoDTO is not None
    assert ErrorDTO is not None
    assert CrearOrdenDTO is not None


def test_routes_mappers_all_exist():
    from app.application.mappers import (
        orden_a_dto, cliente_a_dto, vehiculo_a_dto,
        crear_orden_dto, agregar_servicio_dto,
        autorizar_dto, reautorizar_dto,
        costo_real_dto, intentar_completar_dto,
        entregar_dto, cancelar_dto
    )
    
    assert callable(orden_a_dto)
    assert callable(cliente_a_dto)
    assert callable(vehiculo_a_dto)
    assert callable(crear_orden_dto)


def test_routes_logger_initialized():
    """Test que logger se inicializa."""
    from app.drivers.api.routes import logger
    assert logger is not None


# ============================================================================
# Tests para excepciones y manejo de errores
# ============================================================================

def test_error_dominio_import():
    """Test que ErrorDominio se importa en routes."""
    from app.drivers.api.routes import ErrorDominio
    assert ErrorDominio is not None


def test_codes_defined():
    """Test que códigos de error están definidos."""
    from app.domain.enums.error_code import CodigoError
    
    assert CodigoError.ORDER_NOT_FOUND is not None
    assert CodigoError.INVALID_OPERATION is not None
    assert CodigoError.SEQUENCE_ERROR is not None


