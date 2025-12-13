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
    async def dispatch(self, request: Request, call_next):
        inicio = time.time()
        metodo = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        client_ip = request.client.host if request.client else "unknown"
        
        body_request = {}
        if path == "/commands" and metodo == "POST":
            body_request = {"nota": "Body será capturado en endpoint o exception handler"}
        
        logger.info(
            f"Request {metodo} {path}",
            extra={
                "method": metodo,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
                "request_body": body_request
            }
        )
        
        try:
            logger.debug(f"Llamando a call_next para {metodo} {path}")
            response = await call_next(request)
            logger.debug(f"Response recibido para {metodo} {path}, status: {response.status_code}")
            tiempo_respuesta = (time.time() - inicio) * 1000
            
            body_response = {}
            if path == "/commands":
                try:
                    if isinstance(response, JSONResponse):
                        if hasattr(response, "body") and response.body:
                            try:
                                body_response = json.loads(response.body.decode("utf-8"))
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                body_response = {"raw_body": response.body.decode("utf-8", errors="replace")[:1000]}
                        elif hasattr(response, "render"):
                            try:
                                rendered = response.render({})
                                if rendered:
                                    try:
                                        body_response = json.loads(rendered.decode("utf-8"))
                                    except (json.JSONDecodeError, UnicodeDecodeError):
                                        body_response = {"raw": str(rendered)[:1000]}
                            except Exception:
                                if hasattr(response, "_content"):
                                    try:
                                        body_response = json.loads(response._content.decode("utf-8"))
                                    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                                        pass
                except Exception as e:
                    body_response = {"error_captura": str(e)}
            
            if response.status_code >= 400:
                logger.error(
                    f"Request {metodo} {path} procesado en {tiempo_respuesta:.2f}ms, status {response.status_code}",
                    extra={
                        "method": metodo,
                        "path": path,
                        "status_code": response.status_code,
                        "response_time_ms": tiempo_respuesta,
                        "client_ip": client_ip,
                        "request_body": body_request,
                        "response_body": body_response
                    }
                )
            else:
                logger.info(
                    f"Request {metodo} {path} procesado en {tiempo_respuesta:.2f}ms, status {response.status_code}",
                    extra={
                        "method": metodo,
                        "path": path,
                        "status_code": response.status_code,
                        "response_time_ms": tiempo_respuesta,
                        "client_ip": client_ip,
                        "request_body": body_request,
                        "response_body": body_response
                    }
                )
            
            return response
        except Exception as e:
            tiempo_respuesta = (time.time() - inicio) * 1000
            logger.error(
                f"Error al procesar request {metodo} {path}: {str(e)}",
                extra={
                    "method": metodo,
                    "path": path,
                    "response_time_ms": tiempo_respuesta,
                    "client_ip": client_ip,
                    "request_body": body_request,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            raise

