from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, MagicMock
import pytest
from sqlalchemy.orm import Session
from app.infrastructure.repositories.repositorio_orden import RepositorioOrden
from app.infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
from app.infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
from app.infrastructure.repositories.repositorio_servicio import RepositorioServicioSQL
from app.infrastructure.repositories.repositorio_evento import RepositorioEventoSQL
from app.domain.entidades import Orden, Cliente, Vehiculo, Servicio, Evento, Componente
from app.domain.enums import EstadoOrden, CodigoError
from app.domain.exceptions import ErrorDominio


def test_repositorio_orden_obtener_no_existe():
    sesion = Mock(spec=Session)
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    repo = RepositorioOrden(sesion)
    orden = repo.obtener("ORD-999")
    
    assert orden is None

def test_repositorio_cliente_buscar_o_crear_existente():
    sesion = Mock(spec=Session)
    cliente_modelo = Mock()
    cliente_modelo.id_cliente = "CLI-001"
    cliente_modelo.nombre = "Juan"
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = cliente_modelo
    sesion.query.return_value = query_mock
    
    repo = RepositorioClienteSQL(sesion)
    cliente = repo.buscar_o_crear_por_nombre("Juan")
    
    assert cliente.id_cliente == "CLI-001"
    sesion.add.assert_not_called()


def test_repositorio_cliente_buscar_o_crear_nuevo():
    sesion = Mock(spec=Session)
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    repo = RepositorioClienteSQL(sesion)
    cliente = repo.buscar_o_crear_por_nombre("Juan")
    
    assert cliente is not None
    sesion.add.assert_called_once()
    sesion.flush.assert_called_once()


# Estos tests usan buscar_o_crear_por_descripcion que no existe en el repositorio actual
# El método actual usa buscar_por_placa o similar
# def test_repositorio_vehiculo_buscar_o_crear_existente():
#     sesion = Mock(spec=Session)
#     vehiculo_modelo = Mock()
#     vehiculo_modelo.id_vehiculo = "VEH-001"
#     vehiculo_modelo.descripcion = "Auto"
#     
#     query_mock = Mock()
#     query_mock.filter.return_value.first.return_value = vehiculo_modelo
#     sesion.query.return_value = query_mock
#     
#     repo = RepositorioVehiculoSQL(sesion)
#     vehiculo = repo.buscar_o_crear_por_descripcion("Auto", "CLI-001")
#     
#     assert vehiculo.id_vehiculo == "VEH-001"
#     sesion.add.assert_not_called()


# def test_repositorio_vehiculo_buscar_o_crear_nuevo():
#     sesion = Mock(spec=Session)
#     
#     query_mock = Mock()
#     query_mock.filter.return_value.first.return_value = None
#     sesion.query.return_value = query_mock
#     
#     repo = RepositorioVehiculoSQL(sesion)
#     vehiculo = repo.buscar_o_crear_por_descripcion("Auto", "CLI-001")
#     
#     assert vehiculo is not None
#     sesion.add.assert_called_once()
#     sesion.flush.assert_called_once()


def test_repositorio_cliente_guardar():
    session_mock = Mock(spec=Session)
    repo = RepositorioClienteSQL(session_mock)
    assert repo is not None


def test_repositorio_vehiculo_tiene_metodos():
    session_mock = Mock(spec=Session)
    repo = RepositorioVehiculoSQL(session_mock)
    assert callable(repo.obtener)
    assert hasattr(repo, 'listar')


def test_repositorio_orden_tiene_repos_internos():
    session_mock = Mock(spec=Session)
    repo = RepositorioOrden(session_mock)
    assert hasattr(repo, 'repo_servicio')
    assert hasattr(repo, 'repo_evento')


def test_repositorio_servicio_creation():
    session_mock = Mock(spec=Session)
    repo = RepositorioServicioSQL(session_mock)
    assert repo is not None
    assert repo.sesion == session_mock


def test_repositorio_evento_creation():
    session_mock = Mock(spec=Session)
    repo = RepositorioEventoSQL(session_mock)
    assert repo is not None
    assert repo.sesion == session_mock


def test_repositorio_orden_deserializar():
    modelo_mock = Mock()
    modelo_mock.id_orden = "ORD-001"
    modelo_mock.cliente = Mock()
    modelo_mock.cliente.nombre = "Juan"
    modelo_mock.vehiculo = Mock()
    modelo_mock.vehiculo.descripcion = "Auto"
    modelo_mock.estado = EstadoOrden.CREATED.value
    modelo_mock.monto_autorizado = None
    modelo_mock.version_autorizacion = 0
    modelo_mock.total_real = Decimal('0')
    modelo_mock.fecha_creacion = datetime.utcnow()
    modelo_mock.fecha_cancelacion = None
    modelo_mock.servicios = []
    modelo_mock.eventos = []
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_mock
    sesion = Mock(spec=Session)
    sesion.query.return_value = query_mock
    
    repo = RepositorioOrden(sesion)
    repo.repo_servicio = Mock()
    repo.repo_evento = Mock()
    repo.repo_cliente = Mock()
    repo.repo_vehiculo = Mock()
    
    orden = repo.obtener("ORD-001")
    assert orden is not None


def test_repositorio_servicio_guardar():
    sesion = Mock(spec=Session)
    servicio = Servicio("Servicio", Decimal("1000.00"))
    componente = Componente("Comp", Decimal("200.00"))
    servicio.componentes.append(componente)
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    repo = RepositorioServicioSQL(sesion)
    repo.guardar_servicios("ORD-001", [servicio], [])
    
    sesion.add.assert_called()


def test_repositorio_evento_guardar():
    sesion = Mock(spec=Session)
    evento = Evento("CREATED", datetime.utcnow(), {})
    
    query_mock = Mock()
    query_mock.filter.return_value.all.return_value = []
    sesion.query.return_value = query_mock
    
    repo = RepositorioEventoSQL(sesion)
    repo.guardar_eventos("ORD-001", [evento], [])
    
    sesion.add.assert_called()


def test_repositorio_orden_guardar_nueva():
    sesion = Mock(spec=Session)
    
    repo_cliente = Mock()
    cliente = Cliente("Juan")
    cliente.id_cliente = 1
    repo_cliente.buscar_o_crear_por_nombre.return_value = cliente
    
    repo_vehiculo = Mock()
    vehiculo = Vehiculo("ABC-123", 1, "Toyota", "Corolla", 2020)
    vehiculo.id_vehiculo = 1
    repo_vehiculo.buscar_o_crear_por_placa.return_value = vehiculo
    
    repo_servicio = Mock()
    repo_evento = Mock()
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    repo = RepositorioOrden(sesion)
    repo.repo_cliente = repo_cliente
    repo.repo_vehiculo = repo_vehiculo
    repo.repo_servicio = repo_servicio
    repo.repo_evento = repo_evento
    
    orden = Orden("ORD-001", "Juan", "ABC-123", datetime.utcnow())
    repo.guardar(orden)
    
    sesion.add.assert_called_once()
    sesion.flush.assert_called()
    sesion.commit.assert_called_once()


def test_repositorio_orden_guardar_existente():
    sesion = Mock(spec=Session)
    
    modelo_existente = Mock()
    modelo_existente.id = 1
    modelo_existente.order_id = "ORD-001"
    modelo_existente.servicios = []
    modelo_existente.eventos = []
    
    repo_cliente = Mock()
    cliente = Cliente("Juan")
    cliente.id_cliente = 1
    repo_cliente.buscar_o_crear_por_nombre.return_value = cliente
    
    repo_vehiculo = Mock()
    vehiculo = Vehiculo("ABC-123", 1, "Toyota", "Corolla", 2020)
    vehiculo.id_vehiculo = 1
    repo_vehiculo.buscar_o_crear_por_placa.return_value = vehiculo
    
    repo_servicio = Mock()
    repo_evento = Mock()
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_existente
    sesion.query.return_value = query_mock
    
    repo = RepositorioOrden(sesion)
    repo.repo_cliente = repo_cliente
    repo.repo_vehiculo = repo_vehiculo
    repo.repo_servicio = repo_servicio
    repo.repo_evento = repo_evento
    
    orden = Orden("ORD-001", "Juan", "ABC-123", datetime.utcnow())
    orden.id = 1
    repo.guardar(orden)
    
    sesion.add.assert_not_called()
    sesion.commit.assert_called_once()


def test_repositorio_orden_guardar_con_id_diferente():
    sesion = Mock(spec=Session)
    
    modelo_existente = Mock()
    modelo_existente.id = 2
    modelo_existente.order_id = "ORD-001"
    
    repo_cliente = Mock()
    cliente = Cliente("Juan")
    cliente.id_cliente = 1
    repo_cliente.buscar_o_crear_por_nombre.return_value = cliente
    
    repo_vehiculo = Mock()
    vehiculo = Vehiculo("ABC-123", 1, "Toyota", "Corolla", 2020)
    vehiculo.id_vehiculo = 1
    repo_vehiculo.buscar_o_crear_por_placa.return_value = vehiculo
    
    repo_servicio = Mock()
    repo_evento = Mock()
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_existente
    sesion.query.return_value = query_mock
    
    repo = RepositorioOrden(sesion)
    repo.repo_cliente = repo_cliente
    repo.repo_vehiculo = repo_vehiculo
    repo.repo_servicio = repo_servicio
    repo.repo_evento = repo_evento
    
    orden = Orden("ORD-001", "Juan", "ABC-123", datetime.utcnow())
    orden.id = 1
    
    try:
        repo.guardar(orden)
        assert False, "Debería lanzar ValueError"
    except ValueError as e:
        assert "id diferente" in str(e).lower()


def test_repositorio_orden_guardar_nueva_con_id():
    sesion = Mock(spec=Session)
    
    modelo_existente_id = Mock()
    modelo_existente_id.id = 999
    
    repo_cliente = Mock()
    cliente = Cliente("Juan")
    cliente.id_cliente = 1
    repo_cliente.buscar_o_crear_por_nombre.return_value = cliente
    
    repo_vehiculo = Mock()
    vehiculo = Vehiculo("ABC-123", 1, "Toyota", "Corolla", 2020)
    vehiculo.id_vehiculo = 1
    repo_vehiculo.buscar_o_crear_por_placa.return_value = vehiculo
    
    repo_servicio = Mock()
    repo_evento = Mock()
    
    query_mock = Mock()
    query_mock.filter.side_effect = [
        Mock(first=Mock(return_value=None)),
        Mock(first=Mock(return_value=modelo_existente_id))
    ]
    sesion.query.return_value = query_mock
    
    repo = RepositorioOrden(sesion)
    repo.repo_cliente = repo_cliente
    repo.repo_vehiculo = repo_vehiculo
    repo.repo_servicio = repo_servicio
    repo.repo_evento = repo_evento
    
    orden = Orden("ORD-001", "Juan", "ABC-123", datetime.utcnow())
    orden.id = 999
    
    try:
        repo.guardar(orden)
        assert False, "Debería lanzar ValueError"
    except ValueError as e:
        assert "ya existe" in str(e).lower()


def test_repositorio_orden_deserializar_completo():
    sesion = Mock(spec=Session)
    
    modelo_mock = Mock()
    modelo_mock.id = 1
    modelo_mock.order_id = "ORD-001"
    modelo_mock.estado = EstadoOrden.CREATED.value
    modelo_mock.monto_autorizado = "1000.00"
    modelo_mock.version_autorizacion = 1
    modelo_mock.total_real = "1200.00"
    modelo_mock.fecha_creacion = datetime.utcnow()
    modelo_mock.fecha_cancelacion = None
    
    cliente_mock = Mock()
    cliente_mock.nombre = "Juan"
    modelo_mock.cliente = cliente_mock
    
    vehiculo_mock = Mock()
    vehiculo_mock.placa = "ABC-123"
    modelo_mock.vehiculo = vehiculo_mock
    
    modelo_mock.servicios = []
    modelo_mock.eventos = []
    
    repo_servicio = Mock()
    repo_servicio.deserializar_servicios.return_value = []
    
    repo_evento = Mock()
    repo_evento.deserializar_eventos.return_value = []
    
    repo = RepositorioOrden(sesion)
    repo.repo_servicio = repo_servicio
    repo.repo_evento = repo_evento
    
    orden = repo._deserializar(modelo_mock)
    
    assert orden.order_id == "ORD-001"
    assert orden.cliente == "Juan"
    assert orden.vehiculo == "ABC-123"
    assert orden.estado == EstadoOrden.CREATED


def test_repositorio_servicio_guardar_existente():
    sesion = Mock(spec=Session)
    
    servicio_existente = Mock()
    servicio_existente.id_servicio = 1
    servicio_existente.componentes = []
    
    servicio = Servicio("Servicio", Decimal("1000.00"))
    servicio.id_servicio = 1
    
    repo = RepositorioServicioSQL(sesion)
    repo.guardar_servicios(1, [servicio], [servicio_existente])
    
    assert servicio_existente.descripcion == "Servicio"


def test_repositorio_servicio_guardar_componente_existente():
    sesion = Mock(spec=Session)
    
    servicio_modelo = Mock()
    servicio_modelo.id_servicio = 1
    
    componente_existente = Mock()
    componente_existente.id_componente = 1
    servicio_modelo.componentes = [componente_existente]
    
    servicio = Servicio("Servicio", Decimal("1000.00"))
    servicio.id_servicio = 1
    
    componente = Componente("Comp", Decimal("200.00"))
    componente.id_componente = 1
    servicio.componentes.append(componente)
    
    repo = RepositorioServicioSQL(sesion)
    repo._guardar_componentes(servicio_modelo, servicio)
    
    assert componente_existente.descripcion == "Comp"


def test_repositorio_servicio_guardar_componente_nuevo():
    sesion = Mock(spec=Session)
    
    servicio_modelo = Mock()
    servicio_modelo.id_servicio = 1
    servicio_modelo.componentes = []
    
    servicio = Servicio("Servicio", Decimal("1000.00"))
    
    componente = Componente("Comp", Decimal("200.00"))
    servicio.componentes.append(componente)
    
    repo = RepositorioServicioSQL(sesion)
    repo._guardar_componentes(servicio_modelo, servicio)
    
    sesion.add.assert_called_once()
    sesion.flush.assert_called_once()


def test_repositorio_servicio_eliminar_componente():
    sesion = Mock(spec=Session)
    
    servicio_modelo = Mock()
    servicio_modelo.id_servicio = 1
    
    componente_eliminar = Mock()
    componente_eliminar.id_componente = 1
    servicio_modelo.componentes = [componente_eliminar]
    
    servicio = Servicio("Servicio", Decimal("1000.00"))
    
    repo = RepositorioServicioSQL(sesion)
    repo._guardar_componentes(servicio_modelo, servicio)
    
    sesion.delete.assert_called_once_with(componente_eliminar)


def test_repositorio_servicio_deserializar():
    sesion = Mock(spec=Session)
    
    componente_modelo = Mock()
    componente_modelo.id_componente = 1
    componente_modelo.descripcion = "Comp"
    componente_modelo.costo_estimado = "200.00"
    componente_modelo.costo_real = "250.00"
    
    servicio_modelo = Mock()
    servicio_modelo.id_servicio = 1
    servicio_modelo.descripcion = "Servicio"
    servicio_modelo.costo_mano_obra_estimado = "1000.00"
    servicio_modelo.costo_real = "1200.00"
    servicio_modelo.completado = 1
    servicio_modelo.componentes = [componente_modelo]
    
    repo = RepositorioServicioSQL(sesion)
    servicios = repo.deserializar_servicios([servicio_modelo])
    
    assert len(servicios) == 1
    assert servicios[0].descripcion == "Servicio"
    assert servicios[0].completado is True
    assert len(servicios[0].componentes) == 1


def test_repositorio_servicio_eliminar_servicio():
    sesion = Mock(spec=Session)
    
    # Configurar flush para simular la asignación de ID
    counter = [100]  # Usamos una lista para poder modificarla desde la función interna
    def mock_flush():
        # Encontrar el último objeto agregado y asignarle un ID
        if sesion.add.called:
            last_added = sesion.add.call_args[0][0]
            if hasattr(last_added, 'id_servicio'):
                last_added.id_servicio = counter[0]
                counter[0] += 1
    
    sesion.flush = mock_flush
    
    servicio_existente = Mock()
    servicio_existente.id_servicio = 1
    servicio_existente.componentes = []
    
    servicio = Servicio("Servicio", Decimal("1000.00"))
    servicio.id_servicio = 2
    
    repo = RepositorioServicioSQL(sesion)
    repo.guardar_servicios(1, [servicio], [servicio_existente])
    
    # Se verifica que se eliminó el servicio existente que ya no está en la nueva lista
    sesion.delete.assert_called_once_with(servicio_existente)


def test_repositorio_evento_actualizar_existente():
    sesion = Mock(spec=Session)
    
    evento_existente = Mock()
    evento_existente.tipo = "OLD"
    evento_existente.timestamp = datetime.utcnow()
    evento_existente.metadatos_json = None
    
    evento = Evento("CREATED", datetime.utcnow(), {"key": "value"})
    
    repo = RepositorioEventoSQL(sesion)
    repo.guardar_eventos(1, [evento], [evento_existente])
    
    assert evento_existente.tipo == "CREATED"


def test_repositorio_evento_eliminar_sobrantes():
    sesion = Mock(spec=Session)
    
    evento_existente1 = Mock()
    evento_existente2 = Mock()
    
    evento = Evento("CREATED", datetime.utcnow(), {})
    
    repo = RepositorioEventoSQL(sesion)
    repo.guardar_eventos(1, [evento], [evento_existente1, evento_existente2])
    
    assert sesion.delete.call_count == 1


def test_repositorio_evento_deserializar():
    sesion = Mock(spec=Session)
    
    # Crear timestamps específicos para asegurar el orden
    timestamp1 = datetime(2024, 1, 1, 10, 0, 0)
    timestamp2 = datetime(2024, 1, 1, 11, 0, 0)
    
    evento_modelo1 = Mock()
    evento_modelo1.tipo = "CREATED"
    evento_modelo1.timestamp = timestamp1
    evento_modelo1.metadatos_json = '{"key": "value"}'
    
    evento_modelo2 = Mock()
    evento_modelo2.tipo = "AUTHORIZED"
    evento_modelo2.timestamp = timestamp2
    evento_modelo2.metadatos_json = None
    
    repo = RepositorioEventoSQL(sesion)
    eventos = repo.deserializar_eventos([evento_modelo2, evento_modelo1])
    
    assert len(eventos) == 2
    # Los eventos se ordenan por timestamp, así que CREATED (10:00) viene antes que AUTHORIZED (11:00)
    assert eventos[0].tipo == "CREATED"
    assert eventos[1].tipo == "AUTHORIZED"


def test_repositorio_cliente_buscar_o_crear_por_criterio_existente_por_id():
    sesion = Mock(spec=Session)
    
    modelo_mock = Mock()
    modelo_mock.id_cliente = 1
    modelo_mock.nombre = "Juan"
    modelo_mock.identificacion = "12345"
    modelo_mock.correo = "juan@test.com"
    modelo_mock.direccion = "Calle 1"
    modelo_mock.celular = "555-1234"
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_mock
    sesion.query.return_value = query_mock
    
    repo = RepositorioClienteSQL(sesion)
    cliente = repo.buscar_o_crear_por_criterio(id_cliente=1)
    
    assert cliente.id_cliente == 1
    assert cliente.nombre == "Juan"


def test_repositorio_cliente_buscar_o_crear_por_criterio_nuevo():
    sesion = Mock(spec=Session)
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    def side_effect_flush():
        sesion.add.call_args[0][0].id_cliente = 1
    
    sesion.flush.side_effect = side_effect_flush
    
    repo = RepositorioClienteSQL(sesion)
    cliente = repo.buscar_o_crear_por_criterio(nombre="Pedro", identificacion="54321")
    
    assert cliente.nombre == "Pedro"
    sesion.add.assert_called_once()
    sesion.commit.assert_called_once()


def test_repositorio_cliente_buscar_o_crear_por_criterio_sin_nombre():
    sesion = Mock(spec=Session)
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    repo = RepositorioClienteSQL(sesion)
    
    try:
        repo.buscar_o_crear_por_criterio(identificacion="12345")
        assert False, "Debe lanzar ValueError"
    except ValueError:
        pass


def test_repositorio_cliente_listar():
    sesion = Mock(spec=Session)
    
    modelo1 = Mock()
    modelo1.id_cliente = 1
    modelo1.nombre = "Juan"
    modelo1.identificacion = "123"
    modelo1.correo = "juan@test.com"
    modelo1.direccion = "Calle 1"
    modelo1.celular = "555-1234"
    
    modelo2 = Mock()
    modelo2.id_cliente = 2
    modelo2.nombre = "Maria"
    modelo2.identificacion = "456"
    modelo2.correo = "maria@test.com"
    modelo2.direccion = "Calle 2"
    modelo2.celular = "555-5678"
    
    query_mock = Mock()
    query_mock.all.return_value = [modelo1, modelo2]
    sesion.query.return_value = query_mock
    
    repo = RepositorioClienteSQL(sesion)
    clientes = repo.listar()
    
    assert len(clientes) == 2
    assert clientes[0].nombre == "Juan"
    assert clientes[1].nombre == "Maria"


def test_repositorio_cliente_listar_error():
    sesion = Mock(spec=Session)
    
    sesion.query.side_effect = Exception("Error de BD")
    
    repo = RepositorioClienteSQL(sesion)
    clientes = repo.listar()
    
    assert len(clientes) == 0


def test_repositorio_cliente_guardar_nuevo_sin_id():
    sesion = Mock(spec=Session)
    
    def side_effect_flush():
        sesion.add.call_args[0][0].id_cliente = 10
    
    sesion.flush.side_effect = side_effect_flush
    
    cliente = Cliente(nombre="Carlos")
    
    repo = RepositorioClienteSQL(sesion)
    repo.guardar(cliente)
    
    assert cliente.id_cliente == 10
    sesion.add.assert_called_once()
    sesion.commit.assert_called_once()


def test_repositorio_cliente_guardar_actualizar_existente():
    sesion = Mock(spec=Session)
    
    modelo_existente = Mock()
    modelo_existente.id_cliente = 1
    modelo_existente.nombre = "Juan"
    modelo_existente.identificacion = "123"
    modelo_existente.correo = "juan@test.com"
    modelo_existente.direccion = "Calle 1"
    modelo_existente.celular = "555-1234"
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_existente
    sesion.query.return_value = query_mock
    
    cliente = Cliente(nombre="Juan Actualizado", id_cliente=1, identificacion="123-updated")
    
    repo = RepositorioClienteSQL(sesion)
    repo.guardar(cliente)
    
    assert modelo_existente.nombre == "Juan Actualizado"
    assert modelo_existente.identificacion == "123-updated"
    sesion.commit.assert_called_once()


def test_repositorio_cliente_guardar_nuevo_con_id_no_existe():
    sesion = Mock(spec=Session)
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    cliente = Cliente(nombre="Pedro", id_cliente=99)
    
    repo = RepositorioClienteSQL(sesion)
    repo.guardar(cliente)
    
    sesion.add.assert_called_once()
    sesion.commit.assert_called_once()


def test_repositorio_vehiculo_listar():
    sesion = Mock(spec=Session)
    
    modelo1 = Mock()
    modelo1.id_vehiculo = 1
    modelo1.placa = "ABC-123"
    modelo1.id_cliente = 1
    modelo1.marca = "Toyota"
    modelo1.modelo = "Corolla"
    modelo1.anio = 2020
    modelo1.kilometraje = 50000
    
    modelo2 = Mock()
    modelo2.id_vehiculo = 2
    modelo2.placa = "XYZ-789"
    modelo2.id_cliente = 2
    modelo2.marca = "Honda"
    modelo2.modelo = "Civic"
    modelo2.anio = 2019
    modelo2.kilometraje = 60000
    
    query_mock = Mock()
    query_mock.all.return_value = [modelo1, modelo2]
    sesion.query.return_value = query_mock
    
    repo = RepositorioVehiculoSQL(sesion)
    vehiculos = repo.listar()
    
    assert len(vehiculos) == 2
    assert vehiculos[0].placa == "ABC-123"
    assert vehiculos[1].placa == "XYZ-789"


def test_repositorio_vehiculo_listar_por_cliente():
    sesion = Mock(spec=Session)
    
    modelo1 = Mock()
    modelo1.id_vehiculo = 1
    modelo1.placa = "ABC-123"
    modelo1.id_cliente = 1
    modelo1.marca = "Toyota"
    modelo1.modelo = "Corolla"
    modelo1.anio = 2020
    modelo1.kilometraje = 50000
    
    query_mock = Mock()
    query_mock.filter.return_value.all.return_value = [modelo1]
    sesion.query.return_value = query_mock
    
    repo = RepositorioVehiculoSQL(sesion)
    vehiculos = repo.listar_por_cliente(1)
    
    assert len(vehiculos) == 1
    assert vehiculos[0].id_cliente == 1


def test_repositorio_vehiculo_guardar_nuevo_sin_id():
    sesion = Mock(spec=Session)
    
    def side_effect_flush():
        sesion.add.call_args[0][0].id_vehiculo = 15
    
    sesion.flush.side_effect = side_effect_flush
    
    vehiculo = Vehiculo(placa="NEW-123", id_cliente=1)
    
    repo = RepositorioVehiculoSQL(sesion)
    repo.guardar(vehiculo)
    
    assert vehiculo.id_vehiculo == 15
    sesion.add.assert_called_once()
    sesion.commit.assert_called_once()


def test_repositorio_vehiculo_guardar_actualizar_existente():
    sesion = Mock(spec=Session)
    
    modelo_existente = Mock()
    modelo_existente.id_vehiculo = 1
    modelo_existente.placa = "ABC-123"
    modelo_existente.marca = "Toyota"
    modelo_existente.modelo = "Corolla"
    modelo_existente.anio = 2020
    modelo_existente.kilometraje = 50000
    modelo_existente.id_cliente = 1
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_existente
    sesion.query.return_value = query_mock
    
    vehiculo = Vehiculo(placa="ABC-123-UPD", id_cliente=1, id_vehiculo=1, marca="Toyota Updated")
    
    repo = RepositorioVehiculoSQL(sesion)
    repo.guardar(vehiculo)
    
    assert modelo_existente.placa == "ABC-123-UPD"
    assert modelo_existente.marca == "Toyota Updated"
    sesion.commit.assert_called_once()


def test_repositorio_vehiculo_guardar_nuevo_con_id_no_existe():
    sesion = Mock(spec=Session)
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    vehiculo = Vehiculo(placa="NEW-999", id_cliente=1, id_vehiculo=99)
    
    repo = RepositorioVehiculoSQL(sesion)
    repo.guardar(vehiculo)
    
    sesion.add.assert_called_once()
    sesion.commit.assert_called_once()


def test_repositorio_vehiculo_buscar_o_crear_placa_existente():
    sesion = Mock(spec=Session)
    
    modelo_existente = Mock()
    modelo_existente.id_vehiculo = 5
    modelo_existente.placa = "ABC-123"
    modelo_existente.id_cliente = 1
    modelo_existente.marca = "Toyota"
    modelo_existente.modelo = "Corolla"
    modelo_existente.anio = 2020
    modelo_existente.kilometraje = 50000
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_existente
    sesion.query.return_value = query_mock
    
    repo = RepositorioVehiculoSQL(sesion)
    vehiculo = repo.buscar_o_crear_por_placa("ABC-123", 1)
    
    assert vehiculo.id_vehiculo == 5
    assert vehiculo.placa == "ABC-123"


def test_repositorio_vehiculo_buscar_por_criterio_por_id():
    sesion = Mock(spec=Session)
    
    modelo_mock = Mock()
    modelo_mock.id_vehiculo = 1
    modelo_mock.placa = "XYZ-999"
    modelo_mock.id_cliente = 2
    modelo_mock.marca = "Honda"
    modelo_mock.modelo = "Civic"
    modelo_mock.anio = 2021
    modelo_mock.kilometraje = 30000
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_mock
    sesion.query.return_value = query_mock
    
    repo = RepositorioVehiculoSQL(sesion)
    vehiculo = repo.buscar_por_criterio(id_vehiculo=1)
    
    assert vehiculo.id_vehiculo == 1
    assert vehiculo.placa == "XYZ-999"


def test_repositorio_vehiculo_buscar_por_criterio_por_placa():
    sesion = Mock(spec=Session)
    
    modelo_mock = Mock()
    modelo_mock.id_vehiculo = 1
    modelo_mock.placa = "DEF-456"
    modelo_mock.id_cliente = 3
    modelo_mock.marca = "Ford"
    modelo_mock.modelo = "Focus"
    modelo_mock.anio = 2019
    modelo_mock.kilometraje = 60000
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_mock
    sesion.query.return_value = query_mock
    
    repo = RepositorioVehiculoSQL(sesion)
    vehiculo = repo.buscar_por_criterio(placa="DEF-456")
    
    assert vehiculo.placa == "DEF-456"


def test_repositorio_vehiculo_buscar_por_criterio_sin_parametros():
    sesion = Mock(spec=Session)
    
    repo = RepositorioVehiculoSQL(sesion)
    vehiculo = repo.buscar_por_criterio()
    
    assert vehiculo is None


def test_repositorio_cliente_buscar_por_criterio_por_identificacion():
    sesion = Mock(spec=Session)
    
    modelo_mock = Mock()
    modelo_mock.id_cliente = 10
    modelo_mock.nombre = "Pedro"
    modelo_mock.identificacion = "987654"
    modelo_mock.correo = "pedro@test.com"
    modelo_mock.direccion = "Calle 10"
    modelo_mock.celular = "555-9999"
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_mock
    sesion.query.return_value = query_mock
    
    repo = RepositorioClienteSQL(sesion)
    cliente = repo.buscar_por_criterio(identificacion="987654")
    
    assert cliente.identificacion == "987654"
    assert cliente.nombre == "Pedro"


def test_repositorio_cliente_buscar_por_criterio_por_nombre():
    sesion = Mock(spec=Session)
    
    modelo_mock = Mock()
    modelo_mock.id_cliente = 11
    modelo_mock.nombre = "Ana"
    modelo_mock.identificacion = "111222"
    modelo_mock.correo = "ana@test.com"
    modelo_mock.direccion = "Calle 11"
    modelo_mock.celular = "555-1111"
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = modelo_mock
    sesion.query.return_value = query_mock
    
    repo = RepositorioClienteSQL(sesion)
    cliente = repo.buscar_por_criterio(nombre="Ana")
    
    assert cliente.nombre == "Ana"


def test_repositorio_cliente_buscar_por_criterio_sin_parametros():
    sesion = Mock(spec=Session)
    
    repo = RepositorioClienteSQL(sesion)
    cliente = repo.buscar_por_criterio()
    
    assert cliente is None


def test_repositorio_cliente_guardar_error_rollback():
    sesion = Mock(spec=Session)
    
    sesion.commit.side_effect = Exception("Error de BD")
    
    cliente = Cliente(nombre="Test")
    repo = RepositorioClienteSQL(sesion)
    
    try:
        repo.guardar(cliente)
        assert False, "Debe lanzar excepción"
    except Exception:
        sesion.rollback.assert_called_once()


def test_repositorio_cliente_buscar_o_crear_por_nombre_nuevo():
    sesion = Mock(spec=Session)
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    def side_effect_flush():
        sesion.add.call_args[0][0].id_cliente = 20
    
    sesion.flush.side_effect = side_effect_flush
    
    repo = RepositorioClienteSQL(sesion)
    cliente = repo.buscar_o_crear_por_nombre("Cliente Nuevo")
    
    assert cliente.nombre == "Cliente Nuevo"
    assert cliente.id_cliente == 20
    sesion.commit.assert_called_once()


def test_repositorio_cliente_buscar_por_identificacion_no_existe():
    sesion = Mock(spec=Session)
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    repo = RepositorioClienteSQL(sesion)
    cliente = repo.buscar_por_identificacion("999999")
    
    assert cliente is None


def test_repositorio_cliente_buscar_por_nombre_no_existe():
    sesion = Mock(spec=Session)
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    repo = RepositorioClienteSQL(sesion)
    cliente = repo.buscar_por_nombre("No Existe")
    
    assert cliente is None


def test_repositorio_vehiculo_buscar_o_crear_integrity_error_con_cliente():
    """Test IntegrityError con cliente asociado al verificar placa existente"""
    from sqlalchemy.exc import IntegrityError
    from app.infrastructure.models.cliente_model import ClienteModel
    
    sesion_mock = Mock()
    cliente_mock = Mock(spec=ClienteModel)
    cliente_mock.nombre = "Juan Pérez"
    
    modelo_vehiculo_mock = Mock()
    modelo_vehiculo_mock.placa = "XYZ-789"
    modelo_vehiculo_mock.id_cliente = 1
    modelo_vehiculo_mock.cliente = cliente_mock
    modelo_vehiculo_mock.marca = "Toyota"
    modelo_vehiculo_mock.modelo = "Corolla"
    
    # Primer query retorna None (no existe), luego IntegrityError en flush, luego existe con otro cliente
    query_results = [None, modelo_vehiculo_mock, modelo_vehiculo_mock]
    query_mock = Mock()
    query_mock.filter().first.side_effect = query_results
    sesion_mock.query.return_value = query_mock
    
    # Simular IntegrityError con mensaje de placa única
    orig_error = Exception("UNIQUE constraint failed: vehiculo.placa")
    integrity_error = IntegrityError("statement", {}, orig_error)
    sesion_mock.flush.side_effect = integrity_error
    
    repo = RepositorioVehiculoSQL(sesion_mock)
    
    with pytest.raises(ErrorDominio) as exc_info:
        repo.buscar_o_crear_por_placa("XYZ-789", id_cliente=2, marca="Honda", modelo="Civic")
    
    assert exc_info.value.codigo == CodigoError.PLACA_ASOCIADA_OTRO_CLIENTE
    assert "Juan Pérez" in str(exc_info.value.mensaje)
    sesion_mock.rollback.assert_called_once()


def test_repositorio_vehiculo_buscar_o_crear_integrity_error_sin_cliente():
    """Test IntegrityError sin cliente asociado al verificar placa existente"""
    from sqlalchemy.exc import IntegrityError
    
    sesion_mock = Mock()
    modelo_vehiculo_mock = Mock()
    modelo_vehiculo_mock.placa = "XYZ-789"
    modelo_vehiculo_mock.id_cliente = 1
    modelo_vehiculo_mock.cliente = None  # Sin cliente asociado
    
    query_results = [None, modelo_vehiculo_mock, modelo_vehiculo_mock]
    query_mock = Mock()
    query_mock.filter().first.side_effect = query_results
    sesion_mock.query.return_value = query_mock
    
    orig_error = Exception("UNIQUE constraint failed: vehiculo.placa")
    integrity_error = IntegrityError("statement", {}, orig_error)
    sesion_mock.flush.side_effect = integrity_error
    
    repo = RepositorioVehiculoSQL(sesion_mock)
    
    with pytest.raises(ErrorDominio) as exc_info:
        repo.buscar_o_crear_por_placa("XYZ-789", id_cliente=2, marca="Honda")
    
    assert exc_info.value.codigo == CodigoError.PLACA_ASOCIADA_OTRO_CLIENTE
    assert "desconocido" in str(exc_info.value.mensaje)
    sesion_mock.rollback.assert_called_once()


def test_repositorio_vehiculo_buscar_o_crear_integrity_error_sin_conflicto_cliente():
    """Test IntegrityError cuando el vehículo existente pertenece al mismo cliente"""
    from sqlalchemy.exc import IntegrityError
    
    sesion_mock = Mock()
    modelo_vehiculo_mock = Mock()
    modelo_vehiculo_mock.placa = "XYZ-789"
    modelo_vehiculo_mock.id_cliente = 1  # Mismo cliente
    
    query_results = [None, modelo_vehiculo_mock]
    query_mock = Mock()
    query_mock.filter().first.side_effect = query_results
    sesion_mock.query.return_value = query_mock
    
    orig_error = Exception("UNIQUE constraint failed: vehiculo.placa")
    integrity_error = IntegrityError("statement", {}, orig_error)
    sesion_mock.flush.side_effect = integrity_error
    
    repo = RepositorioVehiculoSQL(sesion_mock)
    
    # En este caso, no debería lanzar ErrorDominio porque es el mismo cliente
    # Debería relanzar IntegrityError
    with pytest.raises(IntegrityError):
        repo.buscar_o_crear_por_placa("XYZ-789", id_cliente=1, marca="Honda")
    
    sesion_mock.rollback.assert_called_once()


def test_repositorio_vehiculo_buscar_o_crear_integrity_error_generico():
    """Test IntegrityError genérico no relacionado con placa"""
    from sqlalchemy.exc import IntegrityError
    
    sesion_mock = Mock()
    query_mock = Mock()
    query_mock.filter().first.return_value = None
    sesion_mock.query.return_value = query_mock
    
    # IntegrityError sin referencia a placa o unique
    orig_error = Exception("FOREIGN KEY constraint failed")
    integrity_error = IntegrityError("statement", {}, orig_error)
    sesion_mock.flush.side_effect = integrity_error
    
    repo = RepositorioVehiculoSQL(sesion_mock)
    
    with pytest.raises(IntegrityError):
        repo.buscar_o_crear_por_placa("ABC-999", id_cliente=1, marca="Ford")
    
    sesion_mock.rollback.assert_called_once()


def test_repositorio_vehiculo_buscar_o_crear_placa_existente_mismo_cliente_con_nombre():
    """Test buscar_o_crear_por_placa cuando ya existe y consulta nombre del cliente"""
    from app.infrastructure.models.cliente_model import ClienteModel
    
    sesion_mock = Mock()
    cliente_mock = Mock(spec=ClienteModel)
    cliente_mock.nombre = "Pedro García"
    
    modelo_vehiculo_mock = Mock()
    modelo_vehiculo_mock.placa = "ABC-123"
    modelo_vehiculo_mock.id_cliente = 5
    modelo_vehiculo_mock.marca = "Ford"
    modelo_vehiculo_mock.modelo = "Focus"
    modelo_vehiculo_mock.anio = 2020
    modelo_vehiculo_mock.kilometraje = 50000
    modelo_vehiculo_mock.id_vehiculo = 100
    
    # Primera consulta: buscar vehículo por placa con conflicto de cliente
    # Segunda consulta: buscar cliente
    query_results = [modelo_vehiculo_mock, cliente_mock]
    query_mock = Mock()
    query_mock.filter().first.side_effect = query_results
    sesion_mock.query.return_value = query_mock
    
    repo = RepositorioVehiculoSQL(sesion_mock)
    
    with pytest.raises(ErrorDominio) as exc_info:
        repo.buscar_o_crear_por_placa("ABC-123", id_cliente=10, marca="Honda")
    
    assert exc_info.value.codigo == CodigoError.PLACA_ASOCIADA_OTRO_CLIENTE
    assert "Pedro García" in str(exc_info.value.mensaje)
    assert "ID: 5" in str(exc_info.value.mensaje)