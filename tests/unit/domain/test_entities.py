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


def test_crear_orden_basica():
    orden = Orden(
        id_orden="ORD-001",
        cliente="Juan Pérez",
        vehiculo="Toyota Corolla",
        fecha_creacion=datetime.now()
    )
    
    assert orden.id_orden == "ORD-001"
    assert orden.cliente == "Juan Pérez"
    assert orden.vehiculo == "Toyota Corolla"


def test_orden_estado_inicial():
    orden = Orden(
        id_orden="ORD-001",
        cliente="Test",
        vehiculo="Test",
        fecha_creacion=datetime.now()
    )
    assert orden.estado == EstadoOrden.CREATED


def test_orden_version_inicial():
    orden = Orden(
        id_orden="ORD-001",
        cliente="Test",
        vehiculo="Test",
        fecha_creacion=datetime.now()
    )
    assert orden.version_autorizacion == 0


def test_crear_cliente():
    cliente = Cliente(nombre="Juan Pérez", id_cliente="C001")
    assert cliente.id_cliente == "C001"
    assert cliente.nombre == "Juan Pérez"


def test_crear_vehiculo():
    vehiculo = Vehiculo(descripcion="Toyota Corolla 2020", id_cliente="C001", id_vehiculo="V001")
    assert vehiculo.id_vehiculo == "V001"
    assert vehiculo.descripcion == "Toyota Corolla 2020"


def test_crear_servicio():
    servicio = Servicio(
        descripcion="Cambio de aceite",
        costo_mano_obra_estimado=Decimal("50000")
    )
    assert servicio.descripcion == "Cambio de aceite"
    assert servicio.costo_mano_obra_estimado == Decimal("50000")


def test_crear_componente():
    componente = Componente(
        descripcion="Aceite sintético",
        costo_estimado=Decimal("80000")
    )
    assert componente.descripcion == "Aceite sintético"
    assert componente.costo_estimado == Decimal("80000")


def test_crear_evento():
    evento = Evento(
        tipo="ORDEN_CREADA",
        timestamp=datetime.now(),
        metadatos={"order_id": "ORD-001"}
    )
    assert evento.tipo == "ORDEN_CREADA"
    assert evento.metadatos["order_id"] == "ORD-001"
