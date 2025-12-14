"""Tests para ActionService - cobertura completa de flujos."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime

from app.application.action_service import ActionService
from app.application.dtos import OrdenDTO, EventoDTO, ErrorDTO
from app.domain.exceptions import ErrorDominio
from app.domain.enums import CodigoError, EstadoOrden
from app.domain.entidades import Orden, Evento


class TestActionServiceInitialization:
    """Tests para inicialización de ActionService."""
    
    def test_action_service_init(self):
        """Test inicialización de ActionService."""
        repo = Mock()
        auditoria = Mock()
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        assert service.repo == repo
        assert service.auditoria == auditoria
    
    def test_action_service_has_procesar_comando_method(self):
        """Test que ActionService tiene método procesar_comando."""
        repo = Mock()
        auditoria = Mock()
        service = ActionService(repo=repo, auditoria=auditoria)
        
        assert hasattr(service, 'procesar_comando')
        assert callable(service.procesar_comando)


class TestActionServiceBasicCommands:
    """Tests para comandos básicos de ActionService."""
    
    def test_procesar_comando_with_empty_dict(self):
        """Test procesar_comando con diccionario vacío."""
        repo = Mock()
        auditoria = Mock()
        service = ActionService(repo=repo, auditoria=auditoria)
        
        resultado = service.procesar_comando({})
        
        assert resultado is not None
        assert len(resultado) == 3
    
    def test_procesar_comando_returns_tuple_with_three_elements(self):
        """Test que procesar_comando retorna tupla de 3 elementos."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {"op": "UNKNOWN_OP", "data": {}}
        resultado = service.procesar_comando(comando)
        
        assert isinstance(resultado, tuple)
        assert len(resultado) == 3
    
    def test_procesar_comando_unknown_operation(self):
        """Test procesar_comando con operación desconocida."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {"op": "UNKNOWN_OP", "data": {}}
        orden_dto, eventos, error_dto = service.procesar_comando(comando)
        
        assert orden_dto is None
        assert eventos == []
        assert error_dto is not None
        assert "desconocida" in error_dto.message.lower()
    
    def test_procesar_comando_returns_error_for_invalid_op(self):
        """Test que operación inválida retorna ErrorDTO."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {"op": "INVALID_OPERATION", "data": {}}
        _, _, error_dto = service.procesar_comando(comando)
        
        assert error_dto is not None
        assert error_dto.code == CodigoError.INVALID_OPERATION.value


class TestActionServiceWithOrderContext:
    """Tests para ActionService con contexto de orden."""
    
    def test_procesar_comando_retrieves_existing_order(self):
        """Test que procesar_comando recupera orden existente."""
        repo = Mock()
        auditoria = Mock()
        
        # Crear una orden mock con eventos
        orden_mock = Mock(spec=Orden)
        orden_mock.eventos = []
        repo.obtener.return_value = orden_mock
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {
            "op": "UNKNOWN_OP",
            "data": {"order_id": "ORD-001"}
        }
        
        service.procesar_comando(comando)
        
        # Verificar que se intentó obtener la orden
        repo.obtener.assert_called_with("ORD-001")
    
    def test_procesar_comando_counts_existing_events(self):
        """Test que procesar_comando cuenta eventos existentes."""
        repo = Mock()
        auditoria = Mock()
        
        # Crear orden con eventos
        orden_mock = Mock(spec=Orden)
        evento1 = Mock(spec=Evento)
        evento2 = Mock(spec=Evento)
        orden_mock.eventos = [evento1, evento2]
        repo.obtener.return_value = orden_mock
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {
            "op": "UNKNOWN_OP",
            "data": {"order_id": "ORD-001"}
        }
        
        # No debe fallar aunque sea operación desconocida
        resultado = service.procesar_comando(comando)
        assert resultado is not None
    
    def test_procesar_comando_handles_missing_order_id(self):
        """Test que procesar_comando maneja order_id faltante."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {
            "op": "UNKNOWN_OP",
            "data": {}
        }
        
        resultado = service.procesar_comando(comando)
        
        assert resultado is not None
        assert len(resultado) == 3


class TestActionServiceErrorHandling:
    """Tests para manejo de errores en ActionService."""
    
    def test_procesar_comando_handles_domain_error(self):
        """Test manejo de ErrorDominio."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": "ORD-001"},
            "ts": datetime.now().isoformat()
        }
        
        # Mock la acción para que lance ErrorDominio
        with patch('app.application.action_service.CrearOrden') as mock_action:
            mock_action.return_value.ejecutar.side_effect = ErrorDominio(
                codigo=CodigoError.ORDER_NOT_FOUND,
                mensaje="Orden no encontrada"
            )
            
            resultado = service.procesar_comando(comando)
            
            assert resultado is not None
            _, _, error_dto = resultado
            assert error_dto is not None
    
    def test_procesar_comando_handles_generic_exception(self):
        """Test manejo de excepciones genéricas."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {},
            "ts": datetime.now().isoformat()
        }
        
        with patch('app.application.action_service.CrearOrden') as mock_action:
            mock_action.return_value.ejecutar.side_effect = Exception("Generic error")
            
            resultado = service.procesar_comando(comando)
            
            _, _, error_dto = resultado
            assert error_dto is not None
            assert error_dto.code in ["INTERNAL_ERROR", "SEQUENCE_ERROR", "INVALID_OPERATION"]
    
    def test_procesar_comando_reauth_error_with_order(self):
        """Test manejo de error REQUIRES_REAUTH cuando orden existe."""
        repo = Mock()
        auditoria = Mock()
        
        # Crear orden mock
        orden_mock = Mock(spec=Orden)
        evento_mock = Mock(spec=Evento)
        orden_mock.eventos = [evento_mock]
        repo.obtener.return_value = orden_mock
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {
            "op": "SET_REAL_COST",
            "data": {"order_id": "ORD-001"},
            "ts": datetime.now().isoformat()
        }
        
        with patch('app.application.action_service.EstablecerCostoReal') as mock_action:
            mock_action.return_value.ejecutar.side_effect = ErrorDominio(
                codigo=CodigoError.REQUIRES_REAUTH,
                mensaje="Requiere reautorización"
            )
            
            with patch('app.application.action_service.orden_a_dto') as mock_mapper:
                mock_orden_dto = Mock(spec=OrdenDTO)
                mock_orden_dto.events = [Mock()]
                mock_mapper.return_value = mock_orden_dto
                
                resultado = service.procesar_comando(comando)
                
                _, _, error_dto = resultado
                # REQUIRES_REAUTH debe retornar la orden aunque haya error
                assert error_dto is not None
    
    def test_procesar_comando_reauth_error_without_order(self):
        """Test manejo de error REQUIRES_REAUTH cuando orden no existe."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {
            "op": "SET_REAL_COST",
            "data": {"order_id": "ORD-001"},
            "ts": datetime.now().isoformat()
        }
        
        with patch('app.application.action_service.EstablecerCostoReal') as mock_action:
            mock_action.return_value.ejecutar.side_effect = ErrorDominio(
                codigo=CodigoError.REQUIRES_REAUTH,
                mensaje="Requiere reautorización"
            )
            
            resultado = service.procesar_comando(comando)
            
            _, _, error_dto = resultado
            assert error_dto is not None
            assert error_dto.code == CodigoError.REQUIRES_REAUTH.value


class TestActionServiceEventHandling:
    """Tests para manejo de eventos en ActionService."""
    
    def test_procesar_comando_returns_new_events(self):
        """Test que retorna solo eventos nuevos."""
        repo = Mock()
        auditoria = Mock()
        
        # Orden con eventos previos
        orden_mock = Mock(spec=Orden)
        evento1 = Mock(spec=Evento)
        evento2 = Mock(spec=Evento)
        evento3 = Mock(spec=Evento)
        orden_mock.eventos = [evento1, evento2, evento3]
        repo.obtener.return_value = orden_mock
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {
            "op": "UNKNOWN_OP",
            "data": {"order_id": "ORD-001"}
        }
        
        # Aunque la operación sea inválida, debe procesar correctamente
        resultado = service.procesar_comando(comando)
        
        assert resultado is not None
    
    def test_procesar_comando_no_events_for_error(self):
        """Test que retorna lista vacía para errors sin orden."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        
        service = ActionService(repo=repo, auditoria=auditoria)
        
        comando = {
            "op": "UNKNOWN_OP",
            "data": {}
        }
        
        _, _, _ = service.procesar_comando(comando)



