import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from sqlalchemy.exc import SQLAlchemyError
import json

load_dotenv()

from ...infrastructure.logging_config import configurar_logging, obtener_logger
from ...infrastructure.db import crear_engine_bd
from ...domain.exceptions import ErrorDominio
from .routes import router
from .middleware import LoggingMiddleware


logger = obtener_logger("app.drivers.api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configurar_logging()
    logger.info("Iniciando aplicación GestionTalleres API")
    
    try:
        crear_engine_bd()
        logger.info("Conexión a base de datos establecida")
    except Exception as e:
        logger.error(f"Error al conectar a base de datos: {str(e)}", exc_info=True)
    
    yield
    
    logger.info("Cerrando aplicación GestionTalleres API")


app = FastAPI(
    title="GestionTalleres API",
    version="1.0.0",
    description="""
    API para gestionar el ciclo de vida de órdenes de reparación en una red de talleres automotrices.
    
    ## Funcionalidades
    
    * Crear órdenes de reparación
    * Agregar servicios y componentes
    * Controlar estados de las órdenes
    * Registrar costos estimados y reales
    * Manejar autorizaciones y reautorizaciones
    * Mantener trazabilidad del proceso
    
    ## Estados de Orden
    
    * **CREATED**: Orden creada
    * **DIAGNOSED**: Diagnóstico realizado
    * **AUTHORIZED**: Autorizada para reparación
    * **IN_PROGRESS**: En proceso de reparación
    * **WAITING_FOR_APPROVAL**: Esperando reautorización
    * **COMPLETED**: Reparación completada
    * **DELIVERED**: Entregada al cliente
    * **CANCELLED**: Cancelada
    """,
    contact={
        "name": "GestionTalleres",
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
    logger.info(f"Exception handler de validación llamado para {request.method} {request.url.path}")
    
    body_json = {}
    try:
        if hasattr(request.state, "body_captured"):
            body_json = request.state.body_captured
            logger.debug("Body capturado desde request.state")
        else:
            logger.debug("Intentando leer body desde request")
            try:
                body = await request.body()
                body_str = body.decode("utf-8") if body else "{}"
                try:
                    body_json = json.loads(body_str)
                except Exception:
                    body_json = {"raw": body_str[:1000]}
            except Exception as e:
                logger.debug(f"No se pudo leer body: {str(e)}")
                body_json = {}
    except Exception as e:
        logger.debug(f"Error al obtener body: {str(e)}")
        body_json = {}
    
    error_detail = exc.errors()
    error_response = {"detail": error_detail}
    if body_json:
        error_response["body"] = body_json
    
    logger.error(
        f"Error de validación en {request.method} {request.url.path}: {len(error_detail)} errores de validación",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "request_body": body_json,
            "validation_errors": error_detail,
            "error_type": "RequestValidationError",
            "response_body": error_response
        },
        exc_info=True
    )
    
    logger.info(f"Retornando respuesta 422 para {request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


@app.exception_handler(ErrorDominio)
async def error_dominio_handler(request: Request, exc: ErrorDominio):
    logger.error(
        f"Error de dominio: {exc.mensaje}",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "codigo": exc.codigo.value,
            "mensaje": exc.mensaje,
            "error_type": "ErrorDominio"
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.mensaje, "code": exc.codigo.value}
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.error(
        f"Error de validación: {str(exc)}",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "error": str(exc),
            "error_type": "ValueError"
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(KeyError)
async def key_error_handler(request: Request, exc: KeyError):
    logger.error(
        f"Clave no encontrada: {str(exc)}",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "error": str(exc),
            "error_type": "KeyError"
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Clave requerida no encontrada: {str(exc)}"}
    )


@app.exception_handler(ResponseValidationError)
async def response_validation_error_handler(request: Request, exc: ResponseValidationError):
    logger.error(
        f"Error de validación de respuesta en {request.method} {request.url.path}: {str(exc)}",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "error": str(exc),
            "error_type": "ResponseValidationError",
            "body": exc.body if hasattr(exc, "body") else None
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Error de validación de respuesta: {str(exc)}"}
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Error de base de datos: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Error en la base de datos. Intente más tarde."}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    try:
        body = await request.body()
        body_str = body.decode("utf-8") if body else "{}"
        try:
            body_json = json.loads(body_str)
        except (json.JSONDecodeError, UnicodeDecodeError):
            body_json = {"raw": body_str[:1000]}
    except (UnicodeDecodeError, AttributeError):
        body_json = {}
    
    logger.error(
        f"Error inesperado: {str(exc)}",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "request_body": body_json,
            "error": str(exc),
            "error_type": type(exc).__name__
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"}
    )



