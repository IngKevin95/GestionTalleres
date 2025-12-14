from unittest.mock import Mock, patch
from app.drivers.api.dependencies import (
    obtener_sesion_db,
    obtener_repositorio,
    obtener_auditoria,
    obtener_action_service,
    obtener_repositorio_cliente,
    obtener_repositorio_vehiculo
)
from app.infrastructure.repositories import RepositorioOrden, RepositorioClienteSQL, RepositorioVehiculoSQL
from app.infrastructure.logger import AlmacenEventosLogger
from app.application.action_service import ActionService


@patch('app.drivers.api.dependencies.obtener_sesion')
def test_obtener_sesion_db(mock_obtener_sesion):
    sesion_mock = Mock()
    sesion_mock.close = Mock()
    mock_obtener_sesion.return_value = sesion_mock
    
    gen = obtener_sesion_db()
    sesion = next(gen)
    
    assert sesion == sesion_mock
    
    try:
        next(gen)
    except StopIteration:
        pass
    
    sesion_mock.close.assert_called_once()


@patch('app.drivers.api.dependencies.obtener_sesion_db')
def test_obtener_repositorio(mock_sesion_db):
    sesion_mock = Mock()
    mock_sesion_db.return_value = iter([sesion_mock])
    
    repo = obtener_repositorio(sesion_mock)
    
    assert isinstance(repo, RepositorioOrden)


def test_obtener_auditoria():
    auditoria = obtener_auditoria()
    assert isinstance(auditoria, AlmacenEventosLogger)


def test_obtener_action_service():
    repo_mock = Mock(spec=RepositorioOrden)
    auditoria_mock = Mock(spec=AlmacenEventosLogger)
    
    service = obtener_action_service(repo_mock, auditoria_mock)
    
    assert isinstance(service, ActionService)


def test_obtener_repositorio_cliente():
    sesion_mock = Mock()
    
    repo = obtener_repositorio_cliente(sesion_mock)
    
    assert isinstance(repo, RepositorioClienteSQL)


def test_obtener_repositorio_vehiculo():
    sesion_mock = Mock()
    
    repo = obtener_repositorio_vehiculo(sesion_mock)
    
    assert isinstance(repo, RepositorioVehiculoSQL)

