"""Tests para mejorar cobertura de ActionService."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime
from app.application.action_service import ActionService
from app.application.dtos import OrdenDTO, EventoDTO, ErrorDTO
from app.domain.entidades.order import Orden
from app.domain.entidades.cliente import Cliente
from app.domain.entidades.service import Servicio
from app.domain.enums.order_status import EstadoOrden


class TestActionServiceProcessarComando:
    """Tests para procesar_comando de ActionService."""
    
    def test_procesar_comando_sin_operacion(self):
        """Test procesar comando sin operación."""
        repo_mock = Mock()
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        comando = {"data": {}}
        result = service.procesar_comando(comando)
        
        # Debe retornar tupla de (OrdenDTO, List[EventoDTO], ErrorDTO)
        assert isinstance(result, tuple)
        assert len(result) == 3
    
    def test_procesar_comando_con_orden_no_existente(self):
        """Test procesar comando cuando orden no existe."""
        repo_mock = Mock()
        repo_mock.obtener.return_value = None
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        comando = {
            "op": "crear_orden",
            "data": {"order_id": "ORD-001"},
            "ts": datetime.now()
        }
        result = service.procesar_comando(comando)
        
        assert isinstance(result, tuple)
    
    def test_action_service_repo_y_auditoria_accesibles(self):
        """Test que repo y auditoria están accesibles."""
        repo_mock = Mock()
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        assert service.repo == repo_mock
        assert service.auditoria == auditoria_mock


class TestActionServiceIntegration:
    """Tests de integración para ActionService."""
    
    def test_action_service_con_comando_vacio(self):
        """Test ActionService con comando vacío."""
        repo_mock = Mock()
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        comando = {}
        result = service.procesar_comando(comando)
        
        # No debe lanzar excepción
        assert result is not None
    
    def test_action_service_con_comando_con_timestamp(self):
        """Test ActionService con timestamp en comando."""
        repo_mock = Mock()
        repo_mock.obtener.return_value = None
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        ts = datetime.now()
        comando = {"op": "test_op", "data": {}, "ts": ts}
        result = service.procesar_comando(comando)
        
        assert isinstance(result, tuple)
    
    def test_action_service_procesar_comando_con_error(self):
        """Test que ActionService maneja errores correctamente."""
        repo_mock = Mock()
        # No lanzar error en obtener (que se llama antes del try)
        repo_mock.obtener.return_value = None
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        comando = {"op": "test_op", "data": {"order_id": "ORD-001"}, "ts": datetime.now()}
        
        # Debe retornar una tupla incluso con operación desconocida
        result = service.procesar_comando(comando)
        assert isinstance(result, tuple)
        # Verifica que el ErrorDTO se retorna en la tercera posición
        assert result[2] is not None  # error_dto debe estar presente
