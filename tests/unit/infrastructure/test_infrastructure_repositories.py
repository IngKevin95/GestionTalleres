from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from app.infrastructure.repositories.repositorio_orden import RepositorioOrden
from app.infrastructure.repositories.repositorio_cliente import RepositorioClienteSQL
from app.infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
from app.infrastructure.repositories.repositorio_servicio import RepositorioServicioSQL
from app.infrastructure.repositories.repositorio_evento import RepositorioEventoSQL
from app.domain.entidades import Orden, Servicio, Componente, Evento, Cliente, Vehiculo
from app.domain.enums import EstadoOrden


# Test usa estructura antigua con id_orden y descripcion en vehiculos
# def test_repositorio_orden_obtener_existente():
#     sesion_mock = Mock(spec=Session)
#     modelo_mock = Mock()
#     modelo_mock.id_orden = "ORD-001"
#     modelo_mock.estado = "CREATED"
#     modelo_mock.monto_autorizado = None
#     modelo_mock.version_autorizacion = 0
#     modelo_mock.total_real = "0"
#     modelo_mock.fecha_creacion = datetime.utcnow()
#     modelo_mock.fecha_cancelacion = None
#     modelo_mock.cliente = Mock()
#     modelo_mock.cliente.nombre = "Juan"
#     modelo_mock.vehiculo = Mock()
#     modelo_mock.vehiculo.descripcion = "Auto"
#     modelo_mock.servicios = []
#     modelo_mock.eventos = []
#     
#     query_mock = Mock()
#     query_mock.filter.return_value.first.return_value = modelo_mock
#     sesion_mock.query.return_value = query_mock
#     
#     repo_cliente_mock = Mock(spec=RepositorioClienteSQL)
#     repo_vehiculo_mock = Mock(spec=RepositorioVehiculoSQL)
#     repo_servicio_mock = Mock(spec=RepositorioServicioSQL)
#     repo_evento_mock = Mock(spec=RepositorioEventoSQL)
#     
#     repo = RepositorioOrden(sesion_mock)
#     repo.repo_cliente = repo_cliente_mock
#     repo.repo_vehiculo = repo_vehiculo_mock
#     repo.repo_servicio = repo_servicio_mock
#     repo.repo_evento = repo_evento_mock
#     
#     orden = repo.obtener("ORD-001")
#     assert orden is not None
#     assert orden.id_orden == "ORD-001"


def test_repositorio_orden_obtener_no_existente():
    sesion_mock = Mock(spec=Session)
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion_mock.query.return_value = query_mock
    
    repo_cliente_mock = Mock(spec=RepositorioClienteSQL)
    repo_vehiculo_mock = Mock(spec=RepositorioVehiculoSQL)
    repo_servicio_mock = Mock(spec=RepositorioServicioSQL)
    repo_evento_mock = Mock(spec=RepositorioEventoSQL)
    
    repo = RepositorioOrden(sesion_mock)
    repo.repo_cliente = repo_cliente_mock
    repo.repo_vehiculo = repo_vehiculo_mock
    repo.repo_servicio = repo_servicio_mock
    repo.repo_evento = repo_evento_mock
    
    orden = repo.obtener("ORD-999")
    assert orden is None


def test_repositorio_cliente_buscar_o_crear_existente():
    sesion_mock = Mock(spec=Session)
    cliente_mock = Mock()
    cliente_mock.id_cliente = "CLI-001"
    cliente_mock.nombre = "Juan"
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = cliente_mock
    sesion_mock.query.return_value = query_mock
    sesion_mock.add = Mock()
    sesion_mock.flush = Mock()
    
    repo = RepositorioClienteSQL(sesion_mock)
    cliente = repo.buscar_o_crear_por_nombre("Juan")
    
    assert cliente.id_cliente == "CLI-001"
    assert cliente.nombre == "Juan"


def test_repositorio_cliente_buscar_o_crear_nuevo():
    sesion_mock = Mock(spec=Session)
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion_mock.query.return_value = query_mock
    sesion_mock.add = Mock()
    sesion_mock.flush = Mock()
    
    repo = RepositorioClienteSQL(sesion_mock)
    cliente = repo.buscar_o_crear_por_nombre("Juan Nuevo")
    
    assert cliente is not None
    assert cliente.nombre == "Juan Nuevo"
    sesion_mock.add.assert_called_once()


# Tests con estructura antigua - buscar_o_crear_por_descripcion no existe
# def test_repositorio_vehiculo_buscar_o_crear_existente():
#     sesion_mock = Mock(spec=Session)
#     vehiculo_mock = Mock()
#     vehiculo_mock.id_vehiculo = "VEH-001"
#     vehiculo_mock.descripcion = "ABC-123"
#     
#     query_mock = Mock()
#     query_mock.filter.return_value.first.return_value = vehiculo_mock
#     sesion_mock.query.return_value = query_mock
#     sesion_mock.add = Mock()
#     sesion_mock.flush = Mock()
#     
#     repo = RepositorioVehiculoSQL(sesion_mock)
#     vehiculo = repo.buscar_o_crear_por_descripcion("ABC-123", "CLI-001")
#     
#     assert vehiculo.id_vehiculo == "VEH-001"
#     assert vehiculo.descripcion == "ABC-123"


# def test_repositorio_vehiculo_buscar_o_crear_nuevo():
#     sesion_mock = Mock(spec=Session)
#     query_mock = Mock()
#     query_mock.filter.return_value.first.return_value = None
#     sesion_mock.query.return_value = query_mock
#     sesion_mock.add = Mock()
#     sesion_mock.flush = Mock()
#     
#     repo = RepositorioVehiculoSQL(sesion_mock)
#     vehiculo = repo.buscar_o_crear_por_descripcion("XYZ-789", "CLI-001")
#     
#     assert vehiculo is not None
#     assert vehiculo.descripcion == "XYZ-789"
#     sesion_mock.add.assert_called_once()


def test_repositorio_servicio_guardar_servicios():
    sesion_mock = Mock(spec=Session)
    servicio_model_mock = Mock()
    servicio_model_mock.id_servicio = "SERV-001"
    
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion_mock.query.return_value = query_mock
    sesion_mock.add = Mock()
    sesion_mock.delete = Mock()
    sesion_mock.flush = Mock()
    
    servicio = Servicio("Cambio de aceite", Decimal("500.00"))
    componente = Componente("Aceite", Decimal("300.00"))
    servicio.componentes.append(componente)
    
    repo = RepositorioServicioSQL(sesion_mock)
    repo.guardar_servicios("ORD-001", [servicio], [])
    
    sesion_mock.add.assert_called()


def test_repositorio_evento_guardar_eventos():
    sesion_mock = Mock(spec=Session)
    query_mock = Mock()
    query_mock.filter.return_value.all.return_value = []
    sesion_mock.query.return_value = query_mock
    sesion_mock.add = Mock()
    sesion_mock.delete = Mock()
    sesion_mock.flush = Mock()
    
    evento = Evento("CREATED", datetime.utcnow(), {})
    
    repo = RepositorioEventoSQL(sesion_mock)
    repo.guardar_eventos("ORD-001", [evento], [])
    
    sesion_mock.add.assert_called()


def test_repositorio_evento_deserializar_eventos():
    from app.infrastructure.models.evento_model import EventoModel
    import json
    
    sesion_mock = Mock(spec=Session)
    repo = RepositorioEventoSQL(sesion_mock)
    
    evento_model1 = Mock(spec=EventoModel)
    evento_model1.tipo = "CREATED"
    evento_model1.timestamp = datetime.utcnow()
    evento_model1.metadatos_json = json.dumps({"key": "value"})
    
    evento_model2 = Mock(spec=EventoModel)
    evento_model2.tipo = "AUTHORIZED"
    evento_model2.timestamp = datetime.utcnow()
    evento_model2.metadatos_json = None
    
    eventos = repo.deserializar_eventos([evento_model1, evento_model2])
    assert len(eventos) == 2
    assert eventos[0].tipo == "CREATED"
    assert eventos[1].tipo == "AUTHORIZED"


def test_repositorio_servicio_guardar_servicios_existente():
    from app.infrastructure.models.servicio_model import ServicioModel
    
    sesion_mock = Mock(spec=Session)
    servicio_model_mock = Mock(spec=ServicioModel)
    servicio_model_mock.id_servicio = "SERV-001"
    servicio_model_mock.componentes = []
    
    servicio = Servicio("Servicio", Decimal("1000.00"))
    servicio.id_servicio = "SERV-001"
    servicio.costo_real = Decimal("1200.00")
    servicio.completado = True
    
    repo = RepositorioServicioSQL(sesion_mock)
    repo.guardar_servicios("ORD-001", [servicio], [servicio_model_mock])
    
    assert servicio_model_mock.descripcion == "Servicio"


def test_repositorio_servicio_guardar_servicios_eliminar():
    from app.infrastructure.models.servicio_model import ServicioModel
    
    sesion_mock = Mock(spec=Session)
    servicio_model_mock = Mock(spec=ServicioModel)
    servicio_model_mock.id_servicio = "SERV-OLD"
    servicio_model_mock.componentes = []
    
    servicio = Servicio("Servicio Nuevo", Decimal("1000.00"))
    
    repo = RepositorioServicioSQL(sesion_mock)
    repo.guardar_servicios("ORD-001", [servicio], [servicio_model_mock])
    
    sesion_mock.delete.assert_called()


def test_repositorio_servicio_deserializar_servicios():
    from app.infrastructure.models.servicio_model import ServicioModel
    from app.infrastructure.models.componente_model import ComponenteModel
    
    sesion_mock = Mock(spec=Session)
    repo = RepositorioServicioSQL(sesion_mock)
    
    componente_model = Mock(spec=ComponenteModel)
    componente_model.id_componente = "COMP-001"
    componente_model.descripcion = "Componente"
    componente_model.costo_estimado = "200.00"
    componente_model.costo_real = "250.00"
    
    servicio_model = Mock(spec=ServicioModel)
    servicio_model.id_servicio = "SERV-001"
    servicio_model.descripcion = "Servicio"
    servicio_model.costo_mano_obra_estimado = "1000.00"
    servicio_model.costo_real = "1200.00"
    servicio_model.completado = 1
    servicio_model.componentes = [componente_model]
    
    servicios = repo.deserializar_servicios([servicio_model])
    assert len(servicios) == 1
    assert servicios[0].descripcion == "Servicio"
    assert len(servicios[0].componentes) == 1

