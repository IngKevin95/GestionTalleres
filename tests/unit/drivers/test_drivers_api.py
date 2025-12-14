from unittest.mock import Mock, patch
from app.drivers.api.main import app
from app.drivers.api.dependencies import obtener_repositorio, obtener_auditoria, obtener_action_service
from app.drivers.api.schemas import (
    HealthResponse, CommandsRequest
)


def test_obtener_repositorio():
    mock_sesion_obj = Mock()
    
    repo = obtener_repositorio(mock_sesion_obj)
    
    assert repo is not None
    assert hasattr(repo, 'obtener')
    assert hasattr(repo, 'guardar')


def test_obtener_auditoria():
    almacen = obtener_auditoria()
    
    assert almacen is not None
    assert hasattr(almacen, 'registrar')


def test_obtener_action_service():
    mock_repo = Mock()
    mock_auditoria = Mock()
    
    service = obtener_action_service(mock_repo, mock_auditoria)
    
    assert service is not None
    assert service.repo == mock_repo
    assert service.auditoria == mock_auditoria


def test_schemas_health_response():
    response = HealthResponse(
        status="ok",
        api="operativa",
        database="conectada",
        tablas=["ordenes", "clientes"],
        tablas_faltantes=[],
        mensaje=None
    )
    assert response.status == "ok"
    assert response.api == "operativa"
    assert response.database == "conectada"
    assert len(response.tablas) == 2


def test_schemas_commands_request():
    request = CommandsRequest(
        commands=[
            {"op": "CREATE_ORDER", "data": {"customer": "Juan", "vehicle": "Auto"}}
        ]
    )
    assert len(request.commands) == 1
    assert request.commands[0]["op"] == "CREATE_ORDER"


def test_app_creacion():
    assert app is not None
    assert app.title is not None


def test_middleware_basico():
    try:
        from app.drivers.api.middleware import registrar_solicitud
        
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/test"
        
        with patch('app.drivers.api.middleware.obtener_logger') as mock_logger:
            mock_log = Mock()
            mock_logger.return_value = mock_log
            
            registrar_solicitud(mock_request)
            
            mock_log.info.assert_called()
    except ImportError:
        pass

