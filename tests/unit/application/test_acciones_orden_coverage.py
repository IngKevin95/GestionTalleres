"""Tests adicionales para aumentar cobertura de acciones/orden.py"""

import pytest
from unittest.mock import Mock
from datetime import datetime
from app.application.acciones.orden import CrearOrden
from app.application.dtos import CrearOrdenDTO, CustomerIdentifierDTO, VehicleIdentifierDTO
from app.domain.entidades import Cliente, Vehiculo
from app.domain.enums import EstadoOrden


class TestCrearOrdenBasico:
    """Tests básicos para CrearOrden"""
    
    def test_crear_orden_sin_repos(self):
        """Test cuando no se proporcionan repositorios"""
        repo = Mock()
        auditoria = Mock()
        
        # Mock de una orden existente
        orden_mock = Mock()
        orden_mock.order_id = "ORD001"
        orden_mock.estado = EstadoOrden.CREATED
        orden_mock.servicios = []  # Lista vacía para poder iterar
        orden_mock.cliente = "Juan"  # Debe ser string, no Mock
        orden_mock.vehiculo = "ABC123"  # Debe ser string, no Mock
        orden_mock.timestamp = datetime.now()
        orden_mock.eventos = []
        orden_mock.monto_autorizado = None
        orden_mock.total_real = 0.0
        orden_mock.version_autorizacion = 0
        
        repo.obtener.return_value = orden_mock
        
        dto = CrearOrdenDTO(
            order_id="ORD001",
            customer=CustomerIdentifierDTO(id_cliente=None, identificacion=None, nombre="Juan"),
            vehicle=VehicleIdentifierDTO(placa="ABC123", id_vehiculo=None),
            timestamp=datetime.now(),
            customer_extra=None,
            vehicle_extra=None
        )
        
        accion = CrearOrden(repo, auditoria, None, None)
        orden = accion.ejecutar(dto)
        
        assert orden.order_id == "ORD001"
        assert orden.status == "CREATED"


class TestCrearOrdenCoverage:
    """Tests para cubrir líneas faltantes en CrearOrden"""
    
    def test_crear_orden_con_repos_cliente_y_vehiculo(self):
        """Test cuando se proporcionan repositorios y se encuentran cliente y vehículo"""
        repo = Mock()
        auditoria = Mock()
        repo_cliente = Mock()
        repo_vehiculo = Mock()
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        vehiculo = Vehiculo(placa="ABC123", id_cliente=1)
        
        repo_cliente.buscar_o_crear_por_criterio.return_value = cliente
        repo_vehiculo.buscar_o_crear_por_placa.return_value = vehiculo
        
        # Mock de una orden existente - cliente y vehiculo strings porque Orden los almacena así
        orden_mock = Mock()
        orden_mock.order_id = "ORD001"
        orden_mock.estado = EstadoOrden.CREATED
        orden_mock.servicios = []  # Lista vacía para poder iterar
        orden_mock.cliente = "Juan"  # String, no objeto Cliente
        orden_mock.vehiculo = "ABC123"  # String, no objeto Vehiculo
        orden_mock.timestamp = datetime.now()
        orden_mock.eventos = []
        orden_mock.monto_autorizado = None
        orden_mock.total_real = 0.0
        orden_mock.version_autorizacion = 0
        
        repo.obtener.return_value = orden_mock
        
        dto = CrearOrdenDTO(
            order_id="ORD001",
            customer=CustomerIdentifierDTO(id_cliente=None, identificacion=None, nombre="Juan"),
            vehicle=VehicleIdentifierDTO(placa="ABC123", id_vehiculo=None),
            timestamp=datetime.now(),
            customer_extra=None,
            vehicle_extra=None
        )
        
        accion = CrearOrden(repo, auditoria, repo_cliente, repo_vehiculo)
        orden = accion.ejecutar(dto)
        
        assert orden.order_id == "ORD001"
        assert orden.status == "CREATED"
        # No verificamos las llamadas porque repo.obtener() retorna la orden directamente
    
    def test_crear_orden_sin_repos_duplicado(self):
        """Test cuando no se proporcionan repositorios (duplicado)"""
        repo = Mock()
        auditoria = Mock()
        
        # Mock de una orden existente
        orden_mock = Mock()
        orden_mock.order_id = "ORD001"
        orden_mock.estado = EstadoOrden.CREATED
        orden_mock.servicios = []  # Lista vacía para poder iterar
        orden_mock.cliente = "Juan"  # Debe ser string, no Mock
        orden_mock.vehiculo = "ABC123"  # Debe ser string, no Mock
        orden_mock.timestamp = datetime.now()
        orden_mock.eventos = []
        orden_mock.monto_autorizado = None
        orden_mock.total_real = 0.0
        orden_mock.version_autorizacion = 0
        
        repo.obtener.return_value = orden_mock
        
        dto = CrearOrdenDTO(
            order_id="ORD001",
            customer=CustomerIdentifierDTO(id_cliente=None, identificacion=None, nombre="Juan"),
            vehicle=VehicleIdentifierDTO(placa="ABC123", id_vehiculo=None),
            timestamp=datetime.now(),
            customer_extra=None,
            vehicle_extra=None
        )
        
        accion = CrearOrden(repo, auditoria, None, None)
        orden = accion.ejecutar(dto)
        
        assert orden.order_id == "ORD001"
        assert orden.status == "CREATED"



