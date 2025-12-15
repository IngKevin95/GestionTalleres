"""Tests adicionales para aumentar cobertura de routes.py"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from decimal import Decimal
from datetime import datetime

from app.drivers.api.routes import (
    router, root, health_check, obtener_cliente_por_criterio,
    obtener_vehiculo_por_criterio, crear_orden, obtener_orden,
    actualizar_orden, establecer_estado, agregar_servicio,
    autorizar_orden, reautorizar_orden, establecer_costo_real,
    intentar_completar_orden, entregar_orden, cancelar_orden,
    listar_clientes, obtener_cliente, crear_cliente,
    actualizar_cliente, listar_vehiculos, obtener_vehiculo,
    crear_vehiculo, actualizar_vehiculo, procesar_comandos,
    _normalizar_comando, _procesar_comando_individual
)
from app.application.dtos import OrdenDTO, CrearOrdenDTO, ServicioDTO, EventoDTO
from app.domain.enums import EstadoOrden, CodigoError
from app.domain.entidades import Orden, Cliente, Vehiculo
from app.domain.exceptions import ErrorDominio
from datetime import datetime
from app.drivers.api.schemas import (
    HealthResponse, CommandsRequest, CreateOrderRequest,
    AddServiceRequest, AuthorizeRequest, ReauthorizeRequest,
    SetRealCostRequest, CancelRequest, SetStateRequest,
    CreateClienteRequest, UpdateClienteRequest, CreateVehiculoRequest,
    UpdateVehiculoRequest, CustomerIdentifier, VehicleIdentifier
)


class TestHealthEndpoint:
    """Tests para endpoint /health"""
    
    @patch('sqlalchemy.inspect')
    @patch('app.infrastructure.db.crear_engine_bd')
    @patch('app.infrastructure.db.obtener_url_bd')
    def test_health_check_exitoso(self, mock_url, mock_engine, mock_inspect):
        mock_url.return_value = "sqlite:///test.db"
        mock_conn = MagicMock()
        mock_engine_instance = MagicMock()
        mock_engine_instance.connect.return_value.__enter__.return_value = mock_conn
        mock_engine.return_value = mock_engine_instance
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ["ordenes", "clientes", "vehiculos", "servicios", "componentes", "eventos"]
        mock_inspect.return_value = mock_inspector
        
        resultado = health_check()
        assert resultado["status"] == "ok"
        assert resultado["database"] == "conectada"
    
    @patch('app.infrastructure.db.crear_engine_bd')
    @patch('app.infrastructure.db.obtener_url_bd')
    def test_health_check_error_conexion(self, mock_url, mock_engine):
        mock_url.return_value = "sqlite:///test.db"
        mock_engine.side_effect = Exception("Error de conexión")
        
        with pytest.raises(HTTPException) as exc:
            health_check()
        assert exc.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    
    @patch('sqlalchemy.inspect')
    @patch('app.infrastructure.db.crear_engine_bd')
    @patch('app.infrastructure.db.obtener_url_bd')
    def test_health_check_tablas_faltantes(self, mock_url, mock_engine, mock_inspect):
        mock_url.return_value = "sqlite:///test.db"
        mock_conn = MagicMock()
        mock_engine_instance = MagicMock()
        mock_engine_instance.connect.return_value.__enter__.return_value = mock_conn
        mock_engine.return_value = mock_engine_instance
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ["ordenes", "clientes"]
        mock_inspect.return_value = mock_inspector
        
        with pytest.raises(HTTPException) as exc:
            health_check()
        assert exc.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestObtenerClientePorCriterio:
    """Tests para función obtener_cliente_por_criterio"""
    
    def test_obtener_cliente_multiples_criterios(self):
        repo = Mock()
        customer = CustomerIdentifier(id_cliente=1, identificacion="123", nombre="Juan")
        
        with pytest.raises(HTTPException) as exc:
            obtener_cliente_por_criterio(customer, repo)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_obtener_cliente_ningun_criterio(self):
        repo = Mock()
        customer = CustomerIdentifier(id_cliente=None, identificacion=None, nombre=None)
        
        with pytest.raises(HTTPException) as exc:
            obtener_cliente_por_criterio(customer, repo)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_obtener_cliente_no_encontrado(self):
        repo = Mock()
        repo.buscar_por_criterio.return_value = None
        customer = CustomerIdentifier(id_cliente=1, identificacion=None, nombre=None)
        
        with pytest.raises(HTTPException) as exc:
            obtener_cliente_por_criterio(customer, repo)
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    
    def test_obtener_cliente_exitoso(self):
        repo = Mock()
        cliente = Cliente(nombre="Juan", id_cliente=1)
        repo.buscar_por_criterio.return_value = cliente
        customer = CustomerIdentifier(id_cliente=1, identificacion=None, nombre=None)
        
        resultado = obtener_cliente_por_criterio(customer, repo)
        assert resultado == cliente


class TestObtenerVehiculoPorCriterio:
    """Tests para función obtener_vehiculo_por_criterio"""
    
    def test_obtener_vehiculo_multiples_criterios(self):
        repo = Mock()
        vehicle = VehicleIdentifier(id_vehiculo=1, placa="ABC123")
        
        with pytest.raises(HTTPException) as exc:
            obtener_vehiculo_por_criterio(vehicle, repo)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_obtener_vehiculo_ningun_criterio(self):
        repo = Mock()
        vehicle = VehicleIdentifier(id_vehiculo=None, placa=None)
        
        with pytest.raises(HTTPException) as exc:
            obtener_vehiculo_por_criterio(vehicle, repo)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_obtener_vehiculo_no_encontrado(self):
        repo = Mock()
        repo.buscar_por_criterio.return_value = None
        vehicle = VehicleIdentifier(id_vehiculo=1, placa=None)
        
        with pytest.raises(HTTPException) as exc:
            obtener_vehiculo_por_criterio(vehicle, repo)
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND


class TestCrearOrdenEndpoint:
    """Tests para endpoint POST /orders"""
    
    @patch('app.application.acciones.orden.CrearOrden')
    @patch('app.application.mappers.crear_orden_dto')
    def test_crear_orden_exitoso(self, mock_dto, mock_crear_orden_class):
        request = CreateOrderRequest(
            customer="Juan",
            vehicle="ABC123",
            order_id="ORD001"
        )
        action_service = Mock()
        action_service.repo = Mock()
        action_service.auditoria = Mock()
        repo_cliente = Mock()
        repo_vehiculo = Mock()
        
        dto_mock = Mock()
        mock_dto.return_value = dto_mock
        
        accion_mock = Mock()
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.CREATED.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="0.00",
            authorized_amount=None,
            authorization_version=0,
            real_total="0.00",
            events=[]
        )
        accion_mock.ejecutar.return_value = orden_dto
        mock_crear_orden_class.return_value = accion_mock
        
        resultado = crear_orden(request, action_service, repo_cliente, repo_vehiculo)
        assert resultado.order_id == "ORD001"
    
    @patch('app.application.acciones.orden.CrearOrden')
    @patch('app.application.mappers.crear_orden_dto')
    def test_crear_orden_error_dominio(self, mock_dto, mock_accion_class):
        request = CreateOrderRequest(
            customer="Juan",
            vehicle="ABC123",
            order_id="ORD001"
        )
        action_service = Mock()
        action_service.repo = Mock()
        action_service.auditoria = Mock()
        repo_cliente = Mock()
        repo_vehiculo = Mock()
        
        dto_mock = Mock()
        mock_dto.return_value = dto_mock
        
        accion_mock = Mock()
        accion_mock.ejecutar.side_effect = ErrorDominio(CodigoError.INVALID_OPERATION, "Error")
        mock_accion_class.return_value = accion_mock
        
        with pytest.raises(HTTPException) as exc:
            crear_orden(request, action_service, repo_cliente, repo_vehiculo)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


class TestObtenerOrdenEndpoint:
    """Tests para endpoint GET /orders/{order_id}"""
    
    @patch('app.drivers.api.routes.orden_a_dto')
    def test_obtener_orden_exitoso(self, mock_mapper):
        repo = Mock()
        orden = Orden("ORD001", "Juan", "ABC123", datetime.now())
        repo.obtener.return_value = orden
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.CREATED.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="0.00",
            authorized_amount=None,
            authorization_version=0,
            real_total="0.00",
            events=[]
        )
        mock_mapper.return_value = orden_dto
        
        resultado = obtener_orden("ORD001", repo)
        assert resultado.order_id == "ORD001"
    
    def test_obtener_orden_no_encontrada(self):
        repo = Mock()
        repo.obtener.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            obtener_orden("ORD001", repo)
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND


class TestActualizarOrdenEndpoint:
    """Tests para endpoint PATCH /orders/{order_id}"""
    
    @patch('app.drivers.api.routes.orden_a_dto')
    def test_actualizar_orden_exitoso(self, mock_mapper):
        repo = Mock()
        orden = Orden("ORD001", "Juan", "ABC123", datetime.now())
        repo.obtener.return_value = orden
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.CREATED.value,
            customer="Pedro",
            vehicle="XYZ789",
            services=[],
            subtotal_estimated="0.00",
            authorized_amount=None,
            authorization_version=0,
            real_total="0.00",
            events=[]
        )
        mock_mapper.return_value = orden_dto
        
        resultado = actualizar_orden("ORD001", "Pedro", "XYZ789", repo)
        assert orden.cliente == "Pedro"
        assert orden.vehiculo == "XYZ789"
    
    def test_actualizar_orden_no_encontrada(self):
        repo = Mock()
        repo.obtener.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            actualizar_orden("ORD001", "Pedro", None, repo)
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND


class TestEstablecerEstadoEndpoint:
    """Tests para endpoint POST /orders/{order_id}/set_state"""
    
    def test_establecer_estado_invalido(self):
        repo = Mock()
        orden = Orden("ORD001", "Juan", "ABC123", datetime.now())
        repo.obtener.return_value = orden
        action_service = Mock()
        request = SetStateRequest(state="INVALID")
        
        with pytest.raises(HTTPException) as exc:
            establecer_estado("ORD001", request, repo, action_service)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    
    @patch('app.application.acciones.estados.EstablecerEstadoDiagnosticado')
    def test_establecer_estado_diagnosticado(self, mock_accion):
        repo = Mock()
        orden = Orden("ORD001", "Juan", "ABC123", datetime.now())
        repo.obtener.return_value = orden
        action_service = Mock()
        action_service.auditoria = Mock()
        request = SetStateRequest(state="DIAGNOSED")
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.DIAGNOSED.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="0.00",
            authorized_amount=None,
            authorization_version=0,
            real_total="0.00",
            events=[]
        )
        accion_mock = Mock()
        accion_mock.ejecutar.return_value = orden_dto
        mock_accion.return_value = accion_mock
        
        resultado = establecer_estado("ORD001", request, repo, action_service)
        assert resultado.status == EstadoOrden.DIAGNOSED.value


class TestAgregarServicioEndpoint:
    """Tests para endpoint POST /orders/{order_id}/services"""
    
    @patch('app.application.acciones.servicios.AgregarServicio')
    @patch('app.application.mappers.agregar_servicio_dto')
    def test_agregar_servicio_exitoso(self, mock_dto, mock_accion_class):
        action_service = Mock()
        action_service.repo = Mock()
        action_service.auditoria = Mock()
        request = AddServiceRequest(
            description="Cambio de aceite",
            labor_estimated_cost=Decimal("500.00"),
            components=[]
        )
        
        dto_mock = Mock()
        mock_dto.return_value = dto_mock
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.CREATED.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="500.00",
            authorized_amount=None,
            authorization_version=0,
            real_total="0.00",
            events=[]
        )
        accion_mock = Mock()
        accion_mock.ejecutar.return_value = orden_dto
        mock_accion_class.return_value = accion_mock
        
        resultado = agregar_servicio("ORD001", request, action_service)
        assert resultado.order_id == "ORD001"
    
    @patch('app.application.acciones.servicios.AgregarServicio')
    @patch('app.application.mappers.agregar_servicio_dto')
    def test_agregar_servicio_error_dominio(self, mock_dto, mock_accion_class):
        action_service = Mock()
        action_service.repo = Mock()
        action_service.auditoria = Mock()
        request = AddServiceRequest(
            description="Cambio de aceite",
            labor_estimated_cost=Decimal("500.00"),
            components=[]
        )
        
        dto_mock = Mock()
        mock_dto.return_value = dto_mock
        
        accion_mock = Mock()
        accion_mock.ejecutar.side_effect = ErrorDominio(CodigoError.ORDER_NOT_FOUND, "Orden no existe")
        mock_accion_class.return_value = accion_mock
        
        with pytest.raises(HTTPException) as exc:
            agregar_servicio("ORD001", request, action_service)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


class TestAutorizarOrdenEndpoint:
    """Tests para endpoint POST /orders/{order_id}/authorize"""
    
    @patch('app.application.acciones.autorizacion.Autorizar')
    @patch('app.application.mappers.autorizar_dto')
    def test_autorizar_orden_exitoso(self, mock_dto, mock_accion_class):
        action_service = Mock()
        action_service.repo = Mock()
        action_service.auditoria = Mock()
        request = AuthorizeRequest(ts=None)
        
        dto_mock = Mock()
        mock_dto.return_value = dto_mock
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.AUTHORIZED.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="500.00",
            authorized_amount="500.00",
            authorization_version=1,
            real_total="0.00",
            events=[]
        )
        accion_mock = Mock()
        accion_mock.ejecutar.return_value = orden_dto
        mock_accion_class.return_value = accion_mock
        
        resultado = autorizar_orden("ORD001", request, action_service)
        assert resultado.status == EstadoOrden.AUTHORIZED.value


class TestReautorizarOrdenEndpoint:
    """Tests para endpoint POST /orders/{order_id}/reauthorize"""
    
    @patch('app.application.acciones.autorizacion.Reautorizar')
    @patch('app.application.mappers.reautorizar_dto')
    def test_reautorizar_orden_exitoso(self, mock_dto, mock_accion_class):
        action_service = Mock()
        action_service.repo = Mock()
        action_service.auditoria = Mock()
        request = ReauthorizeRequest(new_authorized_amount=Decimal("1000.00"), ts=None)
        
        dto_mock = Mock()
        mock_dto.return_value = dto_mock
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.AUTHORIZED.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="500.00",
            authorized_amount="1000.00",
            authorization_version=2,
            real_total="0.00",
            events=[]
        )
        accion_mock = Mock()
        accion_mock.ejecutar.return_value = orden_dto
        mock_accion_class.return_value = accion_mock
        
        resultado = reautorizar_orden("ORD001", request, action_service)
        assert resultado.authorized_amount == "1000.00"


class TestEstablecerCostoRealEndpoint:
    """Tests para endpoint POST /orders/{order_id}/set_real_cost"""
    
    @patch('app.application.acciones.servicios.EstablecerCostoReal')
    @patch('app.application.mappers.costo_real_dto')
    def test_establecer_costo_real_exitoso(self, mock_dto, mock_accion_class):
        action_service = Mock()
        action_service.repo = Mock()
        action_service.auditoria = Mock()
        request = SetRealCostRequest(
            service_id=1,
            service_index=None,
            real_cost=Decimal("800.00"),
            completed=True,
            components_real={}
        )
        
        dto_mock = Mock()
        mock_dto.return_value = dto_mock
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.IN_PROGRESS.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="500.00",
            authorized_amount="500.00",
            authorization_version=1,
            real_total="800.00",
            events=[]
        )
        accion_mock = Mock()
        accion_mock.ejecutar.return_value = orden_dto
        mock_accion_class.return_value = accion_mock
        
        resultado = establecer_costo_real("ORD001", request, action_service)
        assert resultado.real_total == "800.00"


class TestIntentarCompletarOrdenEndpoint:
    """Tests para endpoint POST /orders/{order_id}/try_complete"""
    
    @patch('app.application.acciones.autorizacion.IntentarCompletar')
    @patch('app.application.mappers.intentar_completar_dto')
    def test_intentar_completar_exitoso(self, mock_dto, mock_accion_class):
        action_service = Mock()
        action_service.repo = Mock()
        action_service.auditoria = Mock()
        
        dto_mock = Mock()
        mock_dto.return_value = dto_mock
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.COMPLETED.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="500.00",
            authorized_amount="500.00",
            authorization_version=1,
            real_total="500.00",
            events=[]
        )
        accion_mock = Mock()
        accion_mock.ejecutar.return_value = orden_dto
        mock_accion_class.return_value = accion_mock
        
        resultado = intentar_completar_orden("ORD001", action_service)
        assert resultado.status == EstadoOrden.COMPLETED.value


class TestEntregarOrdenEndpoint:
    """Tests para endpoint POST /orders/{order_id}/deliver"""
    
    @patch('app.application.acciones.orden.EntregarOrden')
    @patch('app.application.mappers.entregar_dto')
    def test_entregar_orden_exitoso(self, mock_dto, mock_accion_class):
        action_service = Mock()
        action_service.repo = Mock()
        action_service.auditoria = Mock()
        
        dto_mock = Mock()
        mock_dto.return_value = dto_mock
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.DELIVERED.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="500.00",
            authorized_amount="500.00",
            authorization_version=1,
            real_total="500.00",
            events=[]
        )
        accion_mock = Mock()
        accion_mock.ejecutar.return_value = orden_dto
        mock_accion_class.return_value = accion_mock
        
        resultado = entregar_orden("ORD001", action_service)
        assert resultado.status == EstadoOrden.DELIVERED.value


class TestCancelarOrdenEndpoint:
    """Tests para endpoint POST /orders/{order_id}/cancel"""
    
    @patch('app.application.acciones.orden.CancelarOrden')
    @patch('app.application.mappers.cancelar_dto')
    def test_cancelar_orden_exitoso(self, mock_dto, mock_accion_class):
        action_service = Mock()
        action_service.repo = Mock()
        action_service.auditoria = Mock()
        request = CancelRequest(reason="Cliente canceló")
        
        dto_mock = Mock()
        mock_dto.return_value = dto_mock
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.CANCELLED.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="500.00",
            authorized_amount=None,
            authorization_version=0,
            real_total="0.00",
            events=[]
        )
        accion_mock = Mock()
        accion_mock.ejecutar.return_value = orden_dto
        mock_accion_class.return_value = accion_mock
        
        resultado = cancelar_orden("ORD001", request, action_service)
        assert resultado.status == EstadoOrden.CANCELLED.value


class TestListarClientesEndpoint:
    """Tests para endpoint GET /customers"""
    
    def test_listar_clientes_exitoso(self):
        repo = Mock()
        cliente1 = Cliente(nombre="Juan", id_cliente=1)
        cliente2 = Cliente(nombre="Pedro", id_cliente=2)
        repo.listar.return_value = [cliente1, cliente2]
        
        resultado = listar_clientes(repo)
        assert len(resultado.clientes) == 2


class TestObtenerClienteEndpoint:
    """Tests para endpoint GET /customers con query params"""
    
    def test_obtener_cliente_exitoso(self):
        repo = Mock()
        cliente = Cliente(nombre="Juan", id_cliente=1)
        repo.buscar_por_criterio.return_value = cliente
        
        resultado = obtener_cliente(1, None, None, repo)
        assert resultado.id_cliente == 1


class TestCrearClienteEndpoint:
    """Tests para endpoint POST /customers"""
    
    def test_crear_cliente_existente_por_identificacion(self):
        repo = Mock()
        cliente_existente = Cliente(nombre="Juan", id_cliente=1, identificacion="123")
        repo.buscar_por_identificacion.return_value = cliente_existente
        
        request = CreateClienteRequest(nombre="Juan", identificacion="123")
        resultado = crear_cliente(request, repo)
        assert resultado.id_cliente == 1
    
    def test_crear_cliente_nuevo(self):
        repo = Mock()
        repo.buscar_por_identificacion.return_value = None
        repo.buscar_por_nombre.return_value = None
        
        nuevo_cliente = Cliente(nombre="Juan", id_cliente=1)
        nuevo_cliente.identificacion = None
        nuevo_cliente.correo = None
        nuevo_cliente.direccion = None
        nuevo_cliente.celular = None
        
        def guardar_side_effect(cliente):
            cliente.id_cliente = 1
        
        repo.guardar = Mock(side_effect=guardar_side_effect)
        
        request = CreateClienteRequest(nombre="Juan")
        resultado = crear_cliente(request, repo)
        assert resultado.nombre == "Juan"
        assert resultado.id_cliente == 1
        repo.guardar.assert_called_once()
    
    def test_crear_cliente_existente_por_nombre(self):
        repo = Mock()
        cliente_existente = Cliente(nombre="Juan", id_cliente=1)
        cliente_existente.identificacion = None
        cliente_existente.correo = None
        cliente_existente.direccion = None
        cliente_existente.celular = None
        repo.buscar_por_identificacion.return_value = None
        repo.buscar_por_nombre.return_value = cliente_existente
        
        request = CreateClienteRequest(nombre="Juan")
        resultado = crear_cliente(request, repo)
        assert resultado.id_cliente == 1


class TestProcesarComandosEndpoint:
    """Tests para endpoint POST /commands"""
    
    def test_procesar_comandos_vacio(self):
        # CommandsRequest no permite lista vacía, así que usamos un request inválido directamente
        request = Mock()
        request.commands = []
        action_service = Mock()
        
        with pytest.raises(HTTPException) as exc:
            procesar_comandos(request, action_service)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_procesar_comandos_mas_de_100(self):
        request = CommandsRequest(commands=[{}] * 101)
        action_service = Mock()
        
        with pytest.raises(HTTPException) as exc:
            procesar_comandos(request, action_service)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


class TestNormalizarComando:
    """Tests para función _normalizar_comando"""
    
    def test_normalizar_comando_con_op_y_data(self):
        comando = {"op": "CREATE_ORDER", "data": {}}
        resultado = _normalizar_comando(comando, 1)
        assert resultado["op"] == "CREATE_ORDER"
    
    def test_normalizar_comando_con_command(self):
        comando = {"command": "CREATE_ORDER", "order_id": "ORD001"}
        resultado = _normalizar_comando(comando, 1)
        assert resultado["op"] == "CREATE_ORDER"
        assert "order_id" in resultado["data"]
    
    def test_normalizar_comando_sin_campos(self):
        comando = {}
        with pytest.raises(HTTPException) as exc:
            _normalizar_comando(comando, 1)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


class TestProcesarComandoIndividual:
    """Tests para función _procesar_comando_individual"""
    
    @patch('app.drivers.api.routes.logger')
    def test_procesar_comando_individual_con_error(self, mock_logger):
        comando = {"op": "CREATE_ORDER", "data": {}}
        action_service = Mock()
        orders_dict = {}
        events = []
        errors = []
        
        orden_dto = OrdenDTO(
            order_id="ORD001",
            status=EstadoOrden.CREATED.value,
            customer="Juan",
            vehicle="ABC123",
            services=[],
            subtotal_estimated="0.00",
            authorized_amount=None,
            authorization_version=0,
            real_total="0.00",
            events=[]
        )
        error_dto = Mock()
        error_dto.model_dump.return_value = {"code": "ERROR"}
        action_service.procesar_comando.return_value = (orden_dto, [], error_dto)
        
        _procesar_comando_individual(comando, 1, action_service, orders_dict, events, errors)
        assert len(errors) == 1
    
    @patch('app.drivers.api.routes.logger')
    def test_procesar_comando_individual_con_excepcion(self, mock_logger):
        comando = {"op": "CREATE_ORDER", "data": {}}
        action_service = Mock()
        action_service.procesar_comando.side_effect = Exception("Error")
        orders_dict = {}
        events = []
        errors = []
        
        with pytest.raises(Exception):
            _procesar_comando_individual(comando, 1, action_service, orders_dict, events, errors)


class TestActualizarClienteEndpoint:
    """Tests para endpoint PATCH /customers"""
    
    def test_actualizar_cliente_exitoso(self):
        repo = Mock()
        cliente = Cliente(nombre="Juan", id_cliente=1)
        repo.buscar_por_criterio.return_value = cliente
        
        request = UpdateClienteRequest(nombre="Pedro", correo="pedro@test.com")
        resultado = actualizar_cliente(1, None, None, request, repo)
        assert resultado.nombre == "Pedro"
        repo.guardar.assert_called_once()


class TestObtenerVehiculosClienteEndpoint:
    """Tests para endpoint GET /customers/vehicles"""
    
    def test_obtener_vehiculos_cliente_exitoso(self):
        repo_cliente = Mock()
        repo_vehiculo = Mock()
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        repo_cliente.buscar_por_criterio.return_value = cliente
        
        vehiculo1 = Vehiculo(placa="ABC123", id_cliente=1, id_vehiculo=1)
        vehiculo2 = Vehiculo(placa="XYZ789", id_cliente=1, id_vehiculo=2)
        repo_vehiculo.listar_por_cliente.return_value = [vehiculo1, vehiculo2]
        
        from app.drivers.api.routes import obtener_vehiculos_cliente
        resultado = obtener_vehiculos_cliente(1, None, None, repo_cliente, repo_vehiculo)
        assert len(resultado.vehiculos) == 2


class TestListarVehiculosEndpoint:
    """Tests para endpoint GET /vehicles"""
    
    def test_listar_vehiculos_exitoso(self):
        repo_vehiculo = Mock()
        repo_cliente = Mock()
        
        vehiculo1 = Vehiculo(placa="ABC123", id_cliente=1, id_vehiculo=1)
        vehiculo2 = Vehiculo(placa="XYZ789", id_cliente=2, id_vehiculo=2)
        repo_vehiculo.listar.return_value = [vehiculo1, vehiculo2]
        
        cliente1 = Cliente(nombre="Juan", id_cliente=1)
        cliente2 = Cliente(nombre="Pedro", id_cliente=2)
        repo_cliente.obtener.side_effect = [cliente1, cliente2]
        
        resultado = listar_vehiculos(repo_vehiculo, repo_cliente)
        assert len(resultado.vehiculos) == 2
    
    def test_listar_vehiculos_cliente_no_encontrado(self):
        repo_vehiculo = Mock()
        repo_cliente = Mock()
        
        vehiculo = Vehiculo(placa="ABC123", id_cliente=1, id_vehiculo=1)
        repo_vehiculo.listar.return_value = [vehiculo]
        repo_cliente.obtener.return_value = None
        
        resultado = listar_vehiculos(repo_vehiculo, repo_cliente)
        assert len(resultado.vehiculos) == 1
        assert resultado.vehiculos[0].cliente_nombre is None


class TestObtenerVehiculoEndpoint:
    """Tests para endpoint GET /vehicles con query params"""
    
    def test_obtener_vehiculo_exitoso(self):
        repo_vehiculo = Mock()
        repo_cliente = Mock()
        
        vehiculo = Vehiculo(placa="ABC123", id_cliente=1, id_vehiculo=1)
        repo_vehiculo.buscar_por_criterio.return_value = vehiculo
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        repo_cliente.obtener.return_value = cliente
        
        resultado = obtener_vehiculo(None, "ABC123", repo_vehiculo, repo_cliente)
        assert resultado.placa == "ABC123"
    
    def test_obtener_vehiculo_cliente_no_encontrado(self):
        repo_vehiculo = Mock()
        repo_cliente = Mock()
        
        vehiculo = Vehiculo(placa="ABC123", id_cliente=1, id_vehiculo=1)
        repo_vehiculo.buscar_por_criterio.return_value = vehiculo
        repo_cliente.obtener.return_value = None
        
        resultado = obtener_vehiculo(None, "ABC123", repo_vehiculo, repo_cliente)
        assert resultado.cliente_nombre is None


class TestCrearVehiculoEndpoint:
    """Tests para endpoint POST /vehicles"""
    
    def test_crear_vehiculo_existente(self):
        repo_vehiculo = Mock()
        repo_cliente = Mock()
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        repo_cliente.buscar_por_criterio.return_value = cliente
        
        vehiculo_existente = Vehiculo(placa="ABC123", id_cliente=1, id_vehiculo=1)
        repo_vehiculo.buscar_por_placa.return_value = vehiculo_existente
        
        cliente_vehiculo = Cliente(nombre="Juan", id_cliente=1)
        repo_cliente.obtener.return_value = cliente_vehiculo
        
        request = CreateVehiculoRequest(
            placa="ABC123",
            customer=CustomerIdentifier(nombre="Juan")
        )
        
        resultado = crear_vehiculo(request, repo_vehiculo, repo_cliente)
        assert resultado.placa == "ABC123"
    
    def test_crear_vehiculo_nuevo(self):
        repo_vehiculo = Mock()
        repo_cliente = Mock()
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        repo_cliente.buscar_por_criterio.return_value = cliente
        repo_vehiculo.buscar_por_placa.return_value = None
        
        nuevo_vehiculo = Vehiculo(placa="ABC123", id_cliente=1)
        nuevo_vehiculo.id_vehiculo = 1
        
        def guardar_side_effect(vehiculo):
            vehiculo.id_vehiculo = 1
        
        repo_vehiculo.guardar.side_effect = guardar_side_effect
        
        request = CreateVehiculoRequest(
            placa="ABC123",
            customer=CustomerIdentifier(nombre="Juan"),
            marca="Toyota",
            modelo="Corolla"
        )
        
        resultado = crear_vehiculo(request, repo_vehiculo, repo_cliente)
        assert resultado.placa == "ABC123"
        repo_vehiculo.guardar.assert_called_once()


class TestActualizarVehiculoEndpoint:
    """Tests para endpoint PATCH /vehicles"""
    
    def test_actualizar_vehiculo_exitoso(self):
        repo_vehiculo = Mock()
        repo_cliente = Mock()
        
        vehiculo = Vehiculo(placa="ABC123", id_cliente=1)
        vehiculo.id_vehiculo = 1
        repo_vehiculo.buscar_por_criterio.return_value = vehiculo
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        repo_cliente.obtener.return_value = cliente
        
        request = UpdateVehiculoRequest(marca="Toyota", modelo="Corolla")
        resultado = actualizar_vehiculo(1, None, request, repo_vehiculo, repo_cliente)
        assert resultado.marca == "Toyota"
        repo_vehiculo.guardar.assert_called_once()
    
    def test_actualizar_vehiculo_customer_string(self):
        repo_vehiculo = Mock()
        repo_cliente = Mock()
        
        vehiculo = Vehiculo(placa="ABC123", id_cliente=1)
        vehiculo.id_vehiculo = 1
        repo_vehiculo.buscar_por_criterio.return_value = vehiculo
        
        cliente_nuevo = Cliente(nombre="Pedro", id_cliente=2)
        repo_cliente.buscar_por_criterio.return_value = cliente_nuevo
        repo_cliente.obtener.return_value = cliente_nuevo
        
        request = UpdateVehiculoRequest(customer="Pedro")
        resultado = actualizar_vehiculo(1, None, request, repo_vehiculo, repo_cliente)
        assert vehiculo.id_cliente == 2


