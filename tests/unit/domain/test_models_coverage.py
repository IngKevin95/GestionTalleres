"""Tests para mejorar cobertura de domain models."""
import pytest
from decimal import Decimal
from datetime import datetime
from app.domain.entidades.order import Orden
from app.domain.entidades.service import Servicio
from app.domain.entidades.component import Componente
from app.domain.entidades.event import Evento


class TestOrdenModelCoverage:
    """Tests para mejorar cobertura de Orden model."""
    
    def test_orden_model_creation(self):
        """Test crear Orden."""
        orden = Orden(
            order_id="ORD-001",
            cliente="Cliente Test",
            vehiculo="Vehiculo Test",
            fecha_creacion=datetime.now()
        )
        assert orden.order_id == "ORD-001"
        assert orden.cliente == "Cliente Test"
    
    def test_orden_model_con_monto_autorizado(self):
        """Test Orden con monto autorizado."""
        orden = Orden(
            order_id="ORD-001",
            cliente="Cliente",
            vehiculo="Vehiculo",
            fecha_creacion=datetime.now()
        )
        orden.monto_autorizado = Decimal("100000")
        assert orden.monto_autorizado == Decimal("100000")
    
    def test_orden_model_con_version_autorizacion(self):
        """Test Orden con version de autorización."""
        orden = Orden(
            order_id="ORD-001",
            cliente="Cliente",
            vehiculo="Vehiculo",
            fecha_creacion=datetime.now()
        )
        orden.version_autorizacion = 2
        assert orden.version_autorizacion == 2


class TestServicioModelCoverage:
    """Tests para mejorar cobertura de Servicio model."""
    
    def test_servicio_model_creation(self):
        """Test crear Servicio."""
        servicio = Servicio(
            descripcion="Cambio de aceite",
            costo_mano_obra_estimado=Decimal("50000")
        )
        assert servicio.descripcion == "Cambio de aceite"
        assert servicio.costo_mano_obra_estimado == Decimal("50000")
    
    def test_servicio_model_con_costo_real(self):
        """Test Servicio con costo real."""
        servicio = Servicio(
            descripcion="Cambio de aceite",
            costo_mano_obra_estimado=Decimal("50000")
        )
        servicio.costo_real = Decimal("55000")
        assert servicio.costo_real == Decimal("55000")
    
    def test_servicio_model_completado(self):
        """Test Servicio marcado como completado."""
        servicio = Servicio(
            descripcion="Cambio de aceite",
            costo_mano_obra_estimado=Decimal("50000")
        )
        servicio.completado = True
        assert servicio.completado is True


class TestComponenteModelCoverage:
    """Tests para mejorar cobertura de Componente model."""
    
    def test_componente_model_creation(self):
        """Test crear Componente."""
        componente = Componente(
            descripcion="Aceite sintético",
            costo_estimado=Decimal("80000")
        )
        assert componente.descripcion == "Aceite sintético"
        assert componente.costo_estimado == Decimal("80000")
    
    def test_componente_model_con_costo_real(self):
        """Test Componente con costo real."""
        componente = Componente(
            descripcion="Aceite sintético",
            costo_estimado=Decimal("80000")
        )
        componente.costo_real = Decimal("85000")
        assert componente.costo_real == Decimal("85000")


class TestEventoModelCoverage:
    """Tests para mejorar cobertura de Evento model."""
    
    def test_evento_model_creation(self):
        """Test crear Evento."""
        evento = Evento(
            tipo="ORDEN_CREADA",
            timestamp=datetime.now()
        )
        assert evento.tipo == "ORDEN_CREADA"
    
    def test_evento_model_con_metadatos(self):
        """Test Evento con metadatos."""
        evento = Evento(
            tipo="ORDEN_CREADA",
            timestamp=datetime.now(),
            metadatos={"usuario": "admin"}
        )
        assert evento.metadatos == {"usuario": "admin"}
