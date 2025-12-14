"""Tests extendidos para app.domain.models.order.py."""
import pytest
from decimal import Decimal
from datetime import datetime
from app.domain.models.order import Orden
from app.domain.models.service import Servicio
from app.domain.enums.order_status import EstadoOrden


class TestOrderModel:
    """Tests para el modelo Orden."""
    
    def test_order_creation(self):
        """Test creación de Orden."""
        orden = Orden(
            id_orden="ORD-001",
            cliente="Juan",
            vehiculo="Auto",
            fecha_creacion=datetime.now()
        )
        
        assert orden.id_orden == "ORD-001"
        assert orden.cliente == "Juan"
        assert orden.vehiculo == "Auto"
    
    def test_order_with_all_fields(self):
        """Test Orden con todos los campos."""
        orden = Orden(
            id_orden="ORD-001",
            cliente="Juan",
            vehiculo="Auto",
            fecha_creacion=datetime.now()
        )
        orden.monto_autorizado = Decimal("1000.00")
        orden.version_autorizacion = 1
        orden.total_real = Decimal("0.00")
        
        assert orden.id_orden == "ORD-001"
        assert orden.estado == EstadoOrden.CREATED
        assert orden.monto_autorizado == Decimal("1000.00")
        assert orden.version_autorizacion == 1
    
    def test_order_add_service(self):
        """Test agregar servicio a Orden."""
        orden = Orden(id_orden="ORD-001", cliente="Juan", vehiculo="Auto", fecha_creacion=datetime.now())
        servicio = Servicio(descripcion="Cambio de aceite", costo_mano_obra_estimado=Decimal("500.00"))
        
        orden.agregar_servicio(servicio)
        assert len(orden.servicios) == 1
    
    def test_order_services_list(self):
        """Test lista de servicios."""
        orden = Orden(id_orden="ORD-001", cliente="Juan", vehiculo="Auto", fecha_creacion=datetime.now())
        
        assert isinstance(orden.servicios, list)
        assert len(orden.servicios) == 0
    
    def test_order_status_property(self):
        """Test propiedad status."""
        orden = Orden(id_orden="ORD-001", cliente="Juan", vehiculo="Auto", fecha_creacion=datetime.now())
        
        assert orden.estado == EstadoOrden.CREATED
    
    def test_order_authorized_amount_property(self):
        """Test propiedad monto_autorizado."""
        orden = Orden(
            id_orden="ORD-001",
            cliente="Juan",
            vehiculo="Auto",
            fecha_creacion=datetime.now()
        )
        orden.monto_autorizado = Decimal("1000.00")
        
        assert orden.monto_autorizado == Decimal("1000.00")
    
    def test_order_total_real_property(self):
        """Test propiedad total_real."""
        orden = Orden(
            id_orden="ORD-001",
            cliente="Juan",
            vehiculo="Auto",
            fecha_creacion=datetime.now()
        )
        orden.total_real = Decimal("950.00")
        
        assert orden.total_real == Decimal("950.00")
    
    def test_order_authorization_version_property(self):
        """Test propiedad version_autorizacion."""
        orden = Orden(
            id_orden="ORD-001",
            cliente="Juan",
            vehiculo="Auto",
            fecha_creacion=datetime.now()
        )
        orden.version_autorizacion = 2
        
        assert orden.version_autorizacion == 2
    
    def test_order_events_list(self):
        """Test lista de eventos."""
        orden = Orden(id_orden="ORD-001", cliente="Juan", vehiculo="Auto", fecha_creacion=datetime.now())
        
        assert isinstance(orden.eventos, list)


class TestServicioModel:
    """Tests para el modelo Servicio."""
    
    def test_servicio_creation(self):
        """Test creación de Servicio."""
        servicio = Servicio(
            descripcion="Cambio de aceite",
            costo_mano_obra_estimado=Decimal("500.00")
        )
        
        assert servicio.descripcion == "Cambio de aceite"
        assert servicio.costo_mano_obra_estimado == Decimal("500.00")
    
    def test_servicio_with_real_cost(self):
        """Test Servicio con costo real asignado después."""
        servicio = Servicio(
            descripcion="Servicio",
            costo_mano_obra_estimado=Decimal("500.00")
        )
        # Asignar costo_real después
        servicio.costo_real = Decimal("600.00")
        
        assert servicio.costo_mano_obra_estimado == Decimal("500.00")
        assert servicio.costo_real == Decimal("600.00")
    
    def test_servicio_with_components(self):
        """Test Servicio con componentes."""
        servicio = Servicio(
            descripcion="Reparación",
            costo_mano_obra_estimado=Decimal("500.00")
        )
        
        # Verificar que tiene componentes
        assert hasattr(servicio, 'componentes')
        assert isinstance(servicio.componentes, list)
    
    def test_servicio_completado_property(self):
        """Test propiedad completado."""
        servicio = Servicio(
            descripcion="Servicio",
            costo_mano_obra_estimado=Decimal("500.00")
        )
        
        assert hasattr(servicio, 'completado')
        assert servicio.completado is False


class TestOrderIntegration:
    """Tests de integración para Orden y Servicio."""
    
    def test_order_with_multiple_services(self):
        """Test Orden con múltiples Servicios."""
        orden = Orden(id_orden="ORD-001", cliente="Juan", vehiculo="Auto", fecha_creacion=datetime.now())
        
        servicio1 = Servicio(descripcion="Service 1", costo_mano_obra_estimado=Decimal("500.00"))
        servicio2 = Servicio(descripcion="Service 2", costo_mano_obra_estimado=Decimal("300.00"))
        
        orden.agregar_servicio(servicio1)
        orden.agregar_servicio(servicio2)
        
        assert len(orden.servicios) == 2
    
    def test_order_estado_diagnosticado(self):
        """Test cambiar estado a diagnosticado."""
        orden = Orden(id_orden="ORD-001", cliente="Juan", vehiculo="Auto", fecha_creacion=datetime.now())
        
        # Agregar al menos un servicio
        servicio = Servicio(descripcion="Diagnóstico", costo_mano_obra_estimado=Decimal("100.00"))
        orden.agregar_servicio(servicio)
        
        # Cambiar a diagnosticado
        orden.establecer_estado_diagnosticado()
        
        assert orden.estado == EstadoOrden.DIAGNOSED
