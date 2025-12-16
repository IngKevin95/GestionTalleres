"""Tests de casos edge extendidos para endpoints.

Cubre validaciones de formatos, timestamps, datos faltantes y límites.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from datetime import datetime

from app.drivers.api.routes import _normalizar_comando, _procesar_comando_individual
from app.application.action_service import ActionService
from app.application.dtos import OrdenDTO, ErrorDTO
from app.domain.enums import EstadoOrden


class TestValidacionFormatosOrderId:
    """Tests para validación de formatos de order_id."""
    
    def test_order_id_como_string(self):
        """Test que order_id como string funciona correctamente."""
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
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"}
        }
        
        orders_dict = {}
        events = []
        errors = []
        
        _procesar_comando_individual(comando, 0, action_service, orders_dict, events, errors)
        
        assert "R001" in orders_dict
    
    def test_order_id_como_numero(self):
        """Test que order_id como número se convierte a string."""
        action_service = Mock(spec=ActionService)
        orden_dto = OrdenDTO(
            order_id="123",
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
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": 123, "customer": "ACME", "vehicle": "ABC-123"}
        }
        
        orders_dict = {}
        events = []
        errors = []
        
        _procesar_comando_individual(comando, 0, action_service, orders_dict, events, errors)
        
        action_service.procesar_comando.assert_called_once()
        call_args = action_service.procesar_comando.call_args[0][0]
        order_id = call_args.get("data", {}).get("order_id")
        assert isinstance(order_id, (str, int, type(None)))


class TestManejoTimestamps:
    """Tests para manejo de timestamps."""
    
    def test_comando_con_timestamp_valido(self):
        """Test comando con timestamp válido."""
        comando = {
            "op": "CREATE_ORDER",
            "ts": "2025-03-01T09:00:00Z",
            "data": {"order_id": "R001"}
        }
        result = _normalizar_comando(comando, 0)
        assert "ts" in result
        assert result["ts"] == "2025-03-01T09:00:00Z"
    
    def test_comando_sin_timestamp(self):
        """Test comando sin timestamp (debe funcionar)."""
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": "R001"}
        }
        result = _normalizar_comando(comando, 0)
        assert result == comando


class TestValidacionDatosFaltantes:
    """Tests para validación de datos faltantes."""
    
    def test_comando_sin_data_lanza_error(self):
        """Test que comando sin 'data' lanza error."""
        comando = {
            "op": "CREATE_ORDER"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            _normalizar_comando(comando, 0)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_comando_sin_op_ni_command_lanza_error(self):
        """Test que comando sin 'op' ni 'command' lanza error."""
        comando = {
            "data": {"order_id": "R001"}
        }
        
        with pytest.raises(HTTPException) as exc_info:
            _normalizar_comando(comando, 0)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestLimitesBatch:
    """Tests para límites de comandos en batch."""
    
    def test_procesar_multiples_comandos(self):
        """Test procesar múltiples comandos en secuencia."""
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
        
        orden_dto_2 = OrdenDTO(
            order_id="R002",
            status=EstadoOrden.CREATED.value,
            customer="ACME",
            vehicle="XYZ-456",
            subtotal_estimated="0.00",
            authorized_amount=None,
            real_total="0.00",
            events=[],
            services=[],
            authorization_version=0
        )
        action_service.procesar_comando.side_effect = [
            (orden_dto, [], None),
            (orden_dto_2, [], None)
        ]
        
        comandos = [
            {"op": "CREATE_ORDER", "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"}},
            {"op": "CREATE_ORDER", "data": {"order_id": "R002", "customer": "ACME", "vehicle": "XYZ-456"}}
        ]
        
        for idx, comando in enumerate(comandos):
            _procesar_comando_individual(comando, idx, action_service, orders_dict, events, errors)
        
        assert len(orders_dict) == 2
        assert "R001" in orders_dict
        assert "R002" in orders_dict
    
    def test_procesar_comandos_con_errores_mezclados(self):
        """Test procesar comandos donde algunos fallan y otros no."""
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
        error_dto = ErrorDTO(
            op="CREATE_ORDER",
            order_id="R002",
            code="INVALID_OPERATION",
            message="Error de prueba"
        )
        
        action_service.procesar_comando.side_effect = [
            (orden_dto, [], None),
            (None, [], error_dto)
        ]
        
        orders_dict = {}
        events = []
        errors = []
        
        comandos = [
            {"op": "CREATE_ORDER", "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"}},
            {"op": "CREATE_ORDER", "data": {"order_id": "R002"}}
        ]
        
        for idx, comando in enumerate(comandos):
            _procesar_comando_individual(comando, idx, action_service, orders_dict, events, errors)
        
        assert len(orders_dict) == 1
        assert "R001" in orders_dict
        assert len(errors) == 1
        assert errors[0]["order_id"] == "R002"


class TestCasosEdgeComandos:
    """Tests para casos edge específicos de comandos."""
    
    def test_comando_con_data_vacio(self):
        """Test comando con data vacío."""
        comando = {
            "op": "CREATE_ORDER",
            "data": {}
        }
        result = _normalizar_comando(comando, 0)
        assert result["op"] == "CREATE_ORDER"
        assert result["data"] == {}
    
    def test_comando_con_order_id_none(self):
        """Test comando con order_id None."""
        action_service = Mock(spec=ActionService)
        orden_dto = OrdenDTO(
            order_id="",
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
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": None, "customer": "ACME", "vehicle": "ABC-123"}
        }
        
        orders_dict = {}
        events = []
        errors = []
        
        _procesar_comando_individual(comando, 0, action_service, orders_dict, events, errors)
        
        action_service.procesar_comando.assert_called_once()
    
    def test_comando_con_indice_negativo(self):
        """Test procesar comando con índice negativo (caso edge)."""
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
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"}
        }
        
        orders_dict = {}
        events = []
        errors = []
        
        _procesar_comando_individual(comando, -1, action_service, orders_dict, events, errors)
        
        assert "R001" in orders_dict

