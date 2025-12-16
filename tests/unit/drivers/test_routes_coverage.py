"""Tests adicionales para mejorar cobertura de routes.py.

Cubre endpoints de clientes, vehículos y funciones helper que no están
suficientemente testeadas.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from decimal import Decimal

from app.drivers.api.routes import (
    obtener_cliente_por_criterio,
    obtener_vehiculo_por_criterio,
    _normalizar_comando,
    _procesar_comando_individual
)
from app.drivers.api.schemas import CustomerIdentifier, VehicleIdentifier
from app.application.action_service import ActionService
from app.application.dtos import OrdenDTO, EventoDTO, ErrorDTO
from app.domain.entidades import Cliente, Vehiculo
from app.domain.enums import EstadoOrden


class TestObtenerClientePorCriterio:
    """Tests para la función helper obtener_cliente_por_criterio."""
    
    def test_obtener_cliente_por_id_cliente(self):
        """Test obtener cliente por id_cliente."""
        repo = Mock()
        cliente = Cliente(nombre="Juan", identificacion="123")
        repo.buscar_por_criterio.return_value = cliente
        
        customer = CustomerIdentifier(id_cliente=1, identificacion=None, nombre=None)
        result = obtener_cliente_por_criterio(customer, repo)
        
        assert result == cliente
        repo.buscar_por_criterio.assert_called_once_with(id_cliente=1, identificacion=None, nombre=None)
    
    def test_obtener_cliente_por_identificacion(self):
        """Test obtener cliente por identificación."""
        repo = Mock()
        cliente = Cliente(nombre="Juan", identificacion="123")
        repo.buscar_por_criterio.return_value = cliente
        
        customer = CustomerIdentifier(id_cliente=None, identificacion="123", nombre=None)
        result = obtener_cliente_por_criterio(customer, repo)
        
        assert result == cliente
        repo.buscar_por_criterio.assert_called_once_with(id_cliente=None, identificacion="123", nombre=None)
    
    def test_obtener_cliente_por_nombre(self):
        """Test obtener cliente por nombre."""
        repo = Mock()
        cliente = Cliente(nombre="Juan", identificacion="123")
        repo.buscar_por_criterio.return_value = cliente
        
        customer = CustomerIdentifier(id_cliente=None, identificacion=None, nombre="Juan")
        result = obtener_cliente_por_criterio(customer, repo)
        
        assert result == cliente
        repo.buscar_por_criterio.assert_called_once_with(id_cliente=None, identificacion=None, nombre="Juan")
    
    def test_obtener_cliente_sin_criterio_lanza_error(self):
        """Test que lanza error si no se proporciona ningún criterio."""
        repo = Mock()
        customer = CustomerIdentifier(id_cliente=None, identificacion=None, nombre=None)
        
        with pytest.raises(HTTPException) as exc_info:
            obtener_cliente_por_criterio(customer, repo)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_obtener_cliente_multiples_criterios_lanza_error(self):
        """Test que lanza error si se proporcionan múltiples criterios."""
        repo = Mock()
        customer = CustomerIdentifier(id_cliente=1, identificacion="123", nombre=None)
        
        with pytest.raises(HTTPException) as exc_info:
            obtener_cliente_por_criterio(customer, repo)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_obtener_cliente_no_encontrado_lanza_error(self):
        """Test que lanza error si el cliente no se encuentra."""
        repo = Mock()
        repo.buscar_por_criterio.return_value = None
        
        customer = CustomerIdentifier(id_cliente=1, identificacion=None, nombre=None)
        
        with pytest.raises(HTTPException) as exc_info:
            obtener_cliente_por_criterio(customer, repo)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestObtenerVehiculoPorCriterio:
    """Tests para la función helper obtener_vehiculo_por_criterio."""
    
    def test_obtener_vehiculo_por_id_vehiculo(self):
        """Test obtener vehículo por id_vehiculo."""
        repo = Mock()
        vehiculo = Vehiculo(placa="ABC-123", marca="Toyota", id_cliente=1)
        repo.buscar_por_criterio.return_value = vehiculo
        
        vehicle = VehicleIdentifier(id_vehiculo=1, placa=None)
        result = obtener_vehiculo_por_criterio(vehicle, repo)
        
        assert result == vehiculo
        repo.buscar_por_criterio.assert_called_once_with(id_vehiculo=1, placa=None)
    
    def test_obtener_vehiculo_por_placa(self):
        """Test obtener vehículo por placa."""
        repo = Mock()
        vehiculo = Vehiculo(placa="ABC-123", marca="Toyota", id_cliente=1)
        repo.buscar_por_criterio.return_value = vehiculo
        
        vehicle = VehicleIdentifier(id_vehiculo=None, placa="ABC-123")
        result = obtener_vehiculo_por_criterio(vehicle, repo)
        
        assert result == vehiculo
        repo.buscar_por_criterio.assert_called_once_with(id_vehiculo=None, placa="ABC-123")
    
    def test_obtener_vehiculo_sin_criterio_lanza_error(self):
        """Test que lanza error si no se proporciona ningún criterio."""
        repo = Mock()
        vehicle = VehicleIdentifier(id_vehiculo=None, placa=None)
        
        with pytest.raises(HTTPException) as exc_info:
            obtener_vehiculo_por_criterio(vehicle, repo)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_obtener_vehiculo_multiples_criterios_lanza_error(self):
        """Test que lanza error si se proporcionan múltiples criterios."""
        repo = Mock()
        vehicle = VehicleIdentifier(id_vehiculo=1, placa="ABC-123")
        
        with pytest.raises(HTTPException) as exc_info:
            obtener_vehiculo_por_criterio(vehicle, repo)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_obtener_vehiculo_no_encontrado_lanza_error(self):
        """Test que lanza error si el vehículo no se encuentra."""
        repo = Mock()
        repo.buscar_por_criterio.return_value = None
        
        vehicle = VehicleIdentifier(id_vehiculo=1, placa=None)
        
        with pytest.raises(HTTPException) as exc_info:
            obtener_vehiculo_por_criterio(vehicle, repo)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestNormalizarComando:
    """Tests para la función _normalizar_comando."""
    
    def test_normalizar_comando_con_op_y_data(self):
        """Test normalizar comando que ya tiene op y data."""
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": "R001"}
        }
        result = _normalizar_comando(comando, 0)
        assert result == comando
    
    def test_normalizar_comando_con_command(self):
        """Test normalizar comando que tiene 'command' en lugar de 'op'."""
        comando = {
            "command": "CREATE_ORDER",
            "order_id": "R001"
        }
        result = _normalizar_comando(comando, 0)
        assert "op" in result
        assert "data" in result
        assert result["op"] == "CREATE_ORDER"
        assert result["data"]["order_id"] == "R001"
    
    def test_normalizar_comando_sin_op_ni_command_lanza_error(self):
        """Test que lanza error si no tiene op ni command."""
        comando = {"order_id": "R001"}
        
        with pytest.raises(HTTPException) as exc_info:
            _normalizar_comando(comando, 0)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestProcesarComandoIndividual:
    """Tests para la función _procesar_comando_individual."""
    
    def test_procesar_comando_exitoso(self):
        """Test procesar comando exitoso."""
        action_service = Mock(spec=ActionService)
        orden_dto = OrdenDTO(
            order_id="R001",
            status=EstadoOrden.CREATED.value,
            customer="ACME",
            vehicle="ABC-123",
            subtotal_estimated="0.00",
            authorized_amount=None,
            real_total="0.00",
            events=[],
            services=[],
            authorization_version=0
        )
        action_service.procesar_comando.return_value = (orden_dto, [], None)
        
        orders_dict = {}
        events = []
        errors = []
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"}
        }
        
        _procesar_comando_individual(comando, 0, action_service, orders_dict, events, errors)
        
        assert "R001" in orders_dict
        assert len(errors) == 0
    
    def test_procesar_comando_con_error(self):
        """Test procesar comando que genera error."""
        action_service = Mock(spec=ActionService)
        error_dto = ErrorDTO(
            op="CREATE_ORDER",
            order_id="R001",
            code="INVALID_OPERATION",
            message="Error de prueba"
        )
        action_service.procesar_comando.return_value = (None, [], error_dto)
        
        orders_dict = {}
        events = []
        errors = []
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": "R001"}
        }
        
        _procesar_comando_individual(comando, 0, action_service, orders_dict, events, errors)
        
        assert len(errors) == 1
        assert errors[0]["code"] == "INVALID_OPERATION"
    
    def test_procesar_comando_con_eventos(self):
        """Test procesar comando que genera eventos."""
        action_service = Mock(spec=ActionService)
        orden_dto = OrdenDTO(
            order_id="R001",
            status=EstadoOrden.CREATED.value,
            customer="ACME",
            vehicle="ABC-123",
            subtotal_estimated="0.00",
            authorized_amount=None,
            real_total="0.00",
            events=[],
            services=[],
            authorization_version=0
        )
        evento_dto = EventoDTO(order_id="R001", type="CREATED")
        action_service.procesar_comando.return_value = (orden_dto, [evento_dto], None)
        
        orders_dict = {}
        events = []
        errors = []
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"}
        }
        
        _procesar_comando_individual(comando, 0, action_service, orders_dict, events, errors)
        
        assert len(events) == 1
        assert events[0]["type"] == "CREATED"

