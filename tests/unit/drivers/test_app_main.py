import pytest
from fastapi import FastAPI


def test_app_es_fastapi():
    from app.drivers.api.main import app
    assert isinstance(app, FastAPI)


def test_app_tiene_rutas():
    from app.drivers.api.main import app
    assert len(app.routes) > 0


def test_app_tiene_router():
    from app.drivers.api.main import app
    assert app.router is not None


def test_app_titulo():
    from app.drivers.api.main import app
    assert app.title == "GestionTalleres API"


def test_app_version():
    from app.drivers.api.main import app
    assert app.version == "1.0.0"


def test_app_tiene_cors():
    from app.drivers.api.main import app
    middleware_names = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_names


def test_app_tiene_logging_middleware():
    from app.drivers.api.main import app
    middleware_names = [m.cls.__name__ for m in app.user_middleware]
    assert "LoggingMiddleware" in middleware_names


def test_app_tiene_exception_handlers():
    from app.drivers.api.main import app
    from fastapi.exceptions import RequestValidationError, ResponseValidationError
    
    assert RequestValidationError in app.exception_handlers
    assert ResponseValidationError in app.exception_handlers


def test_lifespan_existe():
    from app.drivers.api.main import lifespan
    assert callable(lifespan)
