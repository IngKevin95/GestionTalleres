"""Tests para ActionService de aplicación."""
import pytest
from unittest.mock import Mock
from app.application.action_service import ActionService


class TestActionService:
    """Tests para ActionService."""
    
    def test_action_service_import(self):
        """Test importar ActionService."""
        assert ActionService is not None
    
    def test_action_service_callable(self):
        """Test que ActionService es instantiable."""
        # Mock de repositorio y auditoria
        repos_mock = Mock()
        auditoria_mock = Mock()
        
        service = ActionService(repo=repos_mock, auditoria=auditoria_mock)
        assert service is not None
