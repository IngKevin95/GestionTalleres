from datetime import datetime, timezone
from app.infrastructure.models.orden_model import OrdenModel
from app.infrastructure.models.cliente_model import ClienteModel
from app.infrastructure.models.vehiculo_model import VehiculoModel
from app.infrastructure.models.servicio_model import ServicioModel
from app.infrastructure.models.componente_model import ComponenteModel
from app.infrastructure.models.evento_model import EventoModel


def test_orden_model():
    modelo = OrdenModel(
        id_orden="ORD-001",
        id_cliente="CLI-001",
        id_vehiculo="VEH-001",
        estado="CREATED",
        monto_autorizado="1000.00",
        version_autorizacion=1,
        total_real="0.00",
        fecha_creacion=datetime.now(timezone.utc)
    )
    assert modelo.id_orden == "ORD-001"
    assert modelo.estado == "CREATED"
    assert modelo.version_autorizacion == 1


def test_cliente_model():
    modelo = ClienteModel(
        id_cliente="CLI-001",
        nombre="Juan Pérez"
    )
    assert modelo.id_cliente == "CLI-001"
    assert modelo.nombre == "Juan Pérez"


def test_vehiculo_model():
    modelo = VehiculoModel(
        id_vehiculo="VEH-001",
        id_cliente="CLI-001",
        descripcion="ABC-123",
        marca="Toyota",
        modelo="Corolla",
        anio=2020
    )
    assert modelo.id_vehiculo == "VEH-001"
    assert modelo.descripcion == "ABC-123"
    assert modelo.marca == "Toyota"


def test_servicio_model():
    modelo = ServicioModel(
        id_servicio="SERV-001",
        id_orden="ORD-001",
        descripcion="Cambio de aceite",
        costo_mano_obra_estimado="500.00",
        costo_real="600.00",
        completado=True
    )
    assert modelo.id_servicio == "SERV-001"
    assert modelo.descripcion == "Cambio de aceite"
    assert modelo.completado is True


def test_componente_model():
    modelo = ComponenteModel(
        id_componente="COMP-001",
        id_servicio="SERV-001",
        descripcion="Aceite",
        costo_estimado="300.00",
        costo_real="350.00"
    )
    assert modelo.id_componente == "COMP-001"
    assert modelo.descripcion == "Aceite"
    assert modelo.costo_estimado == "300.00"


def test_evento_model():
    import json
    modelo = EventoModel(
        id_orden="ORD-001",
        tipo="CREATED",
        timestamp=datetime.now(timezone.utc),
        metadatos_json=json.dumps({"key": "value"})
    )
    assert modelo.tipo == "CREATED"
    assert modelo.id_orden == "ORD-001"
    assert modelo.metadatos_json is not None

