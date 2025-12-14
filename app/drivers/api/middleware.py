import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ...infrastructure.logging_config import obtener_logger


logger = obtener_logger("app.drivers.api.middleware")
logger_errores = obtener_logger("app.drivers.api.errors")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        inicio = time.time()
        metodo = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        logger.info(f"REQUEST {metodo} {path} desde {client_ip}")
        
        try:
            response = await call_next(request)
            tiempo_respuesta = (time.time() - inicio) * 1000
            
            logger.info(
                f"RESPONSE {metodo} {path} - {response.status_code} - {tiempo_respuesta:.2f}ms",
                extra={
                    "method": metodo,
                    "path": path,
                    "status_code": response.status_code,
                    "response_time_ms": round(tiempo_respuesta, 2),
                    "client_ip": client_ip
                }
            )
            
            return response
            
        except Exception as e:
            tiempo_respuesta = (time.time() - inicio) * 1000
            logger_errores.error(
                f"ERROR NO CONTROLADO {metodo} {path}: {type(e).__name__}: {str(e)}",
                extra={
                    "method": metodo,
                    "path": path,
                    "response_time_ms": round(tiempo_respuesta, 2),
                    "client_ip": client_ip,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            raise
