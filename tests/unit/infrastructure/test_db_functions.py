from unittest.mock import Mock, patch
import os
from app.infrastructure.db import obtener_url_bd, crear_engine_bd, obtener_sesion


def test_obtener_url_bd():
    with patch.dict(os.environ, {
        'POSTGRES_USER': 'test_user',
        'POSTGRES_PASSWORD': 'test_pass',
        'DB_HOST': 'test_host',
        'DB_INTERNAL_PORT': '5433',
        'POSTGRES_DB': 'test_db'
    }):
        url = obtener_url_bd()
        assert 'test_user' in url
        assert 'test_pass' in url
        assert 'test_host' in url
        assert '5433' in url
        assert 'test_db' in url


def test_obtener_url_bd_defaults():
    with patch.dict(os.environ, {}, clear=True):
        url = obtener_url_bd()
        assert 'talleres_user' in url
        assert 'talleres' in url


def test_crear_engine_bd():
    with patch('app.infrastructure.db.create_engine') as mock_create:
        mock_engine = Mock()
        mock_create.return_value = mock_engine
        
        engine = crear_engine_bd("postgresql://test:test@localhost/test")
        
        mock_create.assert_called_once()
        assert engine is not None


def test_obtener_sesion():
    with patch('app.infrastructure.db.SessionLocal') as mock_session_local:
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        
        sesion = obtener_sesion()
        
        assert sesion is not None

