from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict
from app.application.acciones import (
    Reautorizar, EntregarOrden, CancelarOrden, EstablecerCostoReal
)
from app.application.dtos import (
    ReautorizarDTO, EntregarDTO, CancelarDTO, EstablecerCostoRealDTO
)
from app.application.ports import RepositorioOrden, AlmacenEventos
from app.domain.entidades import Orden, Evento, Servicio, Componente
from app.domain.exceptions import ErrorDominio
from app.domain.enums import CodigoError, EstadoOrden


class RepositorioOrdenMock(RepositorioOrden):
    def __init__(self):
        self._ordenes: Dict[str, Orden] = {}
    
    def obtener(self, id_orden: str) -> Optional[Orden]:
        return self._ordenes.get(id_orden)
    
    def guardar(self, orden: Orden) -> None:
        self._ordenes[orden.id_orden] = orden


class AlmacenEventosMock(AlmacenEventos):
    def __init__(self):
        self.eventos_registrados = []
    
    def registrar(self, evento: Evento) -> None:
        self.eventos_registrados.append(evento)


def test_reautorizar():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.WAITING_FOR_APPROVAL
    orden.monto_autorizado = Decimal("1160.00")
    orden.total_real = Decimal("1300.00")
    orden.version_autorizacion = 1
    repo.guardar(orden)
    
    accion = Reautorizar(repo, audit)
    dto = ReautorizarDTO(
        order_id="ORD-001",
        nuevo_monto_autorizado=Decimal("1500.00"),
        timestamp=datetime.utcnow()
    )
    
    resultado = accion.ejecutar(dto)
    assert resultado.status == "AUTHORIZED"
    assert resultado.authorized_amount == "1500.00"
    
    orden_actualizada = repo.obtener("ORD-001")
    assert orden_actualizada.version_autorizacion == 2


def test_reautorizar_monto_insuficiente():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.WAITING_FOR_APPROVAL
    orden.monto_autorizado = Decimal("1160.00")
    orden.total_real = Decimal("1300.00")
    repo.guardar(orden)
    
    accion = Reautorizar(repo, audit)
    dto = ReautorizarDTO(
        order_id="ORD-001",
        nuevo_monto_autorizado=Decimal("1200.00"),
        timestamp=datetime.utcnow()
    )
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.INVALID_AMOUNT


def test_entregar_orden():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.COMPLETED
    repo.guardar(orden)
    
    accion = EntregarOrden(repo, audit)
    dto = EntregarDTO(order_id="ORD-001")
    
    resultado = accion.ejecutar(dto)
    assert resultado.status == "DELIVERED"
    
    orden_actualizada = repo.obtener("ORD-001")
    assert orden_actualizada.estado == EstadoOrden.DELIVERED


def test_entregar_orden_estado_invalido():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.IN_PROGRESS
    repo.guardar(orden)
    
    accion = EntregarOrden(repo, audit)
    dto = EntregarDTO(order_id="ORD-001")
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_cancelar_orden():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    repo.guardar(orden)
    
    accion = CancelarOrden(repo, audit)
    dto = CancelarDTO(order_id="ORD-001", motivo="Cliente canceló")
    
    resultado = accion.ejecutar(dto)
    assert resultado.status == "CANCELLED"
    
    orden_actualizada = repo.obtener("ORD-001")
    assert orden_actualizada.estado == EstadoOrden.CANCELLED
    assert orden_actualizada.fecha_cancelacion is not None


def test_cancelar_orden_no_existe():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    accion = CancelarOrden(repo, audit)
    dto = CancelarDTO(order_id="ORD-999", motivo="Motivo")
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_establecer_costo_real():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    orden.servicios.append(servicio)
    repo.guardar(orden)
    
    accion = EstablecerCostoReal(repo, audit)
    dto = EstablecerCostoRealDTO(
        order_id="ORD-001",
        servicio_id=servicio.id_servicio,
        costo_real=Decimal("1200.00"),
        completed=True
    )
    
    resultado = accion.ejecutar(dto)
    assert resultado is not None
    
    orden_actualizada = repo.obtener("ORD-001")
    assert orden_actualizada.servicios[0].costo_real == Decimal("1200.00")
    assert orden_actualizada.servicios[0].completado is True


def test_establecer_costo_real_por_indice():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio1 = Servicio("Servicio 1", Decimal("1000.00"))
    servicio2 = Servicio("Servicio 2", Decimal("2000.00"))
    orden.servicios.append(servicio1)
    orden.servicios.append(servicio2)
    repo.guardar(orden)
    
    accion = EstablecerCostoReal(repo, audit)
    dto = EstablecerCostoRealDTO(
        order_id="ORD-001",
        service_index=2,
        costo_real=Decimal("2500.00"),
        completed=True
    )
    
    resultado = accion.ejecutar(dto)
    assert resultado is not None
    
    orden_actualizada = repo.obtener("ORD-001")
    assert orden_actualizada.servicios[1].costo_real == Decimal("2500.00")


def test_establecer_costo_real_con_componentes():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    componente = Componente("Componente", Decimal("200.00"))
    servicio.componentes.append(componente)
    orden.servicios.append(servicio)
    repo.guardar(orden)
    
    accion = EstablecerCostoReal(repo, audit)
    dto = EstablecerCostoRealDTO(
        order_id="ORD-001",
        servicio_id=servicio.id_servicio,
        costo_real=Decimal("1200.00"),
        componentes_reales={componente.id_componente: Decimal("250.00")},
        completed=True
    )
    
    resultado = accion.ejecutar(dto)
    assert resultado is not None
    
    orden_actualizada = repo.obtener("ORD-001")
    assert orden_actualizada.servicios[0].componentes[0].costo_real == Decimal("250.00")


def test_establecer_costo_real_indice_invalido():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    orden.servicios.append(servicio)
    repo.guardar(orden)
    
    accion = EstablecerCostoReal(repo, audit)
    dto = EstablecerCostoRealDTO(
        order_id="ORD-001",
        service_index=99,
        costo_real=Decimal("1200.00")
    )
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_establecer_costo_real_sin_servicio_id_ni_indice():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    repo.guardar(orden)
    
    accion = EstablecerCostoReal(repo, audit)
    dto = EstablecerCostoRealDTO(
        order_id="ORD-001",
        costo_real=Decimal("1200.00")
    )
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND

