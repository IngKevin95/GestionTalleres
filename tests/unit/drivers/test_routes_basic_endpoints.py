import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi import HTTPException, status


def test_root_returns_dict():
    from app.drivers.api.routes import root
    resultado = root()
    assert isinstance(resultado, dict)


def test_root_has_message_field():
    from app.drivers.api.routes import root
    resultado = root()
    assert "message" in resultado


def test_root_has_version_field():
    from app.drivers.api.routes import root
    resultado = root()
    assert "version" in resultado


def test_root_message_contains_api_name():
    from app.drivers.api.routes import root
    resultado = root()
    assert "API" in resultado["message"] or "api" in resultado["message"].lower()


def test_router_exists():
    from app.drivers.api.routes import router
    assert router is not None


def test_router_has_routes():
    from app.drivers.api.routes import router
    assert len(router.routes) > 0


def test_router_has_health_route():
    from app.drivers.api.routes import router
    route_paths = [route.path for route in router.routes]
    assert any("health" in path for path in route_paths)


def test_router_has_root_route():
    from app.drivers.api.routes import router
    route_paths = [route.path for route in router.routes]
    assert "/" in route_paths or any(p == "" for p in route_paths)


def test_procesar_comandos_exitoso():
    from unittest.mock import Mock
    from app.drivers.api.routes import procesar_comandos
    from app.drivers.api.schemas import CommandsRequest
    from app.application.dtos import OrdenDTO
    from app.domain.enums import EstadoOrden
    
    action_service = Mock()
    orden_dto = OrdenDTO(
        order_id="ORD001",
        status=EstadoOrden.CREATED.value,
        customer="Juan",
        vehicle="ABC123",
        services=[],
        subtotal_estimated="0.00",
        authorized_amount=None,
        authorization_version=0,
        real_total="0.00",
        events=[]
    )
    action_service.procesar_comando.return_value = (orden_dto, [], None)
    
    request = CommandsRequest(commands=[{"op": "CREATE_ORDER", "data": {"order_id": "ORD001", "customer": "Juan", "vehicle": "ABC123"}}])
    resultado = procesar_comandos(request, action_service)
    assert len(resultado.orders) == 1


def test_procesar_comandos_error():
    from unittest.mock import Mock
    import pytest
    from fastapi import HTTPException, status
    from app.drivers.api.routes import procesar_comandos
    from app.drivers.api.schemas import CommandsRequest
    
    action_service = Mock()
    action_service.procesar_comando.side_effect = Exception("Error general")
    
    request = CommandsRequest(commands=[{"op": "CREATE_ORDER", "data": {}}])
    
    with pytest.raises(HTTPException) as exc:
        procesar_comandos(request, action_service)
    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR