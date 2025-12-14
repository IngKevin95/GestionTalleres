import os
import logging
from unittest.mock import patch, Mock
from app.infrastructure.logging_config import configurar_logging, obtener_logger


def test_configurar_logging_nivel_info():
    with patch.dict('os.environ', {'LOG_LEVEL': 'INFO'}):
        with patch('app.infrastructure.logging_config.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            configurar_logging()
            
            mock_path_instance.mkdir.assert_called_once()


def test_configurar_logging_nivel_debug():
    with patch.dict('os.environ', {'LOG_LEVEL': 'DEBUG'}):
        with patch('app.infrastructure.logging_config.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            configurar_logging()
            
            mock_path_instance.mkdir.assert_called_once()


def test_configurar_logging_formato_json():
    with patch.dict('os.environ', {'LOG_FORMAT': 'json'}):
        with patch('app.infrastructure.logging_config.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            configurar_logging()
            
            mock_path_instance.mkdir.assert_called_once()


def test_configurar_logging_rotacion_por_tiempo():
    with patch.dict('os.environ', {'LOG_ROTATION': 'time'}):
        with patch('app.infrastructure.logging_config.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            configurar_logging()
            
            mock_path_instance.mkdir.assert_called_once()


def test_configurar_logging_rotacion_por_tamaño():
    with patch.dict('os.environ', {'LOG_ROTATION': 'size'}):
        with patch('app.infrastructure.logging_config.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            configurar_logging()
            
            mock_path_instance.mkdir.assert_called_once()


def test_configurar_logging_valores_por_defecto():
    with patch.dict('os.environ', {}, clear=True):
        with patch('app.infrastructure.logging_config.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            configurar_logging()
            
            mock_path_instance.mkdir.assert_called_once()


def test_obtener_logger():
    logger = obtener_logger("test.module")
    assert logger is not None
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.module"


def test_obtener_logger_diferentes_nombres():
    logger1 = obtener_logger("module1")
    logger2 = obtener_logger("module2")
    
    assert logger1.name == "module1"
    assert logger2.name == "module2"

