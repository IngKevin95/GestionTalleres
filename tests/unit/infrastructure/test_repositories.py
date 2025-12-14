"""Tests para repositorios de infraestructura."""
import pytest
from unittest.mock import Mock
from app.infrastructure.repositories.repositorio_orden import RepositorioOrden
from app.infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
from app.infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
from app.infrastructure.repositories.repositorio_servicio import RepositorioServicioSQL
from app.infrastructure.repositories.repositorio_evento import RepositorioEventoSQL


class TestRepositorioOrden:
    """Tests para RepositorioOrden."""
    
    def test_repositorio_orden_import(self):
        """Test importar RepositorioOrden."""
        assert RepositorioOrden is not None
    
    def test_repositorio_orden_es_abstracto(self):
        """Test que RepositorioOrden tiene métodos abstractos."""
        assert hasattr(RepositorioOrden, 'obtener')


class TestRepositorioCliente:
    """Tests para RepositorioClienteSQL."""
    
    def test_repositorio_cliente_import(self):
        """Test importar RepositorioClienteSQL."""
        assert RepositorioClienteSQL is not None
    
    def test_repositorio_cliente_init(self):
        """Test inicializar RepositorioClienteSQL."""
        sesion_mock = Mock()
        repo = RepositorioClienteSQL(sesion_mock)
        assert repo is not None


class TestRepositorioVehiculo:
    """Tests para RepositorioVehiculoSQL."""
    
    def test_repositorio_vehiculo_init(self):
        """Test inicializar RepositorioVehiculoSQL."""
        sesion_mock = Mock()
        RepositorioVehiculoSQL(sesion_mock)


class TestRepositorioServicio:
    """Tests para RepositorioServicioSQL."""
    
    def test_repositorio_servicio_import(self):
        """Test importar RepositorioServicioSQL."""
        assert RepositorioServicioSQL is not None
    
    def test_repositorio_servicio_init(self):
        """Test inicializar RepositorioServicioSQL."""
        sesion_mock = Mock()
        repo = RepositorioServicioSQL(sesion_mock)
        assert repo is not None


class TestRepositorioEvento:
    """Tests para RepositorioEventoSQL."""
    
    def test_repositorio_evento_import(self):
        """Test importar RepositorioEventoSQL."""
        assert RepositorioEventoSQL is not None
    
    def test_repositorio_evento_init(self):
        """Test inicializar RepositorioEventoSQL."""
        sesion_mock = Mock()
        repo = RepositorioEventoSQL(sesion_mock)
        assert repo is not None
