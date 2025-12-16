from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ...infrastructure.db import obtener_sesion
from ...infrastructure.repositories import RepositorioOrden, RepositorioClienteSQL, RepositorioVehiculoSQL, UnidadTrabajoSQL
from ...infrastructure.logger import AlmacenEventosLogger
from ...infrastructure.logging_config import obtener_logger

from ...application.action_service import ActionService


logger = obtener_logger("app.drivers.api.dependencies")


def obtener_sesion_db() -> Session:
    """Proporciona una sesión de BD con manejo automático de transacciones."""
    sesion = obtener_sesion()
    try:
        yield sesion
        if sesion.is_active:
            try:
                sesion.commit()
            except Exception:
                sesion.rollback()
                raise
    except SQLAlchemyError as e:
        if sesion.is_active:
            sesion.rollback()
        logger.error(f"Error de BD, rollback realizado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en base de datos"
        )
    except Exception as e:
        if sesion.is_active:
            sesion.rollback()
        logger.error(f"Error inesperado, rollback realizado: {str(e)}", exc_info=True)
        raise
    finally:
        sesion.close()


def obtener_unidad_trabajo(sesion: Session = Depends(obtener_sesion_db)) -> UnidadTrabajoSQL:
    return UnidadTrabajoSQL(sesion)


def obtener_repositorio(unidad_trabajo: UnidadTrabajoSQL = Depends(obtener_unidad_trabajo)) -> RepositorioOrden:
    return unidad_trabajo.obtener_repositorio_orden()


def obtener_auditoria() -> AlmacenEventosLogger:
    return AlmacenEventosLogger()


def obtener_action_service(
    repo: RepositorioOrden = Depends(obtener_repositorio),
    auditoria: AlmacenEventosLogger = Depends(obtener_auditoria)
) -> ActionService:
    return ActionService(repo, auditoria)


def obtener_repositorio_cliente(sesion: Session = Depends(obtener_sesion_db)) -> RepositorioClienteSQL:
    return RepositorioClienteSQL(sesion)


def obtener_repositorio_vehiculo(sesion: Session = Depends(obtener_sesion_db)) -> RepositorioVehiculoSQL:
    return RepositorioVehiculoSQL(sesion)

