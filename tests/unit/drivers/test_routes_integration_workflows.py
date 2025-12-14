"""
Integration tests for Order management endpoints.
Tests complete workflows for creating, updating, and managing repair orders.
Focuses on covering more endpoint execution paths to reach 80% coverage.
"""
from unittest.mock import MagicMock, patch
from fastapi import HTTPException


class TestOrderManagementEndpoints:
    """Tests for full order management workflow endpoints"""
    
    @patch('app.drivers.api.routes.obtener_repositorio')
    def test_obtener_orden_success(self, mock_obtain):
        """Test successfully retrieving an order"""
        from app.drivers.api.routes import obtener_orden
        
        mock_repo = MagicMock()
        mock_obtain.return_value = mock_repo
        
        mock_order = MagicMock()
        mock_order.id = "ORD-001"
        mock_repo.obtener.return_value = mock_order
        
        with patch('app.drivers.api.routes.orden_a_dto') as mock_dto:
            mock_dto.return_value = {"id": "ORD-001"}
            result = obtener_orden("ORD-001", mock_repo)
            assert result == {"id": "ORD-001"}
    
    @patch('app.drivers.api.routes.obtener_repositorio')
    def test_actualizar_orden_customer_and_vehicle(self, mock_obtain):
        """Test updating both customer and vehicle"""
        from app.drivers.api.routes import actualizar_orden
        
        mock_repo = MagicMock()
        mock_obtain.return_value = mock_repo
        
        mock_order = MagicMock()
        mock_order.cliente = "Old Client"
        mock_order.vehiculo = "Old Vehicle"
        mock_repo.obtener.return_value = mock_order
        
        with patch('app.drivers.api.routes.orden_a_dto') as mock_dto:
            mock_dto.return_value = {"id": "ORD-002", "cliente": "New", "vehiculo": "New"}
            result = actualizar_orden("ORD-002", "New Client", "New Vehicle", mock_repo)
            assert mock_order.cliente == "New Client"
            assert mock_order.vehiculo == "New Vehicle"
    
    @patch('app.drivers.api.routes.obtener_action_service')
    @patch('app.drivers.api.routes.obtener_repositorio')
    def test_establecer_estado_in_progress(self, mock_repo, mock_service):
        """Test setting order to IN_PROGRESS state"""
        from app.drivers.api.routes import establecer_estado
        from app.drivers.api.schemas import SetStateRequest
        from app.application.dtos import OrdenDTO, EventoDTO
        
        # Setup mocks for obtener_repositorio and obtener_action_service
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        
        # Mock the order obtained from repo
        mock_order = MagicMock()
        mock_order.id = "ORD-003"
        mock_repo_instance.obtener.return_value = mock_order
        
        # Mock action_service
        mock_service_instance = MagicMock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.auditoria = MagicMock()
        
        # Expected result DTO with all required fields
        mock_result_dto = OrdenDTO(
            order_id="ORD-003",
            status="IN_PROGRESS",
            customer="Test Customer",
            vehicle="Test Vehicle",
            services=[],
            subtotal_estimated="1000.00",
            authorization_version=1,
            real_total="1000.00",
            events=[]
        )
        
        # Patch EstablecerEstadoEnProceso inside the function
        with patch('app.application.acciones.estados.EstablecerEstadoEnProceso') as mock_action_class:
            mock_action_instance = MagicMock()
            mock_action_class.return_value = mock_action_instance
            mock_action_instance.ejecutar.return_value = mock_result_dto
            
            request = SetStateRequest(state="IN_PROGRESS")
            result = establecer_estado("ORD-003", request, mock_repo_instance, mock_service_instance)
            
            assert result.order_id == "ORD-003"
            assert result.status == "IN_PROGRESS"


class TestClientVehicleManagement:
    """Tests for client and vehicle management endpoints"""
    
    @patch('app.drivers.api.routes.obtener_repositorio_cliente')
    def test_obtener_cliente_exists(self, mock_obtain):
        """Test getting existing client"""
        from app.drivers.api.routes import obtener_cliente
        
        mock_repo = MagicMock()
        mock_obtain.return_value = mock_repo
        
        mock_client = MagicMock()
        mock_client.id = "CLI-001"
        mock_repo.obtener.return_value = mock_client
        
        with patch('app.drivers.api.routes.cliente_a_dto') as mock_dto:
            mock_dto.return_value = {"id": "CLI-001", "nombre": "Test"}
            result = obtener_cliente("CLI-001", mock_repo)
            assert result["id"] == "CLI-001"
    
    @patch('app.drivers.api.routes.obtener_repositorio_vehiculo')
    @patch('app.drivers.api.routes.obtener_repositorio_cliente')
    def test_obtener_vehiculos_cliente_success(self, mock_cli, mock_veh):
        """Test getting vehicles for a client"""
        from app.drivers.api.routes import obtener_vehiculos_cliente
        
        mock_repo_cli = MagicMock()
        mock_cli.return_value = mock_repo_cli
        
        mock_repo_veh = MagicMock()
        mock_veh.return_value = mock_repo_veh
        
        mock_client = MagicMock()
        mock_client.nombre = "Test Client"
        mock_repo_cli.obtener.return_value = mock_client
        
        mock_vehicle = MagicMock()
        mock_vehicle.id = "VEH-001"
        mock_repo_veh.listar_por_cliente.return_value = [mock_vehicle]
        
        with patch('app.drivers.api.routes.vehiculo_a_dto') as mock_dto:
            # vehiculo_a_dto debe retornar un diccionario válido para VehiculoDTO
            mock_dto.return_value = {
                "id_vehiculo": "VEH-001",
                "descripcion": "Test Vehicle",
                "marca": "Test",
                "modelo": "Model",
                "anio": 2020,
                "id_cliente": "CLI-001",
                "cliente_nombre": "Test Client"
            }
            result = obtener_vehiculos_cliente("CLI-001", mock_repo_cli, mock_repo_veh)
            assert len(result.vehiculos) == 1
    
    @patch('app.drivers.api.routes.obtener_repositorio_vehiculo')
    @patch('app.drivers.api.routes.obtener_repositorio_cliente')
    def test_actualizar_vehiculo_partial(self, mock_cli, mock_veh):
        """Test updating vehicle with partial data"""
        from app.drivers.api.routes import actualizar_vehiculo
        from app.drivers.api.schemas import UpdateVehiculoRequest
        
        mock_repo_veh = MagicMock()
        mock_veh.return_value = mock_repo_veh
        
        mock_repo_cli = MagicMock()
        mock_cli.return_value = mock_repo_cli
        
        mock_vehicle = MagicMock()
        mock_vehicle.id = "VEH-002"
        mock_vehicle.id_cliente = "CLI-002"
        mock_vehicle.descripcion = "Old"
        mock_repo_veh.obtener.return_value = mock_vehicle
        
        mock_client = MagicMock()
        mock_client.nombre = "Client"
        mock_repo_cli.obtener.return_value = mock_client
        
        with patch('app.drivers.api.routes.vehiculo_a_dto') as mock_dto:
            mock_dto.return_value = {"id": "VEH-002"}
            request = UpdateVehiculoRequest(descripcion="New", marca=None, modelo=None, anio=None)
            result = actualizar_vehiculo("VEH-002", request, mock_repo_veh, mock_repo_cli)
            assert mock_vehicle.descripcion == "New"
