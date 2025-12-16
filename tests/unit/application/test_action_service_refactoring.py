"""Tests de regresión exhaustivos para ActionService antes de refactoring.

Estos tests validan el comportamiento actual de ActionService.procesar_comando
para asegurar que el refactoring no rompe funcionalidad.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal

from app.application.action_service import ActionService
from app.application.dtos import OrdenDTO, EventoDTO, ErrorDTO
from app.domain.entidades.order import Orden
from app.domain.entidades.service import Servicio
from app.domain.entidades.component import Componente
from app.domain.enums import EstadoOrden, CodigoError
from app.domain.exceptions import ErrorDominio
from app.domain.zona_horaria import ahora


def crear_orden_test(order_id: str, estado: EstadoOrden = EstadoOrden.CREATED):
    """Helper para crear orden de prueba."""
    orden = Orden(
        order_id=order_id,
        cliente="Cliente Test",
        vehiculo="ABC-123",
        fecha_creacion=ahora()
    )
    orden.estado = estado
    return orden


class TestProcesarComandoRegresion:
    """Tests de regresión para procesar_comando."""
    
    def test_create_order_exitoso(self):
        """Test CREATE_ORDER exitoso."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {
                "order_id": "R001",
                "customer": "ACME",
                "vehicle": "ABC-123"
            },
            "ts": "2025-03-01T09:00:00Z"
        }
        
        orden_dto, eventos, error = service.procesar_comando(comando)
        
        assert orden_dto is not None
        assert orden_dto.order_id == "R001"
        assert error is None
    
    def test_add_service_exitoso(self):
        """Test ADD_SERVICE exitoso."""
        repo = Mock()
        auditoria = Mock()
        orden = crear_orden_test("R001", EstadoOrden.CREATED)
        repo.obtener.return_value = orden
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "ADD_SERVICE",
            "data": {
                "order_id": "R001",
                "description": "Servicio test",
                "labor_estimated_cost": "100.00",
                "components": []
            }
        }
        
        orden_dto, eventos, error = service.procesar_comando(comando)
        
        assert orden_dto is not None
        assert error is None
    
    def test_authorize_exitoso(self):
        """Test AUTHORIZE exitoso."""
        repo = Mock()
        auditoria = Mock()
        orden = crear_orden_test("R001", EstadoOrden.DIAGNOSED)
        servicio = Servicio("Test", Decimal("100.00"))
        orden.servicios.append(servicio)
        repo.obtener.return_value = orden
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "AUTHORIZE",
            "data": {"order_id": "R001"},
            "ts": "2025-03-01T09:00:00Z"
        }
        
        orden_dto, eventos, error = service.procesar_comando(comando)
        
        assert orden_dto is not None
        assert orden_dto.authorized_amount is not None
        assert error is None
    
    def test_try_complete_exitoso(self):
        """Test TRY_COMPLETE exitoso."""
        repo = Mock()
        auditoria = Mock()
        orden = crear_orden_test("R001", EstadoOrden.IN_PROGRESS)
        orden.monto_autorizado = Decimal("100.00")
        servicio = Servicio("Test", Decimal("50.00"))
        servicio.completado = True
        servicio.costo_real = Decimal("50.00")
        orden.servicios.append(servicio)
        repo.obtener.return_value = orden
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "TRY_COMPLETE",
            "data": {"order_id": "R001"}
        }
        
        orden_dto, eventos, error = service.procesar_comando(comando)
        
        assert orden_dto is not None
        assert orden_dto.status == EstadoOrden.COMPLETED.value
        assert error is None
    
    def test_try_complete_excede_110_retorna_error(self):
        """Test TRY_COMPLETE que excede 110% retorna error pero actualiza orden."""
        repo = Mock()
        auditoria = Mock()
        orden = crear_orden_test("R001", EstadoOrden.IN_PROGRESS)
        orden.monto_autorizado = Decimal("100.00")
        servicio = Servicio("Test", Decimal("50.00"))
        servicio.completado = True
        servicio.costo_real = Decimal("120.00")
        orden.servicios.append(servicio)
        repo.obtener.return_value = orden
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "TRY_COMPLETE",
            "data": {"order_id": "R001"}
        }
        
        orden_dto, eventos, error = service.procesar_comando(comando)
        
        assert orden_dto is not None
        assert error is not None
        assert error.code == CodigoError.REQUIRES_REAUTH.value
        assert orden_dto.status == EstadoOrden.WAITING_FOR_APPROVAL.value
    
    def test_operacion_desconocida_retorna_error(self):
        """Test que operación desconocida retorna error."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "OPERACION_INVALIDA",
            "data": {"order_id": "R001"}
        }
        
        orden_dto, eventos, error = service.procesar_comando(comando)
        
        assert orden_dto is None
        assert error is not None
        assert error.code == CodigoError.INVALID_OPERATION.value
    
    def test_order_id_numerico_se_convierte_a_string(self):
        """Test que order_id numérico se convierte a string."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {
                "order_id": 123,
                "customer": "ACME",
                "vehicle": "ABC-123"
            }
        }
        
        orden_dto, eventos, error = service.procesar_comando(comando)
        
        repo.obtener.assert_called()
        call_args = repo.obtener.call_args[0][0] if repo.obtener.called else None
        if call_args:
            assert isinstance(call_args, str)
    
    def test_eventos_anteriores_se_preservan(self):
        """Test que eventos anteriores se preservan correctamente."""
        repo = Mock()
        auditoria = Mock()
        orden = crear_orden_test("R001", EstadoOrden.CREATED)
        orden._agregar_evento("EVENTO_ANTERIOR")
        repo.obtener.return_value = orden
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "SET_STATE_DIAGNOSED",
            "data": {"order_id": "R001"}
        }
        
        orden_dto, eventos, error = service.procesar_comando(comando)
        
        assert len(orden_dto.events) > 1
        assert any(e.type == "EVENTO_ANTERIOR" for e in orden_dto.events)
        assert any(e.type == "DIAGNOSED" for e in orden_dto.events)
    
    def test_solo_nuevos_eventos_se_retornan(self):
        """Test que solo se retornan eventos nuevos, no los anteriores."""
        repo = Mock()
        auditoria = Mock()
        orden = crear_orden_test("R001", EstadoOrden.CREATED)
        orden._agregar_evento("EVENTO_ANTERIOR")
        evts_ant = len(orden.eventos)
        repo.obtener.return_value = orden
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "SET_STATE_DIAGNOSED",
            "data": {"order_id": "R001"}
        }
        
        orden_dto, eventos, error = service.procesar_comando(comando)
        
        assert len(eventos) == 1
        assert eventos[0].type == "DIAGNOSED"
    
    def test_error_dominio_se_maneja_correctamente(self):
        """Test que ErrorDominio se maneja y convierte a ErrorDTO."""
        repo = Mock()
        auditoria = Mock()
        orden = crear_orden_test("R001", EstadoOrden.CREATED)
        repo.obtener.return_value = orden
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "AUTHORIZE",
            "data": {"order_id": "R001"}
        }
        
        orden_dto, eventos, error = service.procesar_comando(comando)
        
        assert error is not None
        assert error.code == CodigoError.SEQUENCE_ERROR.value
    
    def test_excepcion_generica_se_maneja(self):
        """Test que excepciones genéricas se manejan correctamente."""
        repo = Mock()
        auditoria = Mock()
        repo.obtener.return_value = None
        
        from app.application.acciones.orden import CrearOrden
        service = ActionService(repo, auditoria)
        
        comando = {
            "op": "CREATE_ORDER",
            "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"}
        }
        
        with patch.object(CrearOrden, 'ejecutar', side_effect=Exception("Error en acción")):
            orden_dto, eventos, error = service.procesar_comando(comando)
        
        assert orden_dto is None
        assert error is not None
        assert error.code == "INTERNAL_ERROR"
    
    def test_todos_los_comandos_estan_soportados(self):
        """Test que todos los comandos requeridos están soportados."""
        repo = Mock()
        auditoria = Mock()
        orden = crear_orden_test("R001", EstadoOrden.CREATED)
        repo.obtener.return_value = orden
        service = ActionService(repo, auditoria)
        
        comandos = [
            "CREATE_ORDER",
            "ADD_SERVICE",
            "SET_STATE_DIAGNOSED",
            "AUTHORIZE",
            "SET_STATE_IN_PROGRESS",
            "SET_REAL_COST",
            "TRY_COMPLETE",
            "REAUTHORIZE",
            "DELIVER",
            "CANCEL"
        ]
        
        for op in comandos:
            comando = {"op": op, "data": {"order_id": "R001"}}
            try:
                orden_dto, eventos, error = service.procesar_comando(comando)
                assert orden_dto is not None or error is not None
            except Exception as e:
                pytest.fail(f"Comando {op} lanzó excepción inesperada: {e}")

