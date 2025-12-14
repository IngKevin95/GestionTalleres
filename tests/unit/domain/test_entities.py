"""Tests para entidades de dominio (Orden, Servicio, Componente, etc)."""
import pytest
from decimal import Decimal
from datetime import datetime
from app.domain.entidades.order import Orden
from app.domain.entidades.cliente import Cliente
from app.domain.entidades.vehiculo import Vehiculo
from app.domain.entidades.service import Servicio
from app.domain.entidades.component import Componente
from app.domain.entidades.event import Evento
from app.domain.enums.order_status import EstadoOrden


class TestOrdenEntity:
    """Tests para la entidad Orden."""
    
    def test_crear_orden_basica(self):
        """Test crear una orden básica."""
        
        orden = Orden(
            id_orden="ORD-001",
            cliente="Juan Pérez",
            vehiculo="Toyota Corolla",
            fecha_creacion=datetime.now()
        )
        
        assert orden.id_orden == "ORD-001"
        assert orden.cliente == "Juan Pérez"
        assert orden.vehiculo == "Toyota Corolla"
    
    def test_orden_estado_inicial(self):
        """Test que orden inicia en estado CREATED."""
        orden = Orden(
            id_orden="ORD-001",
            cliente="Test",
            vehiculo="Test",
            fecha_creacion=datetime.now()
        )
        assert orden.estado == EstadoOrden.CREATED
    
    def test_orden_version_inicial(self):
        """Test que version de autorización inicia en 0."""
        orden = Orden(
            id_orden="ORD-001",
            cliente="Test",
            vehiculo="Test",
            fecha_creacion=datetime.now()
        )
        assert orden.version_autorizacion == 0


class TestClienteEntity:
    """Tests para la entidad Cliente."""
    
    def test_crear_cliente(self):
        """Test crear cliente."""
        cliente = Cliente(nombre="Juan Pérez", id_cliente="C001")
        assert cliente.id_cliente == "C001"
        assert cliente.nombre == "Juan Pérez"


class TestVehiculoEntity:
    """Tests para la entidad Vehiculo."""
    
    def test_crear_vehiculo(self):
        """Test crear vehiculo."""
        vehiculo = Vehiculo(descripcion="Toyota Corolla 2020", id_cliente="C001", id_vehiculo="V001")
        assert vehiculo.id_vehiculo == "V001"
        assert vehiculo.descripcion == "Toyota Corolla 2020"


class TestServicioEntity:
    """Tests para la entidad Servicio."""
    
    def test_crear_servicio(self):
        """Test crear servicio."""
        servicio = Servicio(
            descripcion="Cambio de aceite",
            costo_mano_obra_estimado=Decimal("50000")
        )
        assert servicio.descripcion == "Cambio de aceite"
        assert servicio.costo_mano_obra_estimado == Decimal("50000")


class TestComponenteEntity:
    """Tests para la entidad Componente."""
    
    def test_crear_componente(self):
        """Test crear componente."""
        componente = Componente(
            descripcion="Aceite sintético",
            costo_estimado=Decimal("80000")
        )
        assert componente.descripcion == "Aceite sintético"
        assert componente.costo_estimado == Decimal("80000")


class TestEventoEntity:
    """Tests para la entidad Evento."""
    
    def test_crear_evento(self):
        """Test crear evento."""
        from datetime import datetime
        evento = Evento(
            tipo="ORDEN_CREADA",
            timestamp=datetime.now(),
            metadatos={"order_id": "ORD-001"}
        )
        assert evento.tipo == "ORDEN_CREADA"
        assert evento.metadatos["order_id"] == "ORD-001"
