"""Tests adicionales para aumentar cobertura de repositorio_cliente.py"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from app.infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
from app.infrastructure.models.cliente_model import ClienteModel
from app.domain.entidades import Cliente



class TestRepositorioClienteSQLCoverage:
    """Tests para cubrir métodos faltantes en RepositorioClienteSQL"""
    
    def test_buscar_o_crear_por_nombre_existente(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        cliente_existente = Cliente(nombre="Juan", id_cliente=1)
        repo.buscar_por_nombre = Mock(return_value=cliente_existente)
        
        resultado = repo.buscar_o_crear_por_nombre("Juan")
        assert resultado == cliente_existente
        sesion.add.assert_not_called()
    
    def test_buscar_o_crear_por_nombre_nuevo(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        repo.buscar_por_nombre = Mock(return_value=None)
        
        modelo_mock = Mock()
        modelo_mock.id_cliente = 1
        sesion.add = Mock()
        sesion.flush = Mock()
        sesion.commit = Mock()
        
        ClienteModel_mock = Mock(return_value=modelo_mock)
        with patch('app.infrastructure.repositories.repositorio_cliente.ClienteModel', ClienteModel_mock):
            resultado = repo.buscar_o_crear_por_nombre("Juan")
            assert resultado.nombre == "Juan"
            assert resultado.id_cliente == 1
    
    def test_buscar_o_crear_por_nombre_error(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        repo.buscar_por_nombre = Mock(return_value=None)
        
        sesion.add = Mock()
        sesion.flush = Mock(side_effect=Exception("Error"))
        sesion.rollback = Mock()
        
        ClienteModel_mock = Mock(return_value=Mock())
        with patch('app.infrastructure.repositories.repositorio_cliente.ClienteModel', ClienteModel_mock):
            with pytest.raises(Exception):
                repo.buscar_o_crear_por_nombre("Juan")
            sesion.rollback.assert_called_once()
    
    def test_buscar_por_identificacion_existente(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        modelo = Mock()
        modelo.nombre = "Juan"
        modelo.id_cliente = 1
        modelo.identificacion = "123"
        modelo.correo = None
        modelo.direccion = None
        modelo.celular = None
        
        query_mock = Mock()
        query_mock.filter.return_value.first.return_value = modelo
        sesion.query.return_value = query_mock
        
        resultado = repo.buscar_por_identificacion("123")
        assert resultado is not None
        assert resultado.identificacion == "123"
    
    def test_buscar_por_identificacion_no_existe(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        query_mock = Mock()
        query_mock.filter.return_value.first.return_value = None
        sesion.query.return_value = query_mock
        
        resultado = repo.buscar_por_identificacion("123")
        assert resultado is None
    
    def test_buscar_por_identificacion_error(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        sesion.query.side_effect = Exception("Error")
        
        resultado = repo.buscar_por_identificacion("123")
        assert resultado is None
    
    def test_buscar_por_nombre_existente(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        modelo = Mock()
        modelo.nombre = "Juan"
        modelo.id_cliente = 1
        modelo.identificacion = None
        modelo.correo = None
        modelo.direccion = None
        modelo.celular = None
        
        query_mock = Mock()
        query_mock.filter.return_value.first.return_value = modelo
        sesion.query.return_value = query_mock
        
        resultado = repo.buscar_por_nombre("Juan")
        assert resultado is not None
        assert resultado.nombre == "Juan"
    
    def test_buscar_por_nombre_error(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        sesion.query.side_effect = Exception("Error")
        
        resultado = repo.buscar_por_nombre("Juan")
        assert resultado is None
    
    def test_buscar_por_criterio_por_id(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        repo.obtener = Mock(return_value=cliente)
        
        resultado = repo.buscar_por_criterio(id_cliente=1)
        assert resultado == cliente
    
    def test_buscar_por_criterio_por_identificacion(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        cliente = Cliente(nombre="Juan", id_cliente=1, identificacion="123")
        repo.buscar_por_identificacion = Mock(return_value=cliente)
        
        resultado = repo.buscar_por_criterio(identificacion="123")
        assert resultado == cliente
    
    def test_buscar_por_criterio_por_nombre(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        repo.buscar_por_nombre = Mock(return_value=cliente)
        
        resultado = repo.buscar_por_criterio(nombre="Juan")
        assert resultado == cliente
    
    def test_buscar_por_criterio_ningun_criterio(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        resultado = repo.buscar_por_criterio()
        assert resultado is None
    
    def test_buscar_o_crear_por_criterio_sin_nombre(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        repo.buscar_por_criterio = Mock(return_value=None)
        
        with pytest.raises(ValueError) as exc:
            repo.buscar_o_crear_por_criterio(nombre=None)
        assert "nombre es requerido" in str(exc.value)
    
    def test_buscar_o_crear_por_criterio_nuevo(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        repo.buscar_por_criterio = Mock(return_value=None)
        
        modelo_mock = Mock()
        modelo_mock.id_cliente = 1
        sesion.add = Mock()
        sesion.flush = Mock()
        sesion.commit = Mock()
        
        modelo_mock = Mock()
        modelo_mock.id_cliente = 1
        # Crear un mock que simule un ClienteModel
        modelo_mock = Mock()
        modelo_mock.nombre = "Juan"
        modelo_mock.id_cliente = 1
        
        ClienteModel_mock = Mock(return_value=modelo_mock)
        sesion.add = Mock()
        sesion.flush = Mock()
        sesion.commit = Mock()
        
        # Mock de buscar_por_criterio para que devuelva None (no existe)
        repo.buscar_por_criterio = Mock(return_value=None)
        
        with patch('app.infrastructure.repositories.repositorio_cliente.ClienteModel', ClienteModel_mock):
            resultado = repo.buscar_o_crear_por_criterio(
                nombre="Juan",
                identificacion="123",
                correo="juan@test.com",
                direccion="Calle 1",
                celular="123456"
            )
            assert resultado.nombre == "Juan"
            assert resultado.id_cliente == 1
            sesion.add.assert_called_once()
            sesion.flush.assert_called_once()
    
    def test_buscar_o_crear_por_criterio_error(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        repo.buscar_por_criterio = Mock(return_value=None)
        
        sesion.add = Mock()
        sesion.flush = Mock(side_effect=Exception("Error"))
        sesion.rollback = Mock()
        
        ClienteModel_mock = Mock(return_value=Mock())
        with patch('app.infrastructure.repositories.repositorio_cliente.ClienteModel', ClienteModel_mock):
            with pytest.raises(Exception):
                repo.buscar_o_crear_por_criterio(nombre="Juan")
            sesion.rollback.assert_called_once()
    
    def test_obtener_existente(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        modelo = Mock()
        modelo.nombre = "Juan"
        modelo.id_cliente = 1
        modelo.identificacion = None
        modelo.correo = None
        modelo.direccion = None
        modelo.celular = None
        
        query_mock = Mock()
        query_mock.filter.return_value.first.return_value = modelo
        sesion.query.return_value = query_mock
        
        resultado = repo.obtener(1)
        assert resultado is not None
        assert resultado.id_cliente == 1
    
    def test_obtener_no_existe(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        query_mock = Mock()
        query_mock.filter.return_value.first.return_value = None
        sesion.query.return_value = query_mock
        
        resultado = repo.obtener(1)
        assert resultado is None
    
    def test_obtener_error(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        sesion.query.side_effect = Exception("Error")
        
        resultado = repo.obtener(1)
        assert resultado is None
    
    def test_listar_exitoso(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        modelo1 = Mock()
        modelo1.nombre = "Juan"
        modelo1.id_cliente = 1
        modelo1.identificacion = None
        modelo1.correo = None
        modelo1.direccion = None
        modelo1.celular = None
        
        modelo2 = Mock()
        modelo2.nombre = "Pedro"
        modelo2.id_cliente = 2
        modelo2.identificacion = None
        modelo2.correo = None
        modelo2.direccion = None
        modelo2.celular = None
        
        query_mock = Mock()
        query_mock.all.return_value = [modelo1, modelo2]
        sesion.query.return_value = query_mock
        
        resultado = repo.listar()
        assert len(resultado) == 2
    
    def test_listar_error(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        sesion.query.side_effect = Exception("Error")
        
        resultado = repo.listar()
        assert len(resultado) == 0
    
    def test_guardar_existente(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        
        modelo = Mock()
        query_mock = Mock()
        query_mock.filter.return_value.first.return_value = modelo
        sesion.query.return_value = query_mock
        sesion.commit = Mock()
        
        repo.guardar(cliente)
        assert modelo.nombre == "Juan"
        sesion.commit.assert_called_once()
    
    def test_guardar_existente_no_encontrado(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        
        query_mock = Mock()
        query_mock.filter.return_value.first.return_value = None
        sesion.query.return_value = query_mock
        sesion.add = Mock()
        sesion.commit = Mock()
        
        ClienteModel_mock = Mock(return_value=Mock())
        with patch('app.infrastructure.repositories.repositorio_cliente.ClienteModel', ClienteModel_mock):
            repo.guardar(cliente)
            sesion.add.assert_called_once()
    
    def test_guardar_nuevo(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        cliente = Cliente(nombre="Juan", id_cliente=None)
        
        modelo_mock = Mock()
        modelo_mock.id_cliente = 1
        ClienteModel_mock = Mock(return_value=modelo_mock)
        
        sesion.add = Mock()
        sesion.flush = Mock()
        sesion.commit = Mock()
        
        with patch('app.infrastructure.repositories.repositorio_cliente.ClienteModel', ClienteModel_mock):
            repo.guardar(cliente)
            assert cliente.id_cliente == 1
            sesion.add.assert_called_once()
    
    def test_guardar_error(self):
        sesion = Mock(spec=Session)
        repo = RepositorioClienteSQL(sesion)
        
        cliente = Cliente(nombre="Juan", id_cliente=1)
        
        query_mock = Mock()
        query_mock.filter.return_value.first.return_value = Mock()
        sesion.query.return_value = query_mock
        sesion.commit = Mock(side_effect=Exception("Error"))
        sesion.rollback = Mock()
        
        with pytest.raises(Exception):
            repo.guardar(cliente)
        sesion.rollback.assert_called_once()

