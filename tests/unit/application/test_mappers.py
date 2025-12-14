from decimal import Decimal
from datetime import datetime, timezone
from app.application.mappers import (
    json_a_crear_orden_dto, json_a_agregar_servicio_dto,
    json_a_establecer_estado_diagnosticado_dto, json_a_autorizar_dto,
    json_a_establecer_estado_en_proceso_dto, json_a_establecer_costo_real_dto,
    json_a_intentar_completar_dto, json_a_reautorizar_dto,
    json_a_entregar_dto, json_a_cancelar_dto,
    componente_a_dto, servicio_a_dto, evento_a_dto, orden_a_dto,
    cliente_a_dto, vehiculo_a_dto
)
from app.domain.entidades import Orden, Servicio, Componente, Evento, Cliente, Vehiculo
from app.domain.enums import EstadoOrden


def test_json_a_crear_orden_dto():
    json_data = {
        "order_id": "ORD-001",
        "customer": "Juan Pérez",
        "vehicle": "Toyota Corolla"
    }
    dto = json_a_crear_orden_dto(json_data, "2025-01-01T10:00:00Z")
    assert dto.order_id == "ORD-001"
    assert dto.cliente == "Juan Pérez"
    assert dto.vehiculo == "Toyota Corolla"
    assert isinstance(dto.timestamp, datetime)


def test_json_a_crear_orden_dto_sin_order_id():
    json_data = {
        "customer": "Juan",
        "vehicle": "Auto"
    }
    dto = json_a_crear_orden_dto(json_data)
    assert dto.cliente == "Juan"
    assert dto.order_id is None


def test_json_a_agregar_servicio_dto():
    json_data = {
        "order_id": "ORD-001",
        "service": {
            "description": "Cambio de aceite",
            "labor_estimated_cost": "500.00",
            "components": [
                {"description": "Aceite", "estimated_cost": "300.00"}
            ]
        }
    }
    dto = json_a_agregar_servicio_dto(json_data)
    assert dto.order_id == "ORD-001"
    assert dto.descripcion == "Cambio de aceite"
    assert dto.costo_mano_obra == Decimal("500.00")
    assert len(dto.componentes) == 1
    assert dto.componentes[0]["description"] == "Aceite"


def test_json_a_agregar_servicio_dto_formato_alternativo():
    json_data = {
        "order_id": "ORD-001",
        "description": "Servicio",
        "labor_estimated_cost": "1000.00",
        "components": []
    }
    dto = json_a_agregar_servicio_dto(json_data)
    assert dto.descripcion == "Servicio"
    assert dto.costo_mano_obra == Decimal("1000.00")


def test_json_a_establecer_estado_diagnosticado_dto():
    json_data = {"order_id": "ORD-001"}
    dto = json_a_establecer_estado_diagnosticado_dto(json_data)
    assert dto.order_id == "ORD-001"


def test_json_a_autorizar_dto():
    json_data = {"order_id": "ORD-001"}
    dto = json_a_autorizar_dto(json_data, "2025-01-01T10:00:00Z")
    assert dto.order_id == "ORD-001"
    assert isinstance(dto.timestamp, datetime)


def test_json_a_establecer_estado_en_proceso_dto():
    json_data = {"order_id": "ORD-001"}
    dto = json_a_establecer_estado_en_proceso_dto(json_data)
    assert dto.order_id == "ORD-001"


def test_json_a_establecer_costo_real_dto():
    json_data = {
        "order_id": "ORD-001",
        "service_id": "SERV-123",
        "real_cost": "1500.00",
        "completed": True,
        "components_real": {
            "COMP-1": "200.00"
        }
    }
    dto = json_a_establecer_costo_real_dto(json_data)
    assert dto.order_id == "ORD-001"
    assert dto.servicio_id == "SERV-123"
    assert dto.costo_real == Decimal("1500.00")
    assert dto.completed is True
    assert "COMP-1" in dto.componentes_reales


def test_json_a_intentar_completar_dto():
    json_data = {"order_id": "ORD-001"}
    dto = json_a_intentar_completar_dto(json_data)
    assert dto.order_id == "ORD-001"


def test_json_a_reautorizar_dto():
    json_data = {
        "order_id": "ORD-001",
        "new_authorized_amount": "15000.00"
    }
    dto = json_a_reautorizar_dto(json_data, "2025-01-01T10:00:00Z")
    assert dto.order_id == "ORD-001"
    assert dto.nuevo_monto_autorizado == Decimal("15000.00")
    assert isinstance(dto.timestamp, datetime)


def test_json_a_entregar_dto():
    json_data = {"order_id": "ORD-001"}
    dto = json_a_entregar_dto(json_data)
    assert dto.order_id == "ORD-001"


def test_json_a_cancelar_dto():
    json_data = {
        "order_id": "ORD-001",
        "reason": "Cliente canceló"
    }
    dto = json_a_cancelar_dto(json_data)
    assert dto.order_id == "ORD-001"
    assert dto.motivo == "Cliente canceló"


def test_componente_a_dto():
    comp = Componente("Aceite", Decimal("300.00"))
    comp.costo_real = Decimal("350.00")
    dto = componente_a_dto(comp)
    assert dto.descripcion == "Aceite"
    assert dto.costo_estimado == "300.00"
    assert dto.costo_real == "350.00"


def test_componente_a_dto_sin_costo_real():
    comp = Componente("Filtro", Decimal("200.00"))
    dto = componente_a_dto(comp)
    assert dto.costo_real is None


def test_servicio_a_dto():
    servicio = Servicio("Cambio de aceite", Decimal("500.00"))
    servicio.componentes.append(Componente("Aceite", Decimal("300.00")))
    servicio.costo_real = Decimal("850.00")
    servicio.completado = True
    
    dto = servicio_a_dto(servicio)
    assert dto.descripcion == "Cambio de aceite"
    assert dto.costo_mano_obra_estimado == "500.00"
    assert dto.costo_real == "850.00"
    assert dto.completado is True
    assert len(dto.componentes) == 1


def test_evento_a_dto():
    evento = Evento("CREATED", datetime.now(timezone.utc), {})
    dto = evento_a_dto(evento, "ORD-001")
    assert dto.order_id == "ORD-001"
    assert dto.type == "CREATED"


def test_orden_a_dto():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.AUTHORIZED
    orden.monto_autorizado = Decimal("1160.00")
    orden.version_autorizacion = 1
    
    servicio = Servicio("Servicio", Decimal("1000.00"))
    orden.servicios.append(servicio)
    orden.eventos.append(Evento("CREATED", datetime.now(timezone.utc), {}))
    
    dto = orden_a_dto(orden)
    assert dto.order_id == "ORD-001"
    assert dto.status == "AUTHORIZED"
    assert dto.customer == "Juan"
    assert dto.vehicle == "Auto"
    assert dto.authorized_amount == "1160.00"
    assert dto.authorization_version == 1
    assert len(dto.services) == 1
    assert len(dto.events) == 1


def test_orden_a_dto_sin_monto_autorizado():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    dto = orden_a_dto(orden)
    assert dto.authorized_amount is None


def test_cliente_a_dto():
    cliente = Cliente("Juan Pérez")
    dto = cliente_a_dto(cliente)
    assert dto.nombre == "Juan Pérez"
    assert dto.id_cliente == cliente.id_cliente


def test_vehiculo_a_dto():
    vehiculo = Vehiculo("ABC-123", "CLI-001", "Toyota", "Corolla", 2020)
    dto = vehiculo_a_dto(vehiculo, "Juan Pérez")
    assert dto.descripcion == "ABC-123"
    assert dto.marca == "Toyota"
    assert dto.modelo == "Corolla"
    assert dto.anio == 2020
    assert dto.id_cliente == "CLI-001"
    assert dto.cliente_nombre == "Juan Pérez"

