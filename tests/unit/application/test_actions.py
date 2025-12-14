"""Tests para acciones de aplicación."""
import pytest
from app.application.acciones.orden import CrearOrden
from app.application.acciones.estados import EstablecerEstadoDiagnosticado
from app.application.acciones.autorizacion import Autorizar
from app.application.acciones.servicios import AgregarServicio


class TestCrearOrdenAction:
    """Tests para acción CrearOrden."""
    
    def test_crear_orden_action_existe(self):
        """Test que CrearOrden action existe."""
        assert CrearOrden is not None


class TestEstadoDiagnosticadoAction:
    """Tests para acción EstablecerEstadoDiagnosticado."""
    
    def test_estado_diagnosticado_existe(self):
        """Test que EstablecerEstadoDiagnosticado existe."""
        assert EstablecerEstadoDiagnosticado is not None


class TestAutorizarAction:
    """Tests para acción Autorizar."""
    
    def test_autorizar_existe(self):
        """Test que Autorizar existe."""
        assert Autorizar is not None


class TestAgregarServicioAction:
    """Tests para acción AgregarServicio."""
    
    def test_agregar_servicio_existe(self):
        """Test que AgregarServicio existe."""
        assert AgregarServicio is not None
