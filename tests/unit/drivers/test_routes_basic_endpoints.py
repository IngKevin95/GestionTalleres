import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi import HTTPException, status


def test_root_returns_dict():
    from app.drivers.api.routes import root
    resultado = root()
    assert isinstance(resultado, dict)


def test_root_has_message_field():
    from app.drivers.api.routes import root
    resultado = root()
    assert "message" in resultado


def test_root_has_version_field():
    from app.drivers.api.routes import root
    resultado = root()
    assert "version" in resultado


def test_root_message_contains_api_name():
    from app.drivers.api.routes import root
    resultado = root()
    assert "API" in resultado["message"] or "api" in resultado["message"].lower()


def test_router_exists():
    from app.drivers.api.routes import router
    assert router is not None


def test_router_has_routes():
    from app.drivers.api.routes import router
    assert len(router.routes) > 0


def test_router_has_health_route():
    from app.drivers.api.routes import router
    route_paths = [route.path for route in router.routes]
    assert any("health" in path for path in route_paths)


def test_router_has_root_route():
    from app.drivers.api.routes import router
    route_paths = [route.path for route in router.routes]
    assert "/" in route_paths or any(p == "" for p in route_paths)
