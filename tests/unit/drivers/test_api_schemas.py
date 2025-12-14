from decimal import Decimal
from app.drivers.api.schemas import (
    HealthResponse, CommandsRequest, CommandsResponse, SetStateRequest,
    CreateOrderRequest, AddServiceRequest, SetRealCostRequest, AuthorizeRequest,
    ReauthorizeRequest, CancelRequest, ClienteResponse, CreateClienteRequest,
    UpdateClienteRequest, ListClientesResponse, VehiculoResponse, CreateVehiculoRequest,
    UpdateVehiculoRequest, ListVehiculosResponse
)


def test_health_response():
    response = HealthResponse(
        status="ok",
        api="operativa",
        database="conectada"
    )
    assert response.status == "ok"
    assert response.api == "operativa"


def test_commands_request():
    request = CommandsRequest(
        commands=[
            {
                "op": "CREATE_ORDER",
                "ts": "2025-01-01T10:00:00Z",
                "data": {"order_id": "ORD-001", "customer": "Juan", "vehicle": "Auto"}
            }
        ]
    )
    assert len(request.commands) == 1
    assert request.commands[0]["op"] == "CREATE_ORDER"


def test_create_order_request():
    request = CreateOrderRequest(
        order_id="ORD-001",
        customer="Juan",
        vehicle="Auto"
    )
    assert request.order_id == "ORD-001"
    assert request.customer == "Juan"


def test_add_service_request():
    request = AddServiceRequest(
        description="Servicio",
        labor_estimated_cost=Decimal("1000.00"),
        components=[]
    )
    assert request.description == "Servicio"
    assert request.labor_estimated_cost == Decimal("1000.00")


def test_set_real_cost_request():
    request = SetRealCostRequest(
        service_index=1,
        real_cost=Decimal("1200.00"),
        completed=True
    )
    assert request.service_index == 1
    assert request.real_cost == Decimal("1200.00")


def test_authorize_request():
    request = AuthorizeRequest()
    assert request.ts is None


def test_reauthorize_request():
    request = ReauthorizeRequest(
        new_authorized_amount=Decimal("1500.00")
    )
    assert request.new_authorized_amount == Decimal("1500.00")


def test_cancel_request():
    request = CancelRequest(reason="Cliente canceló")
    assert request.reason == "Cliente canceló"


def test_cliente_response():
    response = ClienteResponse(
        id_cliente="CLI-001",
        nombre="Juan Pérez"
    )
    assert response.id_cliente == "CLI-001"
    assert response.nombre == "Juan Pérez"


def test_create_cliente_request():
    request = CreateClienteRequest(nombre="Juan Pérez")
    assert request.nombre == "Juan Pérez"


def test_update_cliente_request():
    request = UpdateClienteRequest(nombre="Juan Pérez Actualizado")
    assert request.nombre == "Juan Pérez Actualizado"


def test_list_clientes_response():
    from app.drivers.api.schemas import ClienteResponse
    response = ListClientesResponse(
        clientes=[
            ClienteResponse(id_cliente="CLI-001", nombre="Juan")
        ]
    )
    assert len(response.clientes) == 1


def test_vehiculo_response():
    response = VehiculoResponse(
        id_vehiculo="VEH-001",
        descripcion="ABC-123",
        id_cliente="CLI-001"
    )
    assert response.id_vehiculo == "VEH-001"
    assert response.descripcion == "ABC-123"


def test_create_vehiculo_request():
    request = CreateVehiculoRequest(
        descripcion="ABC-123",
        id_cliente="CLI-001"
    )
    assert request.descripcion == "ABC-123"
    assert request.id_cliente == "CLI-001"


def test_update_vehiculo_request():
    request = UpdateVehiculoRequest(descripcion="XYZ-789")
    assert request.descripcion == "XYZ-789"


def test_list_vehiculos_response():
    from app.drivers.api.schemas import VehiculoResponse
    response = ListVehiculosResponse(
        vehiculos=[
            VehiculoResponse(id_vehiculo="VEH-001", descripcion="ABC-123", id_cliente="CLI-001")
        ]
    )
    assert len(response.vehiculos) == 1

