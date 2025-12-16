from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from app.drivers.api.dependencies import (
    obtener_action_service,
    obtener_unidad_trabajo,
    obtener_repositorio,
    obtener_repositorio_cliente,
    obtener_repositorio_vehiculo
)


def test_obtener_repositorio():
    sesion = MagicMock(spec=Session)
    unidad = obtener_unidad_trabajo(sesion)
    repo = obtener_repositorio(unidad)
    assert repo is not None


def test_obtener_repositorio_cliente():
    sesion = MagicMock(spec=Session)
    repo = obtener_repositorio_cliente(sesion)
    assert repo is not None


def test_obtener_repositorio_vehiculo():
    sesion = MagicMock(spec=Session)
    repo = obtener_repositorio_vehiculo(sesion)
    assert repo is not None


def test_obtener_action_service():
    sesion = MagicMock(spec=Session)
    unidad = obtener_unidad_trabajo(sesion)
    repo = obtener_repositorio(unidad)
    audit_mock = Mock()
    
    service = obtener_action_service(repo, audit_mock)
    assert service is not None

