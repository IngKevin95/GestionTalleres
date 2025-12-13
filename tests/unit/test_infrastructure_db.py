import os
from unittest.mock import patch, Mock
from app.infrastructure.db import obtener_url_bd, crear_engine_bd, obtener_sesion


def test_obtener_url_bd_default():
    with patch.dict(os.environ, {}, clear=True):
        url = obtener_url_bd()
        assert "postgresql://" in url
        assert "talleres_user" in url
        assert "talleres" in url


def test_obtener_url_bd_con_variables():
    with patch.dict(os.environ, {
        "POSTGRES_USER": "usuario_test",
        "POSTGRES_PASSWORD": "pass_test",
        "DB_HOST": "host_test",
        "DB_INTERNAL_PORT": "5433",
        "POSTGRES_DB": "bd_test"
    }, clear=False):
        url = obtener_url_bd()
        assert "usuario_test" in url
        assert "pass_test" in url
        assert "host_test" in url
        assert "5433" in url
        assert "bd_test" in url


def test_crear_engine_bd_con_url():
    from app.infrastructure.db import _engine
    import app.infrastructure.db as db_module
    
    db_module._engine = None
    url_test = "sqlite:///:memory:"
    engine = crear_engine_bd(url_test)
    assert engine is not None


def test_crear_engine_bd_sin_url():
    import app.infrastructure.db as db_module
    
    db_module._engine = None
    with patch('app.infrastructure.db.obtener_url_bd', return_value="sqlite:///:memory:"):
        engine = crear_engine_bd()
        assert engine is not None

