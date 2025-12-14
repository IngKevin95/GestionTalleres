import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Receive
from starlette.responses import JSONResponse, Response
from starlette.types import Message

from ...infrastructure.logging_config import obtener_logger


logger = obtener_logger("app.drivers.api.middleware")


class BodyCapturingReceive:
    def __init__(self, receive: Receive):
        self.receive = receive
        self._body = b""
        self._messages = []
        self._all_consumed = False
        self._current_index = 0
    
    async def __call__(self):
        if self._all_consumed and self._current_index < len(self._messages):
            msg = self._messages[self._current_index].copy()
            self._current_index += 1
            return msg
        
        message = await self.receive()
        if message["type"] == "http.request":
            body = message.get("body", b"")
            self._body += body
            if not message.get("more_body", False):
                self._all_consumed = True
            msg_copy = message.copy()
            self._messages.append(msg_copy)
            self._current_index = len(self._messages)
        return message
    
    def get_body(self) -> bytes:
        return self._body
    
    def reset(self):
        self._current_index = 0


class ResponseCapturingWrapper:
    def __init__(self, response: Response):
        self.response = response
        self._body = None
    
    async def __call__(self, scope, receive, send):
        async def send_wrapper(message: Message):
            if message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    self._body = body
            await send(message)
        
        await self.response(scope, receive, send_wrapper)
    
    def get_body(self):
        return self._body


class LoggingMiddleware(BaseHTTPMiddleware):
    def _obtener_info_request(self, request: Request) -> dict:
        """Extrae información del request."""
        return {
            "metodo": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params) if request.query_params else "",
            "client_ip": request.client.host if request.client else "unknown"
        }
    
    def _obtener_body_request(self, path: str, metodo: str) -> dict:
        """Determina el body del request a loguear."""
        if path == "/commands" and metodo == "POST":
            return {"nota": "Body será capturado en endpoint o exception handler"}
        return {}
    
    def _extraer_body_json(self, response: Response) -> dict:
        """Extrae body JSON de la respuesta."""
        try:
            if isinstance(response, JSONResponse):
                if hasattr(response, "body") and response.body:
                    return json.loads(response.body.decode("utf-8"))
                elif hasattr(response, "render"):
                    rendered = response.render({})
                    if rendered:
                        return json.loads(rendered.decode("utf-8"))
                elif hasattr(response, "_content"):
                    return json.loads(response._content.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            pass
        return {}
    
    def _obtener_body_response(self, path: str, response: Response) -> dict:
        """Obtiene el body de la respuesta para logging."""
        if path != "/commands":
            return {}
        
        try:
            return self._extraer_body_json(response)
        except Exception as e:
            return {"error_captura": str(e)}
    
    def _log_request(self, info: dict, body_request: dict) -> None:
        """Registra el request inicial."""
        logger.info(
            f"Request {info['metodo']} {info['path']}",
            extra={
                "method": info['metodo'],
                "path": info['path'],
                "query_params": info['query_params'],
                "client_ip": info['client_ip'],
                "request_body": body_request
            }
        )
    
    def _log_response(self, info: dict, tiempo_respuesta: float, 
                     status_code: int, body_request: dict, body_response: dict) -> None:
        """Registra la respuesta."""
        log_data = {
            "method": info['metodo'],
            "path": info['path'],
            "status_code": status_code,
            "response_time_ms": tiempo_respuesta,
            "client_ip": info['client_ip'],
            "request_body": body_request,
            "response_body": body_response
        }
        
        if status_code >= 400:
            logger.error(
                f"Request {info['metodo']} {info['path']} procesado en {tiempo_respuesta:.2f}ms, status {status_code}",
                extra=log_data
            )
        else:
            logger.info(
                f"Request {info['metodo']} {info['path']} procesado en {tiempo_respuesta:.2f}ms, status {status_code}",
                extra=log_data
            )
    
    def _log_error(self, info: dict, tiempo_respuesta: float, 
                  body_request: dict, error: Exception) -> None:
        """Registra un error al procesar el request."""
        logger.error(
            f"Error al procesar request {info['metodo']} {info['path']}: {str(error)}",
            extra={
                "method": info['metodo'],
                "path": info['path'],
                "response_time_ms": tiempo_respuesta,
                "client_ip": info['client_ip'],
                "request_body": body_request,
                "error": str(error),
                "error_type": type(error).__name__
            },
            exc_info=True
        )
    
    async def dispatch(self, request: Request, call_next):
        inicio = time.time()
        info = self._obtener_info_request(request)
        body_request = self._obtener_body_request(info['path'], info['metodo'])
        
        self._log_request(info, body_request)
        
        try:
            logger.debug(f"Llamando a call_next para {info['metodo']} {info['path']}")
            response = await call_next(request)
            logger.debug(f"Response recibido para {info['metodo']} {info['path']}, status: {response.status_code}")
            
            tiempo_respuesta = (time.time() - inicio) * 1000
            body_response = self._obtener_body_response(info['path'], response)
            
            self._log_response(info, tiempo_respuesta, response.status_code, body_request, body_response)
            
            return response
        except Exception as e:
            tiempo_respuesta = (time.time() - inicio) * 1000
            self._log_error(info, tiempo_respuesta, body_request, e)
            raise

