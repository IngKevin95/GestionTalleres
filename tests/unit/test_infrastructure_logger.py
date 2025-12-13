from datetime import datetime
from unittest.mock import patch, Mock
from app.infrastructure.logger import AlmacenEventosLogger
from app.domain.entidades import Evento


def test_almacen_eventos_logger_init():
    logger = AlmacenEventosLogger()
    assert logger is not None


@patch('app.infrastructure.logger.logger')
def test_almacen_eventos_logger_registrar(mock_logger):
    logger = AlmacenEventosLogger()
    evento = Evento("CREATED", datetime.utcnow(), {"key": "value"})
    
    logger.registrar(evento)
    
    mock_logger.info.assert_called_once()
    args, kwargs = mock_logger.info.call_args
    assert "Evento de dominio registrado" in args[0]
    assert kwargs["extra"]["tipo"] == "CREATED"
    assert kwargs["extra"]["metadata"] == {"key": "value"}

