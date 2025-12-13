from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from app.infrastructure.repositories.repositorio_orden import RepositorioOrden
from app.domain.entidades import Orden, Servicio, Evento
from app.domain.enums import EstadoOrden


def test_repositorio_orden_obtener_existente():
    mock_sesion = Mock(spec=Session)
    mock_query = Mock()
    mock_orden_model = Mock()
    
    mock_orden_model.id_orden = "ORD-001"
    mock_orden_model.estado = "CREATED"
    mock_orden_model.monto_autorizado = None
    mock_orden_model.version_autorizacion = 0
    mock_orden_model.total_real = "0"
    mock_orden_model.fecha_creacion = datetime.utcnow()
    mock_orden_model.fecha_cancelacion = None
    mock_orden_model.cliente = Mock()
    mock_orden_model.cliente.nombre = "Juan"
    mock_orden_model.vehiculo = Mock()
    mock_orden_model.vehiculo.descripcion = "Auto"
    mock_orden_model.servicios = []
    mock_orden_model.eventos = []
    
    mock_query.filter.return_value.first.return_value = mock_orden_model
    mock_sesion.query.return_value = mock_query
    
    mock_repo_servicio = Mock()
    mock_repo_servicio.deserializar_servicios.return_value = []
    mock_repo_evento = Mock()
    mock_repo_evento.deserializar_eventos.return_value = []
    mock_repo_cliente = Mock()
    mock_repo_vehiculo = Mock()
    
    repo = RepositorioOrden(mock_sesion)
    repo.repo_servicio = mock_repo_servicio
    repo.repo_evento = mock_repo_evento
    repo.repo_cliente = mock_repo_cliente
    repo.repo_vehiculo = mock_repo_vehiculo
    
    orden = repo.obtener("ORD-001")
    
    assert orden is not None
    assert orden.id_orden == "ORD-001"
    mock_sesion.expire_all.assert_called_once()


def test_repositorio_orden_obtener_no_existente():
    mock_sesion = Mock(spec=Session)
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_sesion.query.return_value = mock_query
    
    mock_repo_servicio = Mock()
    mock_repo_evento = Mock()
    mock_repo_cliente = Mock()
    mock_repo_vehiculo = Mock()
    
    repo = RepositorioOrden(mock_sesion)
    repo.repo_servicio = mock_repo_servicio
    repo.repo_evento = mock_repo_evento
    repo.repo_cliente = mock_repo_cliente
    repo.repo_vehiculo = mock_repo_vehiculo
    
    orden = repo.obtener("ORD-999")
    
    assert orden is None


def test_repositorio_orden_guardar_nueva():
    mock_sesion = Mock(spec=Session)
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_sesion.query.return_value = mock_query
    
    mock_repo_cliente = Mock()
    mock_cliente = Mock()
    mock_cliente.id_cliente = "CLI-001"
    mock_repo_cliente.buscar_o_crear_por_nombre.return_value = mock_cliente
    
    mock_repo_vehiculo = Mock()
    mock_vehiculo = Mock()
    mock_vehiculo.id_vehiculo = "VEH-001"
    mock_repo_vehiculo.buscar_o_crear_por_descripcion.return_value = mock_vehiculo
    
    mock_repo_servicio = Mock()
    mock_repo_evento = Mock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.servicios.append(Servicio("Servicio", Decimal("1000.00")))
    orden.eventos.append(Evento("CREATED", datetime.utcnow(), {}))
    
    repo = RepositorioOrden(mock_sesion)
    repo.repo_cliente = mock_repo_cliente
    repo.repo_vehiculo = mock_repo_vehiculo
    repo.repo_servicio = mock_repo_servicio
    repo.repo_evento = mock_repo_evento
    
    repo.guardar(orden)
    
    mock_sesion.add.assert_called_once()
    mock_sesion.flush.assert_called_once()
    mock_sesion.commit.assert_called_once()
    mock_repo_servicio.guardar_servicios.assert_called_once()
    mock_repo_evento.guardar_eventos.assert_called_once()


def test_repositorio_orden_guardar_existente():
    mock_sesion = Mock(spec=Session)
    mock_query = Mock()
    mock_orden_model = Mock()
    mock_orden_model.id_orden = "ORD-001"
    mock_orden_model.servicios = []
    mock_orden_model.eventos = []
    mock_query.filter.return_value.first.return_value = mock_orden_model
    mock_sesion.query.return_value = mock_query
    
    mock_repo_cliente = Mock()
    mock_cliente = Mock()
    mock_cliente.id_cliente = "CLI-001"
    mock_repo_cliente.buscar_o_crear_por_nombre.return_value = mock_cliente
    
    mock_repo_vehiculo = Mock()
    mock_vehiculo = Mock()
    mock_vehiculo.id_vehiculo = "VEH-001"
    mock_repo_vehiculo.buscar_o_crear_por_descripcion.return_value = mock_vehiculo
    
    mock_repo_servicio = Mock()
    mock_repo_evento = Mock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.AUTHORIZED
    orden.monto_autorizado = Decimal("1160.00")
    
    repo = RepositorioOrden(mock_sesion)
    repo.repo_cliente = mock_repo_cliente
    repo.repo_vehiculo = mock_repo_vehiculo
    repo.repo_servicio = mock_repo_servicio
    repo.repo_evento = mock_repo_evento
    
    repo.guardar(orden)
    
    mock_sesion.add.assert_not_called()
    mock_sesion.flush.assert_called_once()
    mock_sesion.commit.assert_called_once()
    assert mock_orden_model.estado == "AUTHORIZED"


def test_repositorio_orden_serializar():
    mock_sesion = Mock(spec=Session)
    mock_repo_servicio = Mock()
    mock_repo_evento = Mock()
    mock_repo_cliente = Mock()
    mock_repo_vehiculo = Mock()
    
    repo = RepositorioOrden(mock_sesion)
    repo.repo_servicio = mock_repo_servicio
    repo.repo_evento = mock_repo_evento
    repo.repo_cliente = mock_repo_cliente
    repo.repo_vehiculo = mock_repo_vehiculo
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.monto_autorizado = Decimal("1160.00")
    orden.version_autorizacion = 1
    
    modelo = repo._serializar(orden, "CLI-001", "VEH-001")
    
    assert modelo.id_orden == "ORD-001"
    assert modelo.id_cliente == "CLI-001"
    assert modelo.id_vehiculo == "VEH-001"
    assert modelo.estado == "CREATED"
    assert modelo.monto_autorizado == "1160.00"
    assert modelo.version_autorizacion == 1


def test_repositorio_orden_serializar_sin_monto():
    mock_sesion = Mock(spec=Session)
    mock_repo_servicio = Mock()
    mock_repo_evento = Mock()
    mock_repo_cliente = Mock()
    mock_repo_vehiculo = Mock()
    
    repo = RepositorioOrden(mock_sesion)
    repo.repo_servicio = mock_repo_servicio
    repo.repo_evento = mock_repo_evento
    repo.repo_cliente = mock_repo_cliente
    repo.repo_vehiculo = mock_repo_vehiculo
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    
    modelo = repo._serializar(orden, "CLI-001", "VEH-001")
    
    assert modelo.monto_autorizado is None


def test_repositorio_orden_actualizar_modelo():
    mock_sesion = Mock(spec=Session)
    mock_repo_servicio = Mock()
    mock_repo_evento = Mock()
    mock_repo_cliente = Mock()
    mock_repo_vehiculo = Mock()
    
    repo = RepositorioOrden(mock_sesion)
    repo.repo_servicio = mock_repo_servicio
    repo.repo_evento = mock_repo_evento
    repo.repo_cliente = mock_repo_cliente
    repo.repo_vehiculo = mock_repo_vehiculo
    
    mock_modelo = Mock()
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.AUTHORIZED
    orden.monto_autorizado = Decimal("1160.00")
    orden.version_autorizacion = 2
    orden.total_real = Decimal("1200.00")
    
    repo._actualizar_modelo(mock_modelo, orden, "CLI-001", "VEH-001")
    
    assert mock_modelo.id_cliente == "CLI-001"
    assert mock_modelo.id_vehiculo == "VEH-001"
    assert mock_modelo.estado == "AUTHORIZED"
    assert mock_modelo.monto_autorizado == "1160.00"
    assert mock_modelo.version_autorizacion == 2
    assert mock_modelo.total_real == "1200.00"


def test_repositorio_orden_deserializar():
    mock_sesion = Mock(spec=Session)
    mock_repo_servicio = Mock()
    mock_servicio = Servicio("Servicio", Decimal("1000.00"))
    mock_repo_servicio.deserializar_servicios.return_value = [mock_servicio]
    
    mock_repo_evento = Mock()
    mock_evento = Evento("CREATED", datetime.utcnow(), {})
    mock_repo_evento.deserializar_eventos.return_value = [mock_evento]
    
    mock_repo_cliente = Mock()
    mock_repo_vehiculo = Mock()
    
    repo = RepositorioOrden(mock_sesion)
    repo.repo_servicio = mock_repo_servicio
    repo.repo_evento = mock_repo_evento
    repo.repo_cliente = mock_repo_cliente
    repo.repo_vehiculo = mock_repo_vehiculo
    
    mock_modelo = Mock()
    mock_modelo.id_orden = "ORD-001"
    mock_modelo.estado = "CREATED"
    mock_modelo.monto_autorizado = None
    mock_modelo.version_autorizacion = 0
    mock_modelo.total_real = "0"
    mock_modelo.fecha_creacion = datetime.utcnow()
    mock_modelo.fecha_cancelacion = None
    mock_modelo.cliente = Mock()
    mock_modelo.cliente.nombre = "Juan"
    mock_modelo.vehiculo = Mock()
    mock_modelo.vehiculo.descripcion = "Auto"
    mock_modelo.servicios = []
    mock_modelo.eventos = []
    
    orden = repo._deserializar(mock_modelo)
    
    assert orden.id_orden == "ORD-001"
    assert orden.cliente == "Juan"
    assert orden.vehiculo == "Auto"
    assert orden.estado == EstadoOrden.CREATED
    assert len(orden.servicios) == 1
    assert len(orden.eventos) == 1

