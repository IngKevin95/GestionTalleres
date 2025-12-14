"""Tests para schemas de API."""
import pytest
from pydantic import ValidationError
from app.drivers.api.schemas import HealthResponse, CommandsRequest, CommandsResponse, SetStateRequest


class TestHealthResponseSchema:
    """Tests para HealthResponse schema."""
    
    def test_health_response_basico(self):
        """Test crear HealthResponse básico."""
        response = HealthResponse(
            status="ok",
            api="operativa",
            database="conectada",
            tablas=["ordenes"],
            tablas_faltantes=[],
            mensaje=None
        )
        assert response.status == "ok"
        assert response.api == "operativa"
    
    def test_health_response_model_dump(self):
        """Test model_dump de HealthResponse."""
        response = HealthResponse(
            status="ok",
            api="operativa",
            database="conectada",
            tablas=[],
            tablas_faltantes=[],
            mensaje=None
        )
        dumped = response.model_dump()
        assert dumped["status"] == "ok"
        assert "api" in dumped


class TestCommandsRequestSchema:
    """Tests para CommandsRequest schema."""
    
    def test_commands_request_valido(self):
        """Test CommandsRequest con datos válidos."""
        request = CommandsRequest(
            commands=[{"command": "CREATE_ORDER", "customer": "Juan"}]
        )
        assert len(request.commands) == 1
    
    def test_commands_request_vacio_falla(self):
        """Test CommandsRequest falla con lista vacía."""
        with pytest.raises(ValidationError):
            CommandsRequest(commands=[])
    
    def test_commands_request_model_dump(self):
        """Test model_dump de CommandsRequest."""
        request = CommandsRequest(
            commands=[{"test": "data"}]
        )
        dumped = request.model_dump()
        assert "commands" in dumped


class TestCommandsResponseSchema:
    """Tests para CommandsResponse schema."""
    
    def test_commands_response_basico(self):
        """Test crear CommandsResponse."""
        response = CommandsResponse(
            orders=[],
            events=[]
        )
        assert response.orders == []
        assert response.events == []


class TestSetStateRequestSchema:
    """Tests para SetStateRequest schema."""
    
    def test_set_state_request_valido(self):
        """Test SetStateRequest con datos válidos."""
        request = SetStateRequest(state="diagnosticado")
        assert request.state == "diagnosticado"
    
    def test_set_state_request_model_json(self):
        """Test SetStateRequest model_dump_json."""
        request = SetStateRequest(state="diagnosticado")
        json_str = request.model_dump_json()
        assert "diagnosticado" in json_str
    
    def test_commands_request_with_multiple_commands(self):
        """Test CommandsRequest con múltiples comandos."""
        request = CommandsRequest(
            commands=[
                {"command": "CREATE_ORDER", "customer": "Juan"},
                {"command": "ADD_SERVICE", "order_id": "ORD-001"}
            ]
        )
        assert len(request.commands) == 2
    
    def test_health_response_model_dump_json(self):
        """Test model_dump_json de HealthResponse."""
        response = HealthResponse(
            status="ok",
            api="operativa",
            database="conectada",
            tablas=["ordenes"],
            tablas_faltantes=[],
            mensaje=None
        )
        json_str = response.model_dump_json()
        assert "ok" in json_str
        assert isinstance(json_str, str)
