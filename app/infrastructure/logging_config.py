import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar('request_id', default=None)


class RotatingFileHandlerSeguro(logging.handlers.TimedRotatingFileHandler):
    def doRollover(self):
        try:
            super().doRollover()
        except (PermissionError, OSError):
            pass


class RotatingFileHandlerSizeSeguro(logging.handlers.RotatingFileHandler):
    def doRollover(self):
        try:
            super().doRollover()
        except (PermissionError, OSError):
            pass


def sanitizar_datos(datos: Dict[str, Any], campos_sensibles: Optional[list] = None) -> Dict[str, Any]:
    """
    Sanitiza datos sensibles en logs.
    
    Args:
        datos: Diccionario con datos a sanitizar
        campos_sensibles: Lista de nombres de campos a ocultar. Si es None, usa lista por defecto.
    
    Returns:
        Diccionario con campos sensibles ocultos
    """
    if campos_sensibles is None:
        campos_sensibles = os.getenv("LOG_SENSITIVE_FIELDS", "password,secret,token,api_key,authorization").split(",")
    
    campos_sensibles = [c.strip().lower() for c in campos_sensibles if c.strip()]
    
    sanitizado = {}
    for clave, valor in datos.items():
        clave_lower = clave.lower()
        if any(campo in clave_lower for campo in campos_sensibles):
            sanitizado[clave] = "***"
        elif isinstance(valor, dict):
            sanitizado[clave] = sanitizar_datos(valor, campos_sensibles)
        elif isinstance(valor, list):
            sanitizado[clave] = [
                sanitizar_datos(item, campos_sensibles) if isinstance(item, dict) else item
                for item in valor
            ]
        else:
            sanitizado[clave] = valor
    
    return sanitizado


def configurar_logging():
    nivel = os.getenv("LOG_LEVEL", "INFO").upper()
    formato = os.getenv("LOG_FORMAT", "text").lower()
    directorio_logs = os.getenv("LOG_DIR", "logs")
    rotacion = os.getenv("LOG_ROTATION", "time").lower()
    max_bytes = int(os.getenv("LOG_MAX_BYTES", "10485760"))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "7"))
    log_to_console = os.getenv("LOG_TO_CONSOLE", "false").lower() == "true"
    
    Path(directorio_logs).mkdir(exist_ok=True)
    
    nivel_logging = getattr(logging, nivel, logging.INFO)
    
    class FormatoDetallado(logging.Formatter):
        def format(self, record):
            msg = super().format(record)
            extras = []
            import json
            
            req_id = request_id_var.get(None)
            if req_id and not hasattr(record, 'request_id'):
                extras.append(f"  REQUEST_ID: {req_id}")
            
            campos = [
                'request_id', 'request_body', 'response_body', 'body', 'comando', 'comando_completo',
                'operacion', 'order_id', 'error', 'error_code', 'error_message',
                'validation_errors', 'comando_index', 'eventos', 'status_orden',
                'timestamp', 'codigo', 'mensaje', 'error_type'
            ]
            
            sanitizar = os.getenv("LOG_SANITIZE", "true").lower() == "true"
            
            for campo in campos:
                if hasattr(record, campo):
                    val = getattr(record, campo)
                    if val:
                        try:
                            if isinstance(val, dict) and sanitizar:
                                val = sanitizar_datos(val)
                            if isinstance(val, (dict, list)):
                                extras.append(f"  {campo.upper()}: {json.dumps(val, ensure_ascii=False, indent=2)}")
                            else:
                                extras.append(f"  {campo.upper()}: {val}")
                        except (TypeError, ValueError, AttributeError):
                            extras.append(f"  {campo.upper()}: {str(val)[:500]}")
            
            if extras:
                msg += "\n" + "\n".join(extras)
            return msg
    
    if formato == "json":
        formato_log = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
            datefmt="%Y-%m-%dT%H:%M:%S"
        )
    else:
        formato_log = FormatoDetallado(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    logger_raiz = logging.getLogger()
    logger_raiz.setLevel(nivel_logging)
    
    for handler in logger_raiz.handlers[:]:
        logger_raiz.removeHandler(handler)
    
    if rotacion == "time":
        handler_general = RotatingFileHandlerSeguro(
            os.path.join(directorio_logs, "app.log"),
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8"
        )
        handler_errores = RotatingFileHandlerSeguro(
            os.path.join(directorio_logs, "errors.log"),
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8"
        )
        handler_requests = RotatingFileHandlerSeguro(
            os.path.join(directorio_logs, "requests.log"),
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8"
        )
    elif rotacion == "size":
        handler_general = RotatingFileHandlerSizeSeguro(
            os.path.join(directorio_logs, "app.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        handler_errores = RotatingFileHandlerSizeSeguro(
            os.path.join(directorio_logs, "errors.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        handler_requests = RotatingFileHandlerSizeSeguro(
            os.path.join(directorio_logs, "requests.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
    else:
        handler_general = logging.FileHandler(
            os.path.join(directorio_logs, "app.log"),
            encoding="utf-8"
        )
        handler_errores = logging.FileHandler(
            os.path.join(directorio_logs, "errors.log"),
            encoding="utf-8"
        )
        handler_requests = logging.FileHandler(
            os.path.join(directorio_logs, "requests.log"),
            encoding="utf-8"
        )
    
    handler_general.setLevel(logging.INFO)
    handler_errores.setLevel(logging.ERROR)
    handler_requests.setLevel(logging.INFO)
    
    handler_general.setFormatter(formato_log)
    handler_errores.setFormatter(formato_log)
    handler_requests.setFormatter(formato_log)
    
    # Flush habilitado para escritura inmediata de logs
    # handler_general.flush = lambda: None
    # handler_errores.flush = lambda: None
    # handler_requests.flush = lambda: None
    
    logger_raiz.addHandler(handler_general)
    logger_raiz.addHandler(handler_errores)
    
    logger_requests = logging.getLogger("app.drivers.api.middleware")
    logger_requests.addHandler(handler_requests)
    logger_requests.addHandler(handler_general)
    logger_requests.setLevel(logging.INFO)
    logger_requests.propagate = False
    
    logger_errores_no_controlados = logging.getLogger("app.drivers.api.errors")
    logger_errores_no_controlados.addHandler(handler_errores)
    logger_errores_no_controlados.addHandler(handler_general)
    logger_errores_no_controlados.setLevel(logging.ERROR)
    logger_errores_no_controlados.propagate = False
    
    if log_to_console:
        handler_consola = logging.StreamHandler()
        handler_consola.setLevel(nivel_logging)
        handler_consola.setFormatter(formato_log)
        logger_raiz.addHandler(handler_consola)
    


def obtener_logger(nombre: str) -> logging.Logger:
    return logging.getLogger(nombre)


def obtener_contexto_log() -> Dict[str, Any]:
    """Extrae contexto común para logs (request_id, etc.)"""
    ctx = {}
    req_id = request_id_var.get(None)
    if req_id:
        ctx['request_id'] = req_id
    return ctx

