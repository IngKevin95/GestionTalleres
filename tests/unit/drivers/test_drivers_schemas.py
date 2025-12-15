from decimal import Decimal
from datetime import datetime
from app.drivers.api.schemas import (
    HealthResponse,
    CommandsRequest,
    CommandsResponse,
    SetStateRequest,
    CreateOrderRequest,
    AddServiceRequest,
    SetRealCostRequest,
    AuthorizeRequest,
    ReauthorizeRequest,
    CancelRequest,
    ClienteResponse,
    CreateClienteRequest,
    UpdateClienteRequest,
    ListClientesResponse,
    VehiculoResponse,
    CreateVehiculoRequest,
    UpdateVehiculoRequest,
    ListVehiculosResponse
)


def test_health_response():
    response = HealthResponse(
        status="ok",
        api="operativa",
        database="conectada",
        tablas=["ordenes", "clientes"],
        tablas_faltantes=[],
        mensaje=None
    )
    assert response.status == "ok"
    assert response.api == "operativa"
    assert len(response.tablas) == 2


def test_health_response_con_warning():
    response = HealthResponse(
        status="warning",
        api="operativa",
        database="conectada",
        tablas=["ordenes"],
        tablas_faltantes=["clientes"],
        mensaje="Faltan algunas tablas"
    )
    assert response.status == "warning"
    assert len(response.tablas_faltantes) == 1


def test_commands_request():
    request = CommandsRequest(
        commands=[
            {"op": "CREATE_ORDER", "data": {"customer": "Juan"}},
            {"op": "ADD_SERVICE", "data": {"order_id": "ORD-001"}}
        ]
    )
    assert len(request.commands) == 2


def test_commands_response():
    response = CommandsResponse(
        orders=[{"order_id": "ORD-001", "status": "CREATED"}],
        events=[{"type": "CREATED"}],
        errors=[]
    )
    assert len(response.orders) == 1
    assert len(response.events) == 1
    assert len(response.errors) == 0


def test_set_state_request():
    request = SetStateRequest(state="DIAGNOSED")
    assert request.state == "DIAGNOSED"


def test_create_order_request():
    request = CreateOrderRequest(
        customer="Juan",
        vehicle="Auto",
        order_id="ORD-001",
        ts=datetime.utcnow()
    )
    assert request.customer == "Juan"
    assert request.vehicle == "Auto"


def test_add_service_request():
    request = AddServiceRequest(
        description="Servicio",
        labor_estimated_cost=Decimal("1000.00"),
        components=[{"description": "Comp"}]
    )
    assert request.description == "Servicio"
    assert request.labor_estimated_cost == Decimal("1000.00")


def test_set_real_cost_request():
    request = SetRealCostRequest(
        service_id=1,
        real_cost=Decimal("1200.00"),
        completed=True,
        components_real={1: Decimal("200.00")}
    )
    assert request.service_id == 1
    assert request.real_cost == Decimal("1200.00")


def test_authorize_request():
    request = AuthorizeRequest(ts=datetime.utcnow())
    assert request.ts is not None


def test_reauthorize_request():
    request = ReauthorizeRequest(
        new_authorized_amount=Decimal("1500.00"),
        ts=datetime.utcnow()
    )
    assert request.new_authorized_amount == Decimal("1500.00")


def test_cancel_request():
    request = CancelRequest(reason="Cliente canceló")
    assert request.reason == "Cliente canceló"


def test_cliente_response():
    response = ClienteResponse(id_cliente=1, nombre="Juan")
    assert response.id_cliente == 1
    assert response.nombre == "Juan"


def test_create_cliente_request():
    request = CreateClienteRequest(nombre="Juan")
    assert request.nombre == "Juan"


def test_update_cliente_request():
    request = UpdateClienteRequest(nombre="Juan Actualizado")
    assert request.nombre == "Juan Actualizado"


def test_list_clientes_response():
    cliente1 = ClienteResponse(id_cliente=1, nombre="Juan")
    cliente2 = ClienteResponse(id_cliente=2, nombre="Pedro")
    response = ListClientesResponse(clientes=[cliente1, cliente2])
    assert len(response.clientes) == 2


def test_vehiculo_response():
    response = VehiculoResponse(
        id_vehiculo=1,
        placa="ABC-123",
        marca="Toyota",
        modelo="Corolla",
        anio=2020,
        id_cliente=1
    )
    assert response.id_vehiculo == 1
    assert response.marca == "Toyota"


def test_create_vehiculo_request():
    request = CreateVehiculoRequest(
        placa="ABC-123",
        customer={"id_cliente": 1},
        marca="Toyota",
        modelo="Corolla",
        anio=2020
    )
    assert request.placa == "ABC-123"
    assert request.customer.id_cliente == 1


def test_update_vehiculo_request():
    request = UpdateVehiculoRequest(
        placa="XYZ-789",
        marca="Honda"
    )
    assert request.placa == "XYZ-789"
    assert request.marca == "Honda"


def test_list_vehiculos_response():
    vehiculo1 = VehiculoResponse(
        id_vehiculo=1,
        placa="ABC-123",
        id_cliente=1
    )
    vehiculo2 = VehiculoResponse(
        id_vehiculo=2,
        placa="XYZ-789",
        id_cliente=1
    )
    response = ListVehiculosResponse(vehiculos=[vehiculo1, vehiculo2])
    assert len(response.vehiculos) == 2

