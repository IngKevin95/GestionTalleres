"""Tests para configuración de infraestructura."""
import pytest
from unittest.mock import patch
from app.infrastructure.db import obtener_url_bd, crear_engine_bd
from app.infrastructure.logging_config import configurar_logging, obtener_logger
from app.infrastructure.logger import AlmacenEventosLogger
import logging


class TestObtenerUrlBD:
    """Tests para obtener_url_bd."""
    
    def test_obtener_url_bd_callable(self):
        """Test que obtener_url_bd es callable."""
        assert callable(obtener_url_bd)
    
    def test_obtener_url_bd_retorna_string(self):
        """Test que retorna string."""
        with patch.dict('os.environ', {}, clear=True):
            url = obtener_url_bd()
            assert isinstance(url, str)
    
    def test_obtener_url_bd_postgresql(self):
        """Test que URL contiene postgresql."""
        with patch.dict('os.environ', {}, clear=True):
            url = obtener_url_bd()
            assert "postgresql" in url


class TestCrearEngineBD:
    """Tests para crear_engine_bd."""
    
    def test_crear_engine_bd_callable(self):
        """Test que crear_engine_bd es callable."""
        assert callable(crear_engine_bd)


class TestConfigurarLogging:
    """Tests para configurar_logging."""
    
    def test_configurar_logging_callable(self):
        """Test que configurar_logging es callable."""
        assert callable(configurar_logging)


class TestObtenerLogger:
    """Tests para obtener_logger."""
    
    def test_obtener_logger_callable(self):
        """Test que obtener_logger es callable."""
        assert callable(obtener_logger)
    
    def test_obtener_logger_retorna_logger(self):
        """Test que obtener_logger retorna Logger."""
        logger = obtener_logger("test")
        assert isinstance(logger, logging.Logger)
    
    def test_obtener_logger_con_nombre(self):
        """Test obtener logger con nombre específico."""
        logger = obtener_logger("test.modulo")
        assert logger.name == "test.modulo"


class TestAlmacenEventosLogger:
    """Tests para AlmacenEventosLogger."""
    
    def test_almacen_eventos_logger_import(self):
        """Test importar AlmacenEventosLogger."""
        assert AlmacenEventosLogger is not None
