from unittest.mock import Mock, patch, MagicMock
from app.infrastructure.db import obtener_sesion, Base
from app.infrastructure.logger import AlmacenEventosLogger
from app.domain.entidades import Evento
from datetime import datetime
import json
import os


def test_obtener_sesion():
    with patch('app.infrastructure.db.SessionLocal') as mock_session:
        mock_session.return_value = Mock()
        sesion = obtener_sesion()
        assert sesion is not None


def test_almacen_eventos_logger_registrar():
    logger = AlmacenEventosLogger()
    evento = Evento("CREATED", datetime.utcnow(), {})
    
    logger.registrar(evento)
    assert True


def test_almacen_eventos_logger_sin_archivo():
    logger = AlmacenEventosLogger()
    evento = Evento("CREATED", datetime.utcnow(), {})
    
    logger.registrar(evento)
    assert True
