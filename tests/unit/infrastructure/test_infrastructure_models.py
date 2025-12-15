from datetime import datetime, timezone
from app.infrastructure.models.orden_model import OrdenModel
from app.infrastructure.models.cliente_model import ClienteModel
from app.infrastructure.models.vehiculo_model import VehiculoModel
from app.infrastructure.models.servicio_model import ServicioModel
from app.infrastructure.models.componente_model import ComponenteModel
from app.infrastructure.models.evento_model import EventoModel


def test_orden_model():
    modelo = OrdenModel(
        order_id="ORD-001",
        id_cliente=1,
        id_vehiculo=1,
        estado="CREATED",
        monto_autorizado="1000.00",
        version_autorizacion=1,
        total_real="0.00",
        fecha_creacion=datetime.now(timezone.utc)
    )
    assert modelo.order_id == "ORD-001"
    assert modelo.estado == "CREATED"
    assert modelo.version_autorizacion == 1


def test_cliente_model():
    modelo = ClienteModel(
        id_cliente=1,
        nombre="Juan Pérez"
    )
    assert modelo.id_cliente == 1
    assert modelo.nombre == "Juan Pérez"


def test_vehiculo_model():
    modelo = VehiculoModel(
        id_vehiculo=1,
        id_cliente=1,
        placa="ABC-123",
        marca="Toyota",
        modelo="Corolla",
        anio=2020
    )
    assert modelo.id_vehiculo == 1
    assert modelo.placa == "ABC-123"
    assert modelo.marca == "Toyota"


def test_servicio_model():
    modelo = ServicioModel(
        id_servicio=1,
        id_orden=1,
        descripcion="Cambio de aceite",
        costo_mano_obra_estimado="500.00",
        costo_real="600.00",
        completado=True
    )
    assert modelo.id_servicio == 1
    assert modelo.descripcion == "Cambio de aceite"
    assert modelo.completado is True


def test_componente_model():
    modelo = ComponenteModel(
        id_componente=1,
        id_servicio=1,
        descripcion="Aceite",
        costo_estimado="300.00",
        costo_real="350.00"
    )
    assert modelo.id_componente == 1
    assert modelo.descripcion == "Aceite"
    assert modelo.costo_estimado == "300.00"


def test_evento_model():
    import json
    modelo = EventoModel(
        id_orden=1,
        tipo="CREATED",
        timestamp=datetime.now(timezone.utc),
        metadatos_json=json.dumps({"key": "value"})
    )
    assert modelo.tipo == "CREATED"
    assert modelo.id_orden == 1
    assert modelo.metadatos_json is not None

