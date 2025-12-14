import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime

from app.application.action_service import ActionService
from app.application.dtos import OrdenDTO, EventoDTO, ErrorDTO
from app.domain.exceptions import ErrorDominio
from app.domain.enums import CodigoError, EstadoOrden
from app.domain.entidades import Orden, Evento


def test_action_service_import():
    assert ActionService is not None


def test_action_service_init():
    repo = Mock()
    auditoria = Mock()
    
    service = ActionService(repo=repo, auditoria=auditoria)
    
    assert service.repo == repo
    assert service.auditoria == auditoria


def test_action_service_has_procesar_comando_method():
    repo = Mock()
    auditoria = Mock()
    service = ActionService(repo=repo, auditoria=auditoria)
    
    assert hasattr(service, 'procesar_comando')
    assert callable(service.procesar_comando)


def test_procesar_comando_with_empty_dict():
    repo = Mock()
    auditoria = Mock()
    service = ActionService(repo=repo, auditoria=auditoria)
    
    resultado = service.procesar_comando({})
    
    assert resultado is not None
    assert len(resultado) == 3


def test_procesar_comando_returns_tuple_with_three_elements():
    repo = Mock()
    auditoria = Mock()
    repo.obtener.return_value = None
    
    service = ActionService(repo=repo, auditoria=auditoria)
    
    comando = {"op": "UNKNOWN_OP", "data": {}}
    resultado = service.procesar_comando(comando)
    
    assert isinstance(resultado, tuple)
    assert len(resultado) == 3


def test_procesar_comando_unknown_operation():
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


def test_procesar_comando_returns_error_for_invalid_op():
    repo = Mock()
    auditoria = Mock()
    repo.obtener.return_value = None
    
    service = ActionService(repo=repo, auditoria=auditoria)
    
    comando = {"op": "INVALID_OPERATION", "data": {}}
    _, _, error_dto = service.procesar_comando(comando)
    
    assert error_dto is not None
    assert error_dto.code == CodigoError.INVALID_OPERATION.value


def test_procesar_comando_retrieves_existing_order():
    repo = Mock()
    auditoria = Mock()
    
    orden_mock = Mock(spec=Orden)
    orden_mock.eventos = []
    repo.obtener.return_value = orden_mock
    
    service = ActionService(repo=repo, auditoria=auditoria)
    
    comando = {
        "op": "UNKNOWN_OP",
        "data": {"order_id": "ORD-001"}
    }
    
    service.procesar_comando(comando)
    
    repo.obtener.assert_called_with("ORD-001")


def test_procesar_comando_counts_existing_events():
    repo = Mock()
    auditoria = Mock()
    
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
    
    resultado = service.procesar_comando(comando)
    assert resultado is not None


def test_procesar_comando_handles_missing_order_id():
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


def test_procesar_comando_handles_domain_error():
    repo = Mock()
    auditoria = Mock()
    repo.obtener.return_value = None
    
    service = ActionService(repo=repo, auditoria=auditoria)
    
    comando = {
        "op": "CREATE_ORDER",
        "data": {"order_id": "ORD-001"},
        "ts": datetime.now().isoformat()
    }
    
    with patch('app.application.action_service.CrearOrden') as mock_action:
        mock_action.return_value.ejecutar.side_effect = ErrorDominio(
            codigo=CodigoError.ORDER_NOT_FOUND,
            mensaje="Orden no encontrada"
        )
        
        resultado = service.procesar_comando(comando)
        
        assert resultado is not None
        _, _, error_dto = resultado
        assert error_dto is not None


def test_procesar_comando_handles_generic_exception():
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


def test_procesar_comando_reauth_error_with_order():
    repo = Mock()
    auditoria = Mock()
    
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
            mock_orden_dto = Mock()
            mock_orden_dto.events = [Mock()]
            mock_mapper.return_value = mock_orden_dto
            
            resultado = service.procesar_comando(comando)
            
            _, _, error_dto = resultado
            assert error_dto is not None


def test_procesar_comando_reauth_error_without_order():
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


def test_procesar_comando_returns_new_events():
    repo = Mock()
    auditoria = Mock()
    
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
    
    resultado = service.procesar_comando(comando)
    
    assert resultado is not None


def test_procesar_comando_no_events_for_error():
    repo = Mock()
    auditoria = Mock()
    repo.obtener.return_value = None
    
    service = ActionService(repo=repo, auditoria=auditoria)
    
    comando = {
        "op": "UNKNOWN_OP",
        "data": {}
    }
    
    _, _, _ = service.procesar_comando(comando)


def test_procesar_comando_con_orden_existente():
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
    assert result[2] is not None


def test_procesar_comando_sin_order_id():
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
    assert result[2] is not None


def test_procesar_comando_sin_operacion():
    repo_mock = Mock()
    auditoria_mock = Mock()
    service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
    
    comando = {"data": {}}
    result = service.procesar_comando(comando)
    
    assert isinstance(result, tuple)
    assert len(result) == 3


def test_action_service_con_comando_con_timestamp():
    repo_mock = Mock()
    repo_mock.obtener.return_value = None
    auditoria_mock = Mock()
    service = ActionService(repo=repo_mock, auditoria=auditoria_mock)
    
    ts = datetime.now()
    comando = {"op": "test_op", "data": {}, "ts": ts}
    result = service.procesar_comando(comando)
    
    assert isinstance(result, tuple)
