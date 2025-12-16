"""Tests para UnidadTrabajoSQL - Patrón Unit of Work."""

import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session

from app.infrastructure.repositories.unidad_trabajo import UnidadTrabajoSQL
from app.infrastructure.repositories.repositorio_orden import RepositorioOrden
from app.infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
from app.infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
from app.infrastructure.repositories.repositorio_servicio import RepositorioServicioSQL
from app.infrastructure.repositories.repositorio_evento import RepositorioEventoSQL


@pytest.fixture
def sesion_mock():
    """Crea una sesión mock para tests."""
    return Mock(spec=Session)


def test_unidad_trabajo_crea_repositorios(sesion_mock):
    """Test que UnidadTrabajoSQL crea repositorios correctamente."""
    unidad = UnidadTrabajoSQL(sesion_mock)
    
    repo_orden = unidad.obtener_repositorio_orden()
    repo_cliente = unidad.obtener_repositorio_cliente()
    repo_vehiculo = unidad.obtener_repositorio_vehiculo()
    repo_servicio = unidad.obtener_repositorio_servicio()
    repo_evento = unidad.obtener_repositorio_evento()
    
    assert isinstance(repo_orden, RepositorioOrden)
    assert isinstance(repo_cliente, RepositorioClienteSQL)
    assert isinstance(repo_vehiculo, RepositorioVehiculoSQL)
    assert isinstance(repo_servicio, RepositorioServicioSQL)
    assert isinstance(repo_evento, RepositorioEventoSQL)


def test_unidad_trabajo_cachea_repositorios(sesion_mock):
    """Test que UnidadTrabajoSQL cachea repositorios (misma instancia)."""
    unidad = UnidadTrabajoSQL(sesion_mock)
    
    repo1 = unidad.obtener_repositorio_cliente()
    repo2 = unidad.obtener_repositorio_cliente()
    
    assert repo1 is repo2
    assert id(repo1) == id(repo2)


def test_unidad_trabajo_repositorios_comparten_sesion(sesion_mock):
    """Test que todos los repositorios comparten la misma sesión."""
    unidad = UnidadTrabajoSQL(sesion_mock)
    
    repo_orden = unidad.obtener_repositorio_orden()
    repo_cliente = unidad.obtener_repositorio_cliente()
    repo_vehiculo = unidad.obtener_repositorio_vehiculo()
    repo_servicio = unidad.obtener_repositorio_servicio()
    repo_evento = unidad.obtener_repositorio_evento()
    
    assert repo_orden.sesion == sesion_mock
    assert repo_cliente.sesion == sesion_mock
    assert repo_vehiculo.sesion == sesion_mock
    assert repo_servicio.sesion == sesion_mock
    assert repo_evento.sesion == sesion_mock


def test_unidad_trabajo_repositorio_orden_recibe_unidad_trabajo(sesion_mock):
    """Test que RepositorioOrden recibe la UnidadTrabajo correctamente."""
    unidad = UnidadTrabajoSQL(sesion_mock)
    
    repo_orden = unidad.obtener_repositorio_orden()
    
    assert repo_orden.unidad_trabajo == unidad


def test_unidad_trabajo_lazy_initialization(sesion_mock):
    """Test que los repositorios se crean bajo demanda (lazy)."""
    unidad = UnidadTrabajoSQL(sesion_mock)
    
    assert unidad._repo_orden is None
    assert unidad._repo_cliente is None
    
    repo_orden = unidad.obtener_repositorio_orden()
    
    assert unidad._repo_orden is not None
    assert unidad._repo_orden == repo_orden


def test_unidad_trabajo_multiple_llamadas_misma_instancia(sesion_mock):
    """Test que múltiples llamadas retornan la misma instancia."""
    unidad = UnidadTrabajoSQL(sesion_mock)
    
    repo1 = unidad.obtener_repositorio_servicio()
    repo2 = unidad.obtener_repositorio_servicio()
    repo3 = unidad.obtener_repositorio_servicio()
    
    assert repo1 is repo2
    assert repo2 is repo3
    assert repo1 is repo3

