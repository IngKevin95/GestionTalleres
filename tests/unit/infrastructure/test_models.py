"""Tests para modelos SQLAlchemy de infraestructura."""
import pytest
from datetime import datetime
from app.infrastructure.models.orden_model import OrdenModel
from app.infrastructure.models.cliente_model import ClienteModel
from app.infrastructure.models.vehiculo_model import VehiculoModel
from app.infrastructure.models.servicio_model import ServicioModel
from app.infrastructure.models.componente_model import ComponenteModel
from app.infrastructure.models.evento_model import EventoModel
from app.infrastructure.models.base import Base, fecha_creacion_default


class TestBaseModel:
    """Tests para Base de SQLAlchemy."""
    
    def test_base_import(self):
        """Test importar Base."""
        assert Base is not None
    
    def test_fecha_creacion_default(self):
        """Test fecha_creacion_default devuelve datetime."""
        fecha = fecha_creacion_default()
        assert isinstance(fecha, datetime)


class TestOrdenModel:
    """Tests para modelo OrdenModel."""
    
    def test_orden_model_import(self):
        """Test importar OrdenModel."""
        assert OrdenModel is not None


class TestClienteModel:
    """Tests para modelo ClienteModel."""
    
    def test_cliente_model_import(self):
        """Test importar ClienteModel."""
        assert ClienteModel is not None


class TestVehiculoModel:
    """Tests para modelo VehiculoModel."""
    
    def test_vehiculo_model_import(self):
        """Test importar VehiculoModel."""
        from app.infrastructure.models import VehiculoModel


class TestServicioModel:
    """Tests para modelo ServicioModel."""
    
    def test_servicio_model_import(self):
        """Test importar ServicioModel."""
        assert ServicioModel is not None


class TestComponenteModel:
    """Tests para modelo ComponenteModel."""
    
    def test_componente_model_import(self):
        """Test importar ComponenteModel."""
        assert ComponenteModel is not None


class TestEventoModel:
    """Tests para modelo EventoModel."""
    
    def test_evento_model_import(self):
        """Test importar EventoModel."""
        assert EventoModel is not None
