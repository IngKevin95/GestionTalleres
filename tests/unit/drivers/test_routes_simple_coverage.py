"""Tests simples para aumentar cobertura de routes.py"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from app.drivers.api.routes import procesar_comandos, _procesar_comando_individual
from app.drivers.api.schemas import CommandsRequest
from app.application.dtos import OrdenDTO, EventoDTO, ServicioDTO
from app.domain.enums import EstadoOrden


class TestProcesarComandosSimple:
    """Tests simples para procesar_comandos"""
    
    def test_procesar_comandos_exitoso(self):
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
    
    def test_procesar_comandos_error_general(self):
        action_service = Mock()
        action_service.procesar_comando.side_effect = Exception("Error general")
        
        request = CommandsRequest(commands=[{"op": "CREATE_ORDER", "data": {}}])
        
        with pytest.raises(HTTPException) as exc:
            procesar_comandos(request, action_service)
        assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestProcesarComandoIndividualSimple:
    """Tests simples para _procesar_comando_individual"""
    
    @patch('app.drivers.api.routes.logger')
    def test_procesar_comando_individual_sin_order_id(self, mock_logger):
        comando = {"op": "CREATE_ORDER", "data": {}}
        action_service = Mock()
        orders_dict = {}
        events = []
        errors = []
        
        # Cuando no hay order_id en data, debería auto-generarse
        orden_dto = OrdenDTO(
            order_id="ORD-AUTO",
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
        
        _procesar_comando_individual(comando, 1, action_service, orders_dict, events, errors)
        assert len(orders_dict) == 1  # Orden fue creada
    
    @patch('app.drivers.api.routes.logger')
    def test_procesar_comando_individual_con_eventos(self, mock_logger):
        comando = {"op": "CREATE_ORDER", "data": {}}
        action_service = Mock()
        orders_dict = {}
        events = []
        errors = []
        
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
            events=[EventoDTO(order_id="ORD001", type="CREATED")]
        )
        action_service.procesar_comando.return_value = (orden_dto, [EventoDTO(order_id="ORD001", type="CREATED")], None)
        
        _procesar_comando_individual(comando, 1, action_service, orders_dict, events, errors)
        assert len(events) == 1

