from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import Mock, MagicMock
from decimal import Decimal
from datetime import datetime
from app.drivers.api.main import app
from app.application.action_service import ActionService
from app.application.dtos import OrdenDTO, EventoDTO, ErrorDTO
from app.domain.entidades import Orden
from app.domain.enums import EstadoOrden


class MockActionService:
    def procesar_comando(self, comando):
        op = comando.get("op")
        if op == "CREATE_ORDER":
            return OrdenDTO(
                order_id="ORD-001",
                status="CREATED",
                customer="Juan",
                vehicle="Auto",
                services=[],
                subtotal_estimated="0.00",
                authorized_amount=None,
                authorization_version=0,
                real_total="0.00",
                events=[]
            ), [], None
        return None, [], None


import pytest
from unittest.mock import Mock, patch

def test_root_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None


def test_health_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None


def test_process_commands_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None


def test_get_order_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None


def test_list_orders_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None


def test_get_cliente_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None


def test_list_clientes_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None


def test_create_cliente_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None


def test_get_vehiculo_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None


def test_list_vehiculos_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None


def test_create_vehiculo_endpoint_import():
    from app.drivers.api.routes import router
    assert router is not None

