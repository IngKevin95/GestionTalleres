import pytest
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from unittest.mock import Mock
from app.drivers.api.main import app
from app.drivers.api.middleware import LoggingMiddleware
from app.drivers.api.dependencies import obtener_action_service, obtener_sesion


def test_app_es_fastapi():
    assert isinstance(app, FastAPI)


def test_app_tiene_rutas():
    routes = list(app.routes)
    assert len(routes) > 0


def test_app_tiene_router():
    assert app.router is not None


def test_app_title():
    assert app.title == "GestionTalleres API"


def test_logging_middleware_es_base_http_middleware():
    assert issubclass(LoggingMiddleware, BaseHTTPMiddleware)


def test_obtener_action_service_callable():
    assert callable(obtener_action_service)


def test_obtener_sesion_callable():
    assert callable(obtener_sesion)
