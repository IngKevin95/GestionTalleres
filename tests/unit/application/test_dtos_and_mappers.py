"""Tests para DTOs y mappers de aplicación."""
import pytest
from app.application.dtos import CrearOrdenDTO, AgregarServicioDTO
from app.application.mappers import json_a_crear_orden_dto
from decimal import Decimal


class TestCrearOrdenDTO:
    """Tests para DTO CrearOrdenDTO."""
    
    def test_crear_orden_dto_existe(self):
        """Test que CrearOrdenDTO existe."""
        from app.application.dtos import CrearOrdenDTO


class TestAgregarServicioDTO:
    """Tests para DTO AgregarServicioDTO."""
    
    def test_agregar_servicio_dto_existe(self):
        """Test que AgregarServicioDTO existe."""
        from app.application.dtos import AgregarServicioDTO


class TestJsonACrearOrdenMapper:
    """Tests para mapper json_a_crear_orden_dto."""
    
    def test_json_a_crear_orden_dto_callable(self):
        """Test que mapper es callable."""
        assert callable(json_a_crear_orden_dto)
    
    def test_json_a_crear_orden_dto_basico(self):
        """Test mapear JSON básico a DTO."""
        json_data = {
            "order_id": "ORD-001",
            "customer": "Juan",
            "vehicle": "Toyota"
        }
        resultado = json_a_crear_orden_dto(json_data)
        assert resultado is not None
