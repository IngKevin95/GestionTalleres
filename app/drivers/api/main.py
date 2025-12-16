import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from sqlalchemy.exc import SQLAlchemyError
import json

# Solo cargar .env si no estamos en Docker (donde las variables ya están configuradas)
if not os.path.exists("/.dockerenv"):
    load_dotenv()

from ...infrastructure.logging_config import configurar_logging, obtener_logger, request_id_var, obtener_contexto_log
from ...infrastructure.db import crear_engine_bd
from ...domain.exceptions import ErrorDominio
from .routes import router
from .middleware import LoggingMiddleware


logger = obtener_logger("app.drivers.api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configurar_logging()
    logger.info("Iniciando aplicación")
    
    try:
        crear_engine_bd()
    except Exception as e:
        logger.error(f"Error BD: {str(e)}", exc_info=True)
    
    yield
    
    logger.info("Cerrando aplicación")


app = FastAPI(
    title="GestionTalleres API",
    version="1.0.0",
    description="Sistema de gestión de órdenes de reparación en talleres automotrices",
    contact={
        "name": "GestionTalleres Support",
        "email": "support@gestiontalleres.com"
    },
    lifespan=lifespan
)

origins = os.getenv("CORS_ORIGINS", "*").split(",")
if origins == ["*"]:
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = [origin.strip() for origin in origins]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = request_id_var.get(None)
    ctx = obtener_contexto_log()
    
    body_json = {}
    try:
        body = await request.body()
        if body:
            try:
                body_json = json.loads(body.decode("utf-8"))
            except:
                body_json = {"raw": body.decode("utf-8")[:500]}
    except:
        pass
    
    error_detail = exc.errors()
    mensajes = []
    for err in error_detail:
        campo = " -> ".join(str(loc) for loc in err.get("loc", []))
        tipo = err.get("type", "unknown")
        msg = err.get("msg", "Error de validación")
        
        if tipo == "string_too_short":
            mensajes.append(f"Campo '{campo}' es requerido y no puede estar vacío")
        elif tipo == "missing":
            mensajes.append(f"Campo '{campo}' es requerido")
        elif tipo == "value_error":
            mensajes.append(f"Campo '{campo}': {msg}")
        else:
            mensajes.append(f"Campo '{campo}': {msg}")
    
    logger.error(
        f"Validación fallida {request.method} {request.url.path}: {len(error_detail)} errores",
        extra={**ctx, "path": request.url.path, "method": request.method, "validation_errors": error_detail}
    )
    
    response_content = {"detail": mensajes, "errors": error_detail}
    if req_id:
        response_content["request_id"] = req_id
    
    response = JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_content
    )
    if req_id:
        response.headers["X-Request-ID"] = req_id
    return response


@app.exception_handler(ErrorDominio)
async def error_dominio_handler(request: Request, exc: ErrorDominio):
    req_id = request_id_var.get(None)
    ctx = obtener_contexto_log()
    ctx.update(exc.contexto)
    
    logger.error(
        f"Error dominio: {exc.mensaje}",
        extra={**ctx, "error_code": exc.codigo.value, "path": request.url.path, "method": request.method},
        exc_info=True
    )
    
    response_content = {"detail": exc.mensaje, "code": exc.codigo.value}
    if req_id:
        response_content["request_id"] = req_id
    if exc.contexto:
        response_content["context"] = exc.contexto
    
    response = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=response_content
    )
    if req_id:
        response.headers["X-Request-ID"] = req_id
    return response


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    req_id = request_id_var.get(None)
    ctx = obtener_contexto_log()
    
    logger.error(
        f"ValueError: {str(exc)}",
        extra={**ctx, "path": request.url.path, "method": request.method},
        exc_info=True
    )
    
    response_content = {"detail": str(exc)}
    if req_id:
        response_content["request_id"] = req_id
    
    response = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=response_content
    )
    if req_id:
        response.headers["X-Request-ID"] = req_id
    return response


@app.exception_handler(KeyError)
async def key_error_handler(request: Request, exc: KeyError):
    req_id = request_id_var.get(None)
    ctx = obtener_contexto_log()
    
    logger.error(
        f"KeyError: {str(exc)}",
        extra={**ctx, "path": request.url.path, "method": request.method, "missing_key": str(exc)}
    )
    
    response_content = {"detail": f"Clave requerida no encontrada: {str(exc)}"}
    if req_id:
        response_content["request_id"] = req_id
    
    response = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=response_content
    )
    if req_id:
        response.headers["X-Request-ID"] = req_id
    return response


@app.exception_handler(ResponseValidationError)
async def response_validation_error_handler(request: Request, exc: ResponseValidationError):
    req_id = request_id_var.get(None)
    ctx = obtener_contexto_log()
    
    logger.error(
        f"Error validación respuesta: {str(exc)}",
        extra={**ctx, "path": request.url.path, "method": request.method},
        exc_info=True
    )
    
    response_content = {"detail": f"Error de validación de respuesta: {str(exc)}"}
    if req_id:
        response_content["request_id"] = req_id
    
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content
    )
    if req_id:
        response.headers["X-Request-ID"] = req_id
    return response


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    req_id = request_id_var.get(None)
    ctx = obtener_contexto_log()
    msg = str(exc)
    
    logger.error(
        f"Error BD: {msg}",
        extra={**ctx, "path": request.url.path, "method": request.method, "error_type": "SQLAlchemyError"},
        exc_info=True
    )
    
    detail = "Error en la base de datos. Intente más tarde."
    if "does not exist" in msg or "no existe" in msg.lower():
        detail = f"Error estructura BD: {msg}"
    elif "connection" in msg.lower():
        detail = "Error de conexión a la BD"
    
    response_content = {"detail": detail}
    if req_id:
        response_content["request_id"] = req_id
    
    response = JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=response_content
    )
    if req_id:
        response.headers["X-Request-ID"] = req_id
    return response


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    req_id = request_id_var.get(None)
    ctx = obtener_contexto_log()
    
    logger.error(
        f"Error inesperado: {str(exc)}",
        extra={**ctx, "path": request.url.path, "method": request.method, "error_type": type(exc).__name__},
        exc_info=True
    )
    
    response_content = {"detail": "Error interno del servidor"}
    if req_id:
        response_content["request_id"] = req_id
    
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content
    )
    if req_id:
        response.headers["X-Request-ID"] = req_id
    return response



