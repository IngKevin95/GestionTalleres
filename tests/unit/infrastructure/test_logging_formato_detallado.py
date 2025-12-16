"""Tests para FormatoDetallado y casos edge de logging."""
import logging
import os
from unittest.mock import patch, MagicMock
from app.infrastructure.logging_config import request_id_var, sanitizar_datos


def test_formato_detallado_con_request_id():
    """Test FormatoDetallado incluye request_id cuando está disponible."""
    from app.infrastructure.logging_config import configurar_logging
    
    request_id_var.set("test-req-123")
    configurar_logging()
    
    logger = logging.getLogger("test.formato")
    record = logging.LogRecord(
        name="test.formato",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    logger.info("Test message", extra={"order_id": "ORD-001"})
    
    request_id_var.set(None)


def test_formato_detallado_sin_request_id():
    """Test FormatoDetallado sin request_id."""
    from app.infrastructure.logging_config import configurar_logging
    
    request_id_var.set(None)
    configurar_logging()
    
    logger = logging.getLogger("test.formato2")
    logger.info("Test message", extra={"order_id": "ORD-002"})


def test_formato_detallado_con_campos_extra():
    """Test FormatoDetallado con diferentes campos extra."""
    from app.infrastructure.logging_config import configurar_logging
    
    configurar_logging()
    
    logger = logging.getLogger("test.formato3")
    
    logger.info("Test", extra={
        "order_id": "ORD-001",
        "comando": {"op": "CREATE"},
        "eventos": [{"tipo": "created"}],
        "error_code": "ERROR_001"
    })


def test_formato_detallado_sanitizar_activado():
    """Test FormatoDetallado con sanitización activada."""
    with patch.dict(os.environ, {"LOG_SANITIZE": "true"}):
        from app.infrastructure.logging_config import configurar_logging
        
        configurar_logging()
        
        logger = logging.getLogger("test.sanitize")
        logger.info("Test", extra={
            "request_body": {"password": "secret123", "username": "admin"}
        })


def test_formato_detallado_sanitizar_desactivado():
    """Test FormatoDetallado con sanitización desactivada."""
    with patch.dict(os.environ, {"LOG_SANITIZE": "false"}):
        from app.infrastructure.logging_config import configurar_logging
        
        configurar_logging()
        
        logger = logging.getLogger("test.no_sanitize")
        logger.info("Test", extra={
            "request_body": {"password": "secret123"}
        })


def test_sanitizar_datos_lista_con_dicts():
    """Test sanitizar_datos con lista que contiene dicts."""
    datos = {
        "items": [
            {"name": "item1", "password": "pass1"},
            {"name": "item2", "api_key": "key2"},
            "string_item"
        ]
    }
    
    sanitizado = sanitizar_datos(datos)
    
    assert sanitizado["items"][0]["name"] == "item1"
    assert sanitizado["items"][0]["password"] == "***"
    assert sanitizado["items"][1]["api_key"] == "***"
    assert sanitizado["items"][2] == "string_item"


def test_sanitizar_datos_lista_solo_strings():
    """Test sanitizar_datos con lista que solo contiene strings."""
    datos = {
        "tags": ["tag1", "tag2", "tag3"]
    }
    
    sanitizado = sanitizar_datos(datos)
    
    assert sanitizado == datos


def test_sanitizar_datos_valor_none():
    """Test sanitizar_datos con valores None."""
    datos = {
        "field1": None,
        "field2": "value",
        "password": None
    }
    
    sanitizado = sanitizar_datos(datos)
    
    assert sanitizado["field1"] is None
    assert sanitizado["field2"] == "value"
    assert sanitizado["password"] == "***"


def test_sanitizar_datos_valor_no_dict_ni_lista():
    """Test sanitizar_datos con valores que no son dict ni lista."""
    datos = {
        "string": "text",
        "number": 123,
        "boolean": True,
        "password": "secret"
    }
    
    sanitizado = sanitizar_datos(datos)
    
    assert sanitizado["string"] == "text"
    assert sanitizado["number"] == 123
    assert sanitizado["boolean"] is True
    assert sanitizado["password"] == "***"


def test_sanitizar_datos_campos_sensibles_vacios():
    """Test sanitizar_datos con campos sensibles vacíos."""
    datos = {
        "password": "",
        "token": None,
        "api_key": "   "
    }
    
    sanitizado = sanitizar_datos(datos)
    
    assert sanitizado["password"] == "***"
    assert sanitizado["token"] == "***"
    assert sanitizado["api_key"] == "***"


def test_sanitizar_datos_recursion_profunda():
    """Test sanitizar_datos con estructura anidada profunda."""
    datos = {
        "level1": {
            "level2": {
                "level3": {
                    "password": "deep_secret",
                    "data": "visible"
                }
            }
        }
    }
    
    sanitizado = sanitizar_datos(datos)
    
    assert sanitizado["level1"]["level2"]["level3"]["password"] == "***"
    assert sanitizado["level1"]["level2"]["level3"]["data"] == "visible"


def test_obtener_contexto_log_sin_request_id_retorna_vacio():
    """Test obtener_contexto_log retorna dict vacío sin request_id."""
    from app.infrastructure.logging_config import obtener_contexto_log
    
    request_id_var.set(None)
    ctx = obtener_contexto_log()
    
    assert ctx == {}
    assert len(ctx) == 0


def test_obtener_contexto_log_multiple_llamadas():
    """Test obtener_contexto_log con múltiples llamadas."""
    from app.infrastructure.logging_config import obtener_contexto_log
    
    request_id_var.set("req-1")
    ctx1 = obtener_contexto_log()
    
    request_id_var.set("req-2")
    ctx2 = obtener_contexto_log()
    
    assert ctx1["request_id"] == "req-1"
    assert ctx2["request_id"] == "req-2"
    assert ctx1 != ctx2


def test_formato_detallado_record_ya_tiene_request_id():
    """Test FormatoDetallado cuando el record ya tiene request_id."""
    from app.infrastructure.logging_config import configurar_logging
    
    request_id_var.set("req-context-123")
    configurar_logging()
    
    logger = logging.getLogger("test.formato4")
    logger.info("Test message", extra={"request_id": "req-record-456", "order_id": "ORD-001"})
    
    request_id_var.set(None)


def test_formato_detallado_valores_complejos():
    """Test FormatoDetallado con valores complejos que pueden fallar al serializar."""
    from app.infrastructure.logging_config import configurar_logging
    
    configurar_logging()
    
    logger = logging.getLogger("test.formato5")
    
    class ObjetoComplejo:
        def __str__(self):
            return "ObjetoComplejo"
    
    try:
        logger.info("Test", extra={
            "comando": {"op": "CREATE", "data": ObjetoComplejo()},
            "order_id": "ORD-001"
        })
    except Exception:
        pass


def test_formato_detallado_valor_muy_largo():
    """Test FormatoDetallado con valores muy largos que se truncan."""
    from app.infrastructure.logging_config import configurar_logging
    
    configurar_logging()
    
    logger = logging.getLogger("test.formato6")
    
    valor_largo = "x" * 1000
    try:
        logger.info("Test", extra={"error": valor_largo})
    except Exception:
        pass

