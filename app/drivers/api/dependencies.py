from fastapi import Depends
from sqlalchemy.orm import Session

from ...infrastructure.db import obtener_sesion
from ...infrastructure.repositories import RepositorioOrden, RepositorioClienteSQL, RepositorioVehiculoSQL, UnidadTrabajoSQL
from ...infrastructure.logger import AlmacenEventosLogger

from ...application.action_service import ActionService


def obtener_sesion_db() -> Session:
    sesion = obtener_sesion()
    try:
        yield sesion
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

