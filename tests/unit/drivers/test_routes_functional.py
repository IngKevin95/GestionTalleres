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
    """Test raíz retorna información de API."""
    result = root()
    assert result is not None
    assert "message" in result
    assert result["message"] == "GestionTalleres API"
    assert "version" in result
    assert result["version"] == "1.0.0"


def test_health_endpoint_import():
    """Test que endpoint /health existe."""
    from app.drivers.api.routes import router
    routes = [route.path for route in router.routes]
    assert "/health" in routes


def test_root_path_import():
    """Test que endpoint / existe."""
    from app.drivers.api.routes import router
    routes = [route.path for route in router.routes]
    assert "/" in routes


# ============================================================================
# Tests para estructura de router
# ============================================================================

def test_router_exists():
    """Test que router está configurado."""
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
        id_orden="ORD-001",
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
        id_cliente="CUST-001"
    )
    
    dto = cliente_a_dto(cliente)
    assert dto.id_cliente == "CUST-001"
    assert dto.nombre == "Juan Pérez"


def test_vehiculo_a_dto_mapping():
    """Test conversión Vehiculo a DTO."""
    from app.application.mappers import vehiculo_a_dto
    
    vehiculo = Vehiculo(
        descripcion="Auto Toyota",
        id_cliente="CUST-001",
        marca="Toyota",
        modelo="Corolla",
        anio=2020,
        id_vehiculo="VEH-001"
    )
    
    dto = vehiculo_a_dto(vehiculo)
    assert dto.id_vehiculo == "VEH-001"
    assert dto.marca == "Toyota"
    assert dto.modelo == "Corolla"
    assert dto.anio == 2020


# ============================================================================
# Tests para JSON to DTO conversions
# ============================================================================

def test_json_a_crear_orden_dto():
    """Test conversión JSON a CrearOrdenDTO."""
    from app.application.mappers import json_a_crear_orden_dto
    from app.domain.zona_horaria import ahora
    
    json_data = {
        "customer": "Juan",
        "vehicle": "Auto"
    }
    
    dto = json_a_crear_orden_dto(json_data)
    assert dto.cliente == "Juan"
    assert dto.vehiculo == "Auto"
    assert dto.timestamp is not None


def test_json_a_agregar_servicio_dto():
    """Test conversión JSON a AgregarServicioDTO."""
    from app.application.mappers import json_a_agregar_servicio_dto
    from decimal import Decimal
    
    json_data = {
        "order_id": "ORD-001",
        "description": "Cambio de aceite",
        "labor_estimated_cost": "500.00"
    }
    
    dto = json_a_agregar_servicio_dto(json_data)
    assert dto.order_id == "ORD-001"
    assert dto.descripcion == "Cambio de aceite"


def test_json_a_autorizar_dto():
    """Test conversión JSON a AutorizarDTO."""
    from app.application.mappers import json_a_autorizar_dto
    
    json_data = {
        "order_id": "ORD-001"
    }
    
    dto = json_a_autorizar_dto(json_data)
    assert dto.order_id == "ORD-001"
    assert dto.timestamp is not None


def test_json_a_establecer_costo_real_dto():
    """Test conversión JSON a EstablecerCostoRealDTO."""
    from app.application.mappers import json_a_establecer_costo_real_dto
    from decimal import Decimal
    
    json_data = {
        "order_id": "ORD-001",
        "real_cost": "1200.00"
    }
    
    dto = json_a_establecer_costo_real_dto(json_data)
    assert dto.order_id == "ORD-001"
    assert dto.costo_real == Decimal("1200.00")


def test_json_a_entregar_dto():
    """Test conversión JSON a EntregarDTO."""
    from app.application.mappers import json_a_entregar_dto
    
    json_data = {
        "order_id": "ORD-001"
    }
    
    dto = json_a_entregar_dto(json_data)
    assert dto.order_id == "ORD-001"


def test_json_a_cancelar_dto():
    """Test conversión JSON a CancelarDTO."""
    from app.application.mappers import json_a_cancelar_dto
    
    json_data = {
        "order_id": "ORD-001",
        "reason": "Cliente cambió de opinión"
    }
    
    dto = json_a_cancelar_dto(json_data)
    assert dto.order_id == "ORD-001"
    assert dto.motivo == "Cliente cambió de opinión"


def test_json_a_reautorizar_dto():
    """Test conversión JSON a ReautorizarDTO."""
    from app.application.mappers import json_a_reautorizar_dto
    from decimal import Decimal
    
    json_data = {
        "order_id": "ORD-001",
        "new_authorized_amount": "1500.00"
    }
    
    dto = json_a_reautorizar_dto(json_data)
    assert dto.order_id == "ORD-001"
    assert dto.nuevo_monto_autorizado == Decimal("1500.00")


def test_json_a_intentar_completar_dto():
    """Test conversión JSON a IntentarCompletarDTO."""
    from app.application.mappers import json_a_intentar_completar_dto
    
    json_data = {
        "order_id": "ORD-001"
    }
    
    dto = json_a_intentar_completar_dto(json_data)
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
    """Test que todos los mappers existen."""
    from app.drivers.api.routes import (
        orden_a_dto, cliente_a_dto, vehiculo_a_dto,
        json_a_crear_orden_dto, json_a_agregar_servicio_dto,
        json_a_autorizar_dto, json_a_reautorizar_dto,
        json_a_establecer_costo_real_dto, json_a_intentar_completar_dto,
        json_a_entregar_dto, json_a_cancelar_dto
    )
    
    assert callable(orden_a_dto)
    assert callable(cliente_a_dto)
    assert callable(vehiculo_a_dto)
    assert callable(json_a_crear_orden_dto)


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


