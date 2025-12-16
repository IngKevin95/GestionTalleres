from unittest.mock import Mock, patch
from app.drivers.api.dependencies import (
    obtener_sesion_db,
    obtener_unidad_trabajo,
    obtener_repositorio,
    obtener_auditoria,
    obtener_action_service,
    obtener_repositorio_cliente,
    obtener_repositorio_vehiculo
)
from app.infrastructure.repositories import RepositorioOrden, RepositorioClienteSQL, RepositorioVehiculoSQL, UnidadTrabajoSQL
from app.infrastructure.logger import AlmacenEventosLogger
from app.application.action_service import ActionService


def test_obtener_sesion_db_cierra_sesion():
    sesion_mock = Mock()
    sesion_mock.close = Mock()
    
    with patch('app.drivers.api.dependencies.obtener_sesion', return_value=sesion_mock):
        gen = obtener_sesion_db()
        sesion = next(gen)
        
        assert sesion == sesion_mock
        
        try:
            next(gen)
        except StopIteration:
            pass
        
        sesion_mock.close.assert_called_once()


def test_obtener_unidad_trabajo():
    sesion_mock = Mock()
    
    unidad = obtener_unidad_trabajo(sesion_mock)
    
    assert isinstance(unidad, UnidadTrabajoSQL)
    assert unidad.sesion == sesion_mock


def test_obtener_repositorio():
    sesion_mock = Mock()
    
    unidad = obtener_unidad_trabajo(sesion_mock)
    repo = obtener_repositorio(unidad)
    
    assert isinstance(repo, RepositorioOrden)
    assert repo.sesion == sesion_mock


def test_obtener_auditoria():
    auditoria = obtener_auditoria()
    
    assert isinstance(auditoria, AlmacenEventosLogger)


def test_obtener_action_service():
    sesion_mock = Mock()
    unidad = UnidadTrabajoSQL(sesion_mock)
    repo = unidad.obtener_repositorio_orden()
    auditoria = AlmacenEventosLogger()
    
    service = obtener_action_service(repo, auditoria)
    
    assert isinstance(service, ActionService)
    assert service.repo == repo
    assert service.auditoria == auditoria


def test_obtener_repositorio_cliente():
    sesion_mock = Mock()
    
    repo = obtener_repositorio_cliente(sesion_mock)
    
    assert isinstance(repo, RepositorioClienteSQL)
    assert repo.sesion == sesion_mock


def test_obtener_repositorio_vehiculo():
    sesion_mock = Mock()
    
    repo = obtener_repositorio_vehiculo(sesion_mock)
    
    assert isinstance(repo, RepositorioVehiculoSQL)
    assert repo.sesion == sesion_mock
