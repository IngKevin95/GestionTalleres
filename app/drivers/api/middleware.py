import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ...infrastructure.logging_config import obtener_logger, request_id_var

logger = obtener_logger("app.drivers.api.middleware")
logger_errores = obtener_logger("app.drivers.api.errors")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        inicio = time.time()
        metodo = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        request_id_var.set(req_id)
        
        logger.info(
            f"REQUEST {metodo} {path} desde {client_ip}",
            extra={
                "request_id": req_id,
                "method": metodo,
                "path": path,
                "client_ip": client_ip
            }
        )
        
        try:
            response = await call_next(request)
            tiempo_respuesta = (time.time() - inicio) * 1000
            
            response.headers["X-Request-ID"] = req_id
            
            logger.info(
                f"RESPONSE {metodo} {path} - {response.status_code} - {tiempo_respuesta:.2f}ms",
                extra={
                    "request_id": req_id,
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
                    "request_id": req_id,
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
