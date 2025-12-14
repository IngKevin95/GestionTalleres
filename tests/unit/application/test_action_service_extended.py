"""Tests extendidos para ActionService para mejorar cobertura."""
import pytest
from unittest.mock import Mock
from datetime import datetime
from app.application.action_service import ActionService


class TestActionServiceProcessCommands:
    """Tests simples para procesar_comando."""
    
    def test_procesar_comando_con_orden_existente(self):
        """Test procesar comando con orden existente en repo."""
        repo_mock = Mock()
        orden_mock = Mock()
        orden_mock.eventos = []
        repo_mock.obtener.return_value = orden_mock
        
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        comando = {
            "op": "UNKNOWN",
            "data": {"order_id": "ORD-001"},
            "ts": datetime.now()
        }
        
        result = service.procesar_comando(comando)
        
        assert isinstance(result, tuple)
        assert len(result) == 3
        # Debe haber error por operación desconocida
        assert result[2] is not None
    
    def test_procesar_comando_sin_order_id(self):
        """Test procesar comando sin order_id."""
        repo_mock = Mock()
        repo_mock.obtener.return_value = None
        
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        comando = {
            "op": "UNKNOWN",
            "data": {},
            "ts": datetime.now()
        }
        
        result = service.procesar_comando(comando)
        
        assert isinstance(result, tuple)
        assert result[2] is not None  # Error por operación desconocida
    
    def test_procesar_comando_vacio(self):
        """Test procesar comando vacío."""
        repo_mock = Mock()
        repo_mock.obtener.return_value = None
        
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        comando = {}
        
        result = service.procesar_comando(comando)
        
        assert isinstance(result, tuple)
        assert len(result) == 3


class TestActionServiceOperations:
    """Tests de operaciones básicas."""
    
    def test_action_service_tiene_repo_y_auditoria(self):
        """Test que ActionService tiene repo y auditoria."""
        repo_mock = Mock()
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        assert service.repo == repo_mock
        assert service.auditoria == auditoria_mock
    
    def test_procesar_comando_retorna_tupla(self):
        """Test que procesar_comando siempre retorna tupla."""
        repo_mock = Mock()
        repo_mock.obtener.return_value = None
        auditoria_mock = Mock()
        service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
        
        comando = {"op": "UNKNOWN", "data": {}}
        result = service.procesar_comando(comando)
        
        assert isinstance(result, tuple)
        assert len(result) == 3
