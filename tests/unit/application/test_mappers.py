from decimal import Decimal
from datetime import datetime, timezone
from app.application.mappers import (
    crear_orden_dto, agregar_servicio_dto,
    estado_diagnosticado_dto, autorizar_dto,
    estado_en_proceso_dto, costo_real_dto,
    intentar_completar_dto, reautorizar_dto,
    entregar_dto, cancelar_dto,
    componente_a_dto, servicio_a_dto, evento_a_dto, orden_a_dto,
    cliente_a_dto, vehiculo_a_dto
)
from app.domain.entidades import Orden, Servicio, Componente, Evento, Cliente, Vehiculo
from app.domain.enums import EstadoOrden


def test_crear_orden_dto():
    data = {
        "order_id": "ORD-001",
        "customer": "Juan Pérez",
        "vehicle": "Toyota Corolla"
    }
    dto = crear_orden_dto(data, "2025-01-01T10:00:00Z")
    assert dto.order_id == "ORD-001"
    assert dto.customer.nombre == "Juan Pérez"
    assert dto.vehicle.placa == "Toyota Corolla"
    assert isinstance(dto.timestamp, datetime)


def test_crear_orden_dto_sin_order_id():
    data = {
        "customer": "Juan",
        "vehicle": "Auto"
    }
    try:
        crear_orden_dto(data)
        assert False
    except ValueError:
        pass


def test_agregar_servicio_dto():
    data = {
        "order_id": "ORD-001",
        "service": {
            "description": "Cambio de aceite",
            "labor_estimated_cost": "500.00",
            "components": [
                {"description": "Aceite", "estimated_cost": "300.00"}
            ]
        }
    }
    dto = agregar_servicio_dto(data)
    assert dto.order_id == "ORD-001"
    assert dto.descripcion == "Cambio de aceite"
    assert dto.costo_mano_obra == Decimal("500.00")
    assert len(dto.componentes) == 1
    assert dto.componentes[0]["description"] == "Aceite"


def test_agregar_servicio_dto_formato_alternativo():
    data = {
        "order_id": "ORD-001",
        "description": "Servicio",
        "labor_estimated_cost": "1000.00",
        "components": []
    }
    dto = agregar_servicio_dto(data)
    assert dto.descripcion == "Servicio"
    assert dto.costo_mano_obra == Decimal("1000.00")


def test_estado_diagnosticado_dto():
    data = {"order_id": "ORD-001"}
    dto = estado_diagnosticado_dto(data)
    assert dto.order_id == "ORD-001"


def test_autorizar_dto():
    data = {"order_id": "ORD-001"}
    dto = autorizar_dto(data, "2025-01-01T10:00:00Z")
    assert dto.order_id == "ORD-001"
    assert isinstance(dto.timestamp, datetime)


def test_estado_en_proceso_dto():
    data = {"order_id": "ORD-001"}
    dto = estado_en_proceso_dto(data)
    assert dto.order_id == "ORD-001"


def test_costo_real_dto():
    data = {
        "order_id": "ORD-001",
        "service_id": 123,
        "real_cost": "1500.00",
        "completed": True,
        "components_real": {
            "1": "200.00"
        }
    }
    dto = costo_real_dto(data)
    assert dto.order_id == "ORD-001"
    assert dto.servicio_id == 123
    assert dto.costo_real == Decimal("1500.00")
    assert dto.completed is True
    assert 1 in dto.componentes_reales


def test_intentar_completar_dto():
    data = {"order_id": "ORD-001"}
    dto = intentar_completar_dto(data)
    assert dto.order_id == "ORD-001"


def test_reautorizar_dto():
    data = {
        "order_id": "ORD-001",
        "new_authorized_amount": "15000.00"
    }
    dto = reautorizar_dto(data, "2025-01-01T10:00:00Z")
    assert dto.order_id == "ORD-001"
    assert dto.nuevo_monto_autorizado == Decimal("15000.00")
    assert isinstance(dto.timestamp, datetime)


def test_entregar_dto():
    data = {"order_id": "ORD-001"}
    dto = entregar_dto(data)
    assert dto.order_id == "ORD-001"


def test_cancelar_dto():
    data = {
        "order_id": "ORD-001",
        "reason": "Cliente canceló"
    }
    dto = cancelar_dto(data)
    assert dto.order_id == "ORD-001"
    assert dto.motivo == "Cliente canceló"


def test_componente_a_dto():
    comp = Componente("Aceite", Decimal("300.00"))
    comp.id_componente = 1
    comp.costo_real = Decimal("350.00")
    dto = componente_a_dto(comp)
    assert dto.descripcion == "Aceite"
    assert dto.costo_estimado == "300.00"
    assert dto.costo_real == "350.00"


def test_componente_a_dto_sin_costo_real():
    comp = Componente("Filtro", Decimal("200.00"))
    comp.id_componente = 2
    dto = componente_a_dto(comp)
    assert dto.costo_real is None


def test_servicio_a_dto():
    srv = Servicio("Cambio de aceite", Decimal("500.00"))
    srv.id_servicio = 1
    srv.componentes.append(Componente("Aceite", Decimal("300.00")))
    srv.componentes[0].id_componente = 1
    srv.costo_real = Decimal("850.00")
    srv.completado = True
    
    dto = servicio_a_dto(srv)
    assert dto.descripcion == "Cambio de aceite"
    assert dto.costo_mano_obra_estimado == "500.00"
    assert dto.costo_real == "850.00"
    assert dto.completado is True
    assert len(dto.componentes) == 1


def test_evento_a_dto():
    evt = Evento("CREATED", datetime.now(timezone.utc), {})
    dto = evento_a_dto(evt, "ORD-001")
    assert dto.order_id == "ORD-001"
    assert dto.type == "CREATED"


def test_orden_a_dto():
    ord = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    ord.estado = EstadoOrden.AUTHORIZED
    ord.monto_autorizado = Decimal("1160.00")
    ord.version_autorizacion = 1
    
    srv = Servicio("Servicio", Decimal("1000.00"))
    srv.id_servicio = 1
    ord.servicios.append(srv)
    ord.eventos.append(Evento("CREATED", datetime.now(timezone.utc), {}))
    
    dto = orden_a_dto(ord)
    assert dto.order_id == "ORD-001"
    assert dto.status == "AUTHORIZED"
    assert dto.customer == "Juan"
    assert dto.vehicle == "Auto"
    assert dto.authorized_amount == "1160.00"
    assert dto.authorization_version == 1
    assert len(dto.services) == 1
    assert len(dto.events) == 1


def test_orden_a_dto_sin_monto():
    ord = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    dto = orden_a_dto(ord)
    assert dto.authorized_amount is None


def test_cliente_a_dto():
    c = Cliente("Juan Pérez")
    c.id_cliente = 1
    dto = cliente_a_dto(c)
    assert dto.nombre == "Juan Pérez"
    assert dto.id_cliente == 1


def test_vehiculo_a_dto():
    v = Vehiculo("ABC-123", 1, "Toyota", "Corolla", 2020)
    v.id_vehiculo = 1
    dto = vehiculo_a_dto(v, "Juan Pérez")
    assert dto.placa == "ABC-123"
    assert dto.marca == "Toyota"
    assert dto.modelo == "Corolla"
    assert dto.anio == 2020
    assert dto.id_cliente == 1
    assert dto.cliente_nombre == "Juan Pérez"

