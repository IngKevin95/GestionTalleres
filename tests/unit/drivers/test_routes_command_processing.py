"""
Tests for command processing in routes.
Tests the _procesar_comando_individual function and related command normalization
to ensure proper handling of batch command operations.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestRoutesLines:
    """Tests para cubrir líneas específicas de routes.py"""
    
    # def test_formatear_orden_respuesta(self):
    #     """Cubre _formatear_orden_respuesta lineas 113-121"""
    #     from app.drivers.api.routes import _formatear_orden_respuesta
    #     
    #     orden = MagicMock()
    #     orden.order_id = "ORD-001"
    #     orden.status = "PENDING"
    #     orden.customer = "Test"
    #     orden.vehicle = "Test"
    #     orden.subtotal_estimated = "100.00"
    #     orden.authorized_amount = None
    #     orden.real_total = "0.00"
    #     
    #     result = _formatear_orden_respuesta(orden)
    #     
    #     assert result["authorized_amount"] == "0.00"
    #     assert result["order_id"] == "ORD-001"
    
    def test_normalizar_comando_with_op(self):
        """Cubre _normalizar_comando con op/data 123-131"""
        from app.drivers.api.routes import _normalizar_comando
        
        cmd = {"op": "TEST", "data": {"field": "value"}}
        result = _normalizar_comando(cmd, 1)
        
        assert result["op"] == "TEST"
    
    def test_normalizar_comando_with_command(self):
        """Cubre _normalizar_comando con command field"""
        from app.drivers.api.routes import _normalizar_comando
        
        cmd = {"command": "CREATE", "id": "123"}
        result = _normalizar_comando(cmd, 1)
        
        assert result["op"] == "CREATE"
    
    def test_procesar_comando_individual_success(self):
        """Cubre _procesar_comando_individual"""
        from app.drivers.api.routes import _procesar_comando_individual
        
        service = MagicMock()
        orden = MagicMock()
        orden.order_id = "ORD-001"
        evento = MagicMock()
        evento.dict.return_value = {"type": "test"}
        
        service.procesar_comando.return_value = (orden, [evento], None)
        
        orders = {}
        events = []
        errors = []
        
        _procesar_comando_individual(
            {"op": "TEST", "data": {}},
            1, service, orders, events, errors
        )
        
        assert "ORD-001" in orders
        assert len(events) == 1
    
    def test_procesar_comando_individual_with_error(self):
        """Cubre _procesar_comando_individual con error"""
        from app.drivers.api.routes import _procesar_comando_individual
        
        service = MagicMock()
        error = MagicMock()
        error.dict.return_value = {"code": "ERROR"}
        
        service.procesar_comando.return_value = (None, [], error)
        
        orders = {}
        events = []
        errors = []
        
        _procesar_comando_individual(
            {"op": "TEST", "data": {}},
            1, service, orders, events, errors
        )
        
        assert len(errors) == 1
    
    def test_procesar_comando_individual_with_events(self):
        """Cubre _procesar_comando_individual con múltiples eventos"""
        from app.drivers.api.routes import _procesar_comando_individual
        
        service = MagicMock()
        orden = MagicMock()
        orden.order_id = "ORD-002"
        
        evento1 = MagicMock()
        evento1.dict.return_value = {"type": "created"}
        evento2 = MagicMock()
        evento2.dict.return_value = {"type": "authorized"}
        
        service.procesar_comando.return_value = (orden, [evento1, evento2], None)
        
        orders = {}
        events = []
        errors = []
        
        _procesar_comando_individual(
            {"op": "CREATE", "data": {}},
            1, service, orders, events, errors
        )
        
        assert len(events) == 2
