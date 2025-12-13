from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict
from app.application.acciones import (
    Autorizar, Reautorizar, IntentarCompletar,
    EstablecerEstadoDiagnosticado, EstablecerEstadoEnProceso,
    AgregarServicio, EstablecerCostoReal, CrearOrden
)
from app.application.dtos import (
    AutorizarDTO, ReautorizarDTO, IntentarCompletarDTO,
    EstablecerEstadoDiagnosticadoDTO, EstablecerEstadoEnProcesoTDTO,
    AgregarServicioDTO, EstablecerCostoRealDTO, CrearOrdenDTO
)
from app.application.ports import RepositorioOrden, AlmacenEventos
from app.domain.entidades import Orden, Evento, Servicio
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


def test_autorizar_orden_no_existe():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    accion = Autorizar(repo, audit)
    
    dto = AutorizarDTO(order_id="ORD-999", timestamp=datetime.utcnow())
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_reautorizar_orden_no_existe():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    accion = Reautorizar(repo, audit)
    
    dto = ReautorizarDTO(
        order_id="ORD-999",
        nuevo_monto_autorizado=Decimal("1500.00"),
        timestamp=datetime.utcnow()
    )
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_intentar_completar_orden_no_existe():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    accion = IntentarCompletar(repo, audit)
    
    dto = IntentarCompletarDTO(order_id="ORD-999")
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_establecer_estado_diagnosticado_orden_no_existe():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    accion = EstablecerEstadoDiagnosticado(repo, audit)
    
    dto = EstablecerEstadoDiagnosticadoDTO(order_id="ORD-999")
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_establecer_estado_en_proceso_orden_no_existe():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    accion = EstablecerEstadoEnProceso(repo, audit)
    
    dto = EstablecerEstadoEnProcesoTDTO(order_id="ORD-999")
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_agregar_servicio_orden_no_existe():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    accion = AgregarServicio(repo, audit)
    
    dto = AgregarServicioDTO(
        order_id="ORD-999",
        descripcion="Servicio",
        costo_mano_obra=Decimal("1000.00"),
        componentes=[]
    )
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_establecer_costo_real_orden_no_existe():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    accion = EstablecerCostoReal(repo, audit)
    
    dto = EstablecerCostoRealDTO(
        order_id="ORD-999",
        servicio_id="SERV-123",
        costo_real=Decimal("1200.00")
    )
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_establecer_costo_real_indice_cero():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    orden.servicios.append(servicio)
    repo.guardar(orden)
    
    accion = EstablecerCostoReal(repo, audit)
    dto = EstablecerCostoRealDTO(
        order_id="ORD-001",
        service_index=0,
        costo_real=Decimal("1200.00")
    )
    
    try:
        accion.ejecutar(dto)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_establecer_costo_real_indice_muy_alto():
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


def test_establecer_costo_real_completed_false():
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
        completed=False
    )
    
    resultado = accion.ejecutar(dto)
    assert resultado is not None
    
    orden_actualizada = repo.obtener("ORD-001")
    assert orden_actualizada.servicios[0].completado is False


def test_establecer_costo_real_completed_none():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    servicio.completado = True
    orden.servicios.append(servicio)
    repo.guardar(orden)
    
    accion = EstablecerCostoReal(repo, audit)
    dto = EstablecerCostoRealDTO(
        order_id="ORD-001",
        servicio_id=servicio.id_servicio,
        costo_real=Decimal("1200.00"),
        completed=None
    )
    
    resultado = accion.ejecutar(dto)
    assert resultado is not None
    
    orden_actualizada = repo.obtener("ORD-001")
    assert orden_actualizada.servicios[0].completado is True


def test_crear_orden_sin_order_id():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    accion = CrearOrden(repo, audit)
    
    dto = CrearOrdenDTO(
        cliente="Juan",
        vehiculo="Auto",
        timestamp=datetime.utcnow()
    )
    
    resultado = accion.ejecutar(dto)
    assert resultado.order_id is not None
    assert resultado.order_id.startswith("ORD-")


def test_agregar_servicio_con_componentes():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    repo.guardar(orden)
    
    accion = AgregarServicio(repo, audit)
    dto = AgregarServicioDTO(
        order_id="ORD-001",
        descripcion="Servicio",
        costo_mano_obra=Decimal("1000.00"),
        componentes=[
            {"description": "Comp1", "estimated_cost": "200.00"},
            {"description": "Comp2", "estimated_cost": "300.00"}
        ]
    )
    
    resultado = accion.ejecutar(dto)
    assert len(resultado.services) == 1
    assert len(resultado.services[0].componentes) == 2


def test_agregar_servicio_componente_sin_costo():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    repo.guardar(orden)
    
    accion = AgregarServicio(repo, audit)
    dto = AgregarServicioDTO(
        order_id="ORD-001",
        descripcion="Servicio",
        costo_mano_obra=Decimal("1000.00"),
        componentes=[
            {"description": "Comp1"}
        ]
    )
    
    resultado = accion.ejecutar(dto)
    assert len(resultado.services) == 1
    assert len(resultado.services[0].componentes) == 1

