import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime

from app.application.action_service import ActionService
from app.application.dtos import OrdenDTO, EventoDTO, ErrorDTO
from app.domain.exceptions import ErrorDominio
from app.domain.enums import CodigoError, EstadoOrden
from app.domain.entidades import Orden, Evento


def test_action_service_init():
    repo = Mock()
    audit = Mock()
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    assert srv.repo == repo
    assert srv.auditoria == audit


def test_procesar_comando_vacio():
    repo = Mock()
    audit = Mock()
    srv = ActionService(repo=repo, auditoria=audit)
    
    res = srv.procesar_comando({})
    
    assert res is not None
    assert len(res) == 3


def test_procesar_comando_retorna_tupla():
    repo = Mock()
    audit = Mock()
    repo.obtener.return_value = None
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {"op": "UNKNOWN_OP", "data": {}}
    res = srv.procesar_comando(cmd)
    
    assert isinstance(res, tuple)
    assert len(res) == 3


def test_procesar_comando_desconocido():
    repo = Mock()
    audit = Mock()
    repo.obtener.return_value = None
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {"op": "UNKNOWN_OP", "data": {}}
    ord_dto, evts, err = srv.procesar_comando(cmd)
    
    assert ord_dto is None
    assert evts == []
    assert err is not None
    assert "desconocida" in err.message.lower()


def test_procesar_comando_operacion_invalida():
    repo = Mock()
    audit = Mock()
    repo.obtener.return_value = None
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {"op": "INVALID_OPERATION", "data": {}}
    _, _, err = srv.procesar_comando(cmd)
    
    assert err is not None
    assert err.code == CodigoError.INVALID_OPERATION.value


def test_procesar_comando_obtiene_orden():
    repo = Mock()
    audit = Mock()
    
    ord_mock = Mock(spec=Orden)
    ord_mock.eventos = []
    repo.obtener.return_value = ord_mock
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {
        "op": "UNKNOWN_OP",
        "data": {"order_id": "ORD-001"}
    }
    
    srv.procesar_comando(cmd)
    
    repo.obtener.assert_called_with("ORD-001")


def test_procesar_comando_cuenta_eventos():
    repo = Mock()
    audit = Mock()
    
    ord_mock = Mock(spec=Orden)
    evt1 = Mock(spec=Evento)
    evt2 = Mock(spec=Evento)
    ord_mock.eventos = [evt1, evt2]
    repo.obtener.return_value = ord_mock
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {
        "op": "UNKNOWN_OP",
        "data": {"order_id": "ORD-001"}
    }
    
    res = srv.procesar_comando(cmd)
    assert res is not None


def test_procesar_comando_error_dominio():
    repo = Mock()
    audit = Mock()
    repo.obtener.return_value = None
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {
        "op": "CREATE_ORDER",
        "data": {"order_id": "ORD-001"},
        "ts": datetime.now().isoformat()
    }
    
    with patch('app.application.action_service.CrearOrden') as mock_action:
        mock_action.return_value.ejecutar.side_effect = ErrorDominio(
            codigo=CodigoError.ORDER_NOT_FOUND,
            mensaje="Orden no encontrada"
        )
        
        res = srv.procesar_comando(cmd)
        
        assert res is not None
        _, _, err = res
        assert err is not None


def test_procesar_comando_exception():
    repo = Mock()
    audit = Mock()
    repo.obtener.return_value = None
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {
        "op": "CREATE_ORDER",
        "data": {},
        "ts": datetime.now().isoformat()
    }
    
    with patch('app.application.action_service.CrearOrden') as mock_action:
        mock_action.return_value.ejecutar.side_effect = Exception("Error genérico")
        
        res = srv.procesar_comando(cmd)
        
        _, _, err = res
        assert err is not None
        assert err.code in ["INTERNAL_ERROR", "SEQUENCE_ERROR", "INVALID_OPERATION"]


def test_procesar_comando_reauth_con_orden():
    repo = Mock()
    audit = Mock()
    
    ord_mock = Mock(spec=Orden)
    evt_mock = Mock(spec=Evento)
    ord_mock.eventos = [evt_mock]
    repo.obtener.return_value = ord_mock
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {
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
            mock_ord_dto = Mock()
            mock_ord_dto.events = [Mock()]
            mock_mapper.return_value = mock_ord_dto
            
            res = srv.procesar_comando(cmd)
            
            _, _, err = res
            assert err is not None


def test_procesar_comando_reauth_sin_orden():
    repo = Mock()
    audit = Mock()
    repo.obtener.return_value = None
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {
        "op": "SET_REAL_COST",
        "data": {"order_id": "ORD-001"},
        "ts": datetime.now().isoformat()
    }
    
    with patch('app.application.action_service.EstablecerCostoReal') as mock_action:
        mock_action.return_value.ejecutar.side_effect = ErrorDominio(
            codigo=CodigoError.REQUIRES_REAUTH,
            mensaje="Requiere reautorización"
        )
        
        res = srv.procesar_comando(cmd)
        
        _, _, err = res
        assert err is not None
        assert err.code == CodigoError.REQUIRES_REAUTH.value


def test_procesar_comando_nuevos_eventos():
    repo = Mock()
    audit = Mock()
    
    ord_mock = Mock(spec=Orden)
    evt1 = Mock(spec=Evento)
    evt2 = Mock(spec=Evento)
    evt3 = Mock(spec=Evento)
    ord_mock.eventos = [evt1, evt2, evt3]
    repo.obtener.return_value = ord_mock
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {
        "op": "UNKNOWN_OP",
        "data": {"order_id": "ORD-001"}
    }
    
    res = srv.procesar_comando(cmd)
    
    assert res is not None


def test_procesar_comando_error_sin_eventos():
    repo = Mock()
    audit = Mock()
    repo.obtener.return_value = None
    
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {
        "op": "UNKNOWN_OP",
        "data": {}
    }
    
    _, _, _ = srv.procesar_comando(cmd)


def test_procesar_comando_sin_op():
    repo = Mock()
    audit = Mock()
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {"data": {}}
    res = srv.procesar_comando(cmd)
    
    assert isinstance(res, tuple)
    assert len(res) == 3


def test_procesar_comando_con_ts():
    repo = Mock()
    repo.obtener.return_value = None
    audit = Mock()
    srv = ActionService(repo=repo, auditoria=audit)
    
    ts = datetime.now()
    cmd = {"op": "test_op", "data": {}, "ts": ts}
    res = srv.procesar_comando(cmd)
    
    assert isinstance(res, tuple)


def test_procesar_comando_order_id_int():
    repo = Mock()
    repo.obtener.return_value = None
    audit = Mock()
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {"op": "UNKNOWN_OP", "data": {"order_id": 123}}
    res = srv.procesar_comando(cmd)
    
    repo.obtener.assert_called_with("123")
    assert isinstance(res, tuple)


def test_procesar_comando_order_id_float():
    repo = Mock()
    repo.obtener.return_value = None
    audit = Mock()
    srv = ActionService(repo=repo, auditoria=audit)
    
    cmd = {"op": "UNKNOWN_OP", "data": {"order_id": 123.5}}
    res = srv.procesar_comando(cmd)
    
    repo.obtener.assert_called_with("123.5")
    assert isinstance(res, tuple)


def test_procesar_comando_create_order():
    repo = Mock()
    repo.obtener.return_value = None
    audit = Mock()
    
    ord_mock = Mock()
    ord_mock.eventos = []
    ord_dto_mock = Mock()
    ord_dto_mock.events = []
    
    with patch('app.application.action_service.CrearOrden') as mock_crear:
        mock_crear.return_value.ejecutar.return_value = ord_dto_mock
        
        srv = ActionService(repo=repo, auditoria=audit)
        cmd = {
            "op": "CREATE_ORDER",
            "data": {"customer": "Juan", "vehicle": "ABC-123"},
            "ts": datetime.now().isoformat()
        }
        
        res = srv.procesar_comando(cmd)
        
        assert res is not None
        ord_dto, evts, err = res
        assert ord_dto is not None
        assert err is None


def test_procesar_comando_add_service():
    repo = Mock()
    ord_mock = Mock()
    ord_mock.eventos = []
    repo.obtener.return_value = ord_mock
    audit = Mock()
    
    ord_dto_mock = Mock()
    ord_dto_mock.events = []
    
    with patch('app.application.action_service.AgregarServicio') as mock_add:
        mock_add.return_value.ejecutar.return_value = ord_dto_mock
        
        srv = ActionService(repo=repo, auditoria=audit)
        cmd = {
            "op": "ADD_SERVICE",
            "data": {"order_id": "ORD-001", "service": {"description": "Test"}}
        }
        
        res = srv.procesar_comando(cmd)
        assert res is not None


def test_procesar_comando_authorize():
    repo = Mock()
    ord_mock = Mock()
    ord_mock.eventos = []
    repo.obtener.return_value = ord_mock
    audit = Mock()
    
    ord_dto_mock = Mock()
    ord_dto_mock.events = []
    
    with patch('app.application.action_service.Autorizar') as mock_auth:
        mock_auth.return_value.ejecutar.return_value = ord_dto_mock
        
        srv = ActionService(repo=repo, auditoria=audit)
        cmd = {
            "op": "AUTHORIZE",
            "data": {"order_id": "ORD-001"},
            "ts": datetime.now().isoformat()
        }
        
        res = srv.procesar_comando(cmd)
        assert res is not None


def test_procesar_comando_set_state_diagnosed():
    repo = Mock()
    ord_mock = Mock()
    ord_mock.eventos = []
    repo.obtener.return_value = ord_mock
    audit = Mock()
    
    ord_dto_mock = Mock()
    ord_dto_mock.events = []
    
    with patch('app.application.action_service.EstablecerEstadoDiagnosticado') as mock_state:
        mock_state.return_value.ejecutar.return_value = ord_dto_mock
        
        srv = ActionService(repo=repo, auditoria=audit)
        cmd = {"op": "SET_STATE_DIAGNOSED", "data": {"order_id": "ORD-001"}}
        
        res = srv.procesar_comando(cmd)
        assert res is not None


def test_procesar_comando_set_state_in_progress():
    repo = Mock()
    ord_mock = Mock()
    ord_mock.eventos = []
    repo.obtener.return_value = ord_mock
    audit = Mock()
    
    ord_dto_mock = Mock()
    ord_dto_mock.events = []
    
    with patch('app.application.action_service.EstablecerEstadoEnProceso') as mock_state:
        mock_state.return_value.ejecutar.return_value = ord_dto_mock
        
        srv = ActionService(repo=repo, auditoria=audit)
        cmd = {"op": "SET_STATE_IN_PROGRESS", "data": {"order_id": "ORD-001"}}
        
        res = srv.procesar_comando(cmd)
        assert res is not None


def test_procesar_comando_try_complete():
    repo = Mock()
    ord_mock = Mock()
    ord_mock.eventos = []
    repo.obtener.return_value = ord_mock
    audit = Mock()
    
    ord_dto_mock = Mock()
    ord_dto_mock.events = []
    
    with patch('app.application.action_service.IntentarCompletar') as mock_complete:
        mock_complete.return_value.ejecutar.return_value = ord_dto_mock
        
        srv = ActionService(repo=repo, auditoria=audit)
        cmd = {"op": "TRY_COMPLETE", "data": {"order_id": "ORD-001"}}
        
        res = srv.procesar_comando(cmd)
        assert res is not None


def test_procesar_comando_deliver():
    repo = Mock()
    ord_mock = Mock()
    ord_mock.eventos = []
    repo.obtener.return_value = ord_mock
    audit = Mock()
    
    ord_dto_mock = Mock()
    ord_dto_mock.events = []
    
    with patch('app.application.action_service.EntregarOrden') as mock_deliver:
        mock_deliver.return_value.ejecutar.return_value = ord_dto_mock
        
        srv = ActionService(repo=repo, auditoria=audit)
        cmd = {"op": "DELIVER", "data": {"order_id": "ORD-001"}}
        
        res = srv.procesar_comando(cmd)
        assert res is not None


def test_procesar_comando_cancel():
    repo = Mock()
    ord_mock = Mock()
    ord_mock.eventos = []
    repo.obtener.return_value = ord_mock
    audit = Mock()
    
    ord_dto_mock = Mock()
    ord_dto_mock.events = []
    
    with patch('app.application.action_service.CancelarOrden') as mock_cancel:
        mock_cancel.return_value.ejecutar.return_value = ord_dto_mock
        
        srv = ActionService(repo=repo, auditoria=audit)
        cmd = {"op": "CANCEL", "data": {"order_id": "ORD-001", "reason": "Test"}}
        
        res = srv.procesar_comando(cmd)
        assert res is not None
