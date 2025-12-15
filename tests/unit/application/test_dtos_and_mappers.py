import pytest
from app.application.dtos import CrearOrdenDTO, AgregarServicioDTO
from app.application.mappers import crear_orden_dto
from decimal import Decimal


class TestCrearOrdenDTO:
    def test_crear_orden_dto_existe(self):
        from app.application.dtos import CrearOrdenDTO
        assert CrearOrdenDTO is not None


class TestAgregarServicioDTO:
    def test_agregar_servicio_dto_existe(self):
        from app.application.dtos import AgregarServicioDTO
        assert AgregarServicioDTO is not None


class TestCrearOrdenMapper:
    def test_crear_orden_dto_callable(self):
        assert callable(crear_orden_dto)
    
    def test_crear_orden_dto_basico(self):
        data = {
            "order_id": "ORD-001",
            "customer": "Juan",
            "vehicle": "Toyota"
        }
        resultado = crear_orden_dto(data)
        assert resultado is not None
        assert resultado.order_id == "ORD-001"
