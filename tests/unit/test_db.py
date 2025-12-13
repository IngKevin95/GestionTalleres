import os
from unittest.mock import patch, Mock
from app.infrastructure.db import obtener_url_bd, crear_engine_bd, obtener_sesion


def test_obtener_sesion():
    with patch('app.infrastructure.db.crear_engine_bd') as mock_crear:
        mock_engine = Mock()
        mock_crear.return_value = mock_engine
        
        with patch('app.infrastructure.db.sessionmaker') as mock_sessionmaker:
            mock_session_class = Mock()
            mock_session_instance = Mock()
            mock_session_class.return_value = mock_session_instance
            mock_sessionmaker.return_value = mock_session_class
            
            sesion = obtener_sesion()
            
            assert sesion == mock_session_instance
            mock_sessionmaker.assert_called_once_with(bind=mock_engine)

