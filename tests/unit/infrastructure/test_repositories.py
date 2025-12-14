import pytest
from unittest.mock import Mock
from app.infrastructure.repositories.repositorio_orden import RepositorioOrden
from app.infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
from app.infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
from app.infrastructure.repositories.repositorio_servicio import RepositorioServicioSQL
from app.infrastructure.repositories.repositorio_evento import RepositorioEventoSQL


def test_repositorio_orden_es_abstracto():
    assert hasattr(RepositorioOrden, 'obtener')


def test_repositorio_cliente_init():
    sesion_mock = Mock()
    repo = RepositorioClienteSQL(sesion_mock)
    assert repo is not None


def test_repositorio_vehiculo_init():
    sesion_mock = Mock()
    RepositorioVehiculoSQL(sesion_mock)


def test_repositorio_servicio_init():
    sesion_mock = Mock()
    repo = RepositorioServicioSQL(sesion_mock)
    assert repo is not None


def test_repositorio_evento_init():
    sesion_mock = Mock()
    repo = RepositorioEventoSQL(sesion_mock)
    assert repo is not None
