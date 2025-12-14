from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict
from app.application.acciones import (
    CrearOrden, AgregarServicio, EstablecerEstadoDiagnosticado,
    Autorizar, EstablecerEstadoEnProceso, IntentarCompletar,
    Reautorizar, EntregarOrden, CancelarOrden, EstablecerCostoReal
)
from app.application.dtos import (
    CrearOrdenDTO, AgregarServicioDTO, EstablecerEstadoDiagnosticadoDTO,
    AutorizarDTO, EstablecerEstadoEnProcesoTDTO, IntentarCompletarDTO,
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


def crear_fixtures():
    repo = RepositorioOrdenMock()
    auditoria = AlmacenEventosMock()
    return repo, auditoria


def test_crear_orden():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    accion = CrearOrden(repo, audit)
    
    dto = CrearOrdenDTO(
        cliente="Juan Pérez",
        vehiculo="Toyota Corolla",
        timestamp=datetime.utcnow()
    )
    
    resultado = accion.ejecutar(dto)
    assert resultado.status == "CREATED"
    assert resultado.customer == "Juan Pérez"
    
    orden = repo.obtener(resultado.order_id)
    assert orden is not None


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


def test_agregar_servicio():
    repo, auditoria = crear_fixtures()
    
    crear = CrearOrden(repo, auditoria)
    orden_dto = crear.ejecutar(CrearOrdenDTO(
        cliente="Juan", vehiculo="Auto", timestamp=datetime.utcnow()
    ))
    
    agregar = AgregarServicio(repo, auditoria)
    servicio_dto = AgregarServicioDTO(
        order_id=orden_dto.order_id,
        descripcion="Cambio de aceite",
        costo_mano_obra=Decimal("500.00"),
        componentes=[{"description": "Aceite", "estimated_cost": "300.00"}]
    )
    
    resultado = agregar.ejecutar(servicio_dto)
    assert len(resultado.services) == 1


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


def test_autorizar():
    r = RepositorioOrdenMock()
    a = AlmacenEventosMock()
    
    crear = CrearOrden(r, a)
    orden_dto = crear.ejecutar(CrearOrdenDTO(
        cliente="Juan", vehiculo="Auto", timestamp=datetime.utcnow()
    ))
    
    agregar = AgregarServicio(r, a)
    agregar.ejecutar(AgregarServicioDTO(
        order_id=orden_dto.order_id,
        descripcion="Servicio",
        costo_mano_obra=Decimal("1000.00"),
        componentes=[]
    ))
    
    diagnosticar = EstablecerEstadoDiagnosticado(r, a)
    diagnosticar.ejecutar(EstablecerEstadoDiagnosticadoDTO(order_id=orden_dto.order_id))
    
    autorizar = Autorizar(r, a)
    resultado = autorizar.ejecutar(AutorizarDTO(
        order_id=orden_dto.order_id,
        timestamp=datetime.utcnow()
    ))
    
    assert resultado.status == "AUTHORIZED"
    assert resultado.authorized_amount is not None


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


def test_intentar_completar_excede_110():
    repo, auditoria = crear_fixtures()
    
    crear = CrearOrden(repo, auditoria)
    orden_dto = crear.ejecutar(CrearOrdenDTO(
        cliente="Juan", vehiculo="Auto", timestamp=datetime.utcnow()
    ))
    
    agregar = AgregarServicio(repo, auditoria)
    agregar.ejecutar(AgregarServicioDTO(
        order_id=orden_dto.order_id,
        descripcion="Servicio",
        costo_mano_obra=Decimal("10000.00"),
        componentes=[]
    ))
    
    diagnosticar = EstablecerEstadoDiagnosticado(repo, auditoria)
    diagnosticar.ejecutar(EstablecerEstadoDiagnosticadoDTO(order_id=orden_dto.order_id))
    
    autorizar = Autorizar(repo, auditoria)
    autorizar.ejecutar(AutorizarDTO(order_id=orden_dto.order_id, timestamp=datetime.utcnow()))
    
    en_proceso = EstablecerEstadoEnProceso(repo, auditoria)
    en_proceso.ejecutar(EstablecerEstadoEnProcesoTDTO(order_id=orden_dto.order_id))
    
    orden = repo.obtener(orden_dto.order_id)
    monto_autorizado = orden.monto_autorizado
    limite_110 = monto_autorizado * Decimal("1.10")
    costo_que_excede = limite_110 + Decimal("100.00")
    
    orden.servicios[0].costo_real = costo_que_excede
    orden.servicios[0].completado = True
    repo.guardar(orden)
    
    completar = IntentarCompletar(repo, auditoria)
    try:
        completar.ejecutar(IntentarCompletarDTO(order_id=orden_dto.order_id))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.REQUIRES_REAUTH
        
        orden = repo.obtener(orden_dto.order_id)
        assert orden.estado == EstadoOrden.WAITING_FOR_APPROVAL


def test_intentar_completar_sin_servicios_completados():
    repo, auditoria = crear_fixtures()
    
    crear = CrearOrden(repo, auditoria)
    orden_dto = crear.ejecutar(CrearOrdenDTO(
        cliente="Juan", vehiculo="Auto", timestamp=datetime.utcnow()
    ))
    
    agregar = AgregarServicio(repo, auditoria)
    agregar.ejecutar(AgregarServicioDTO(
        order_id=orden_dto.order_id,
        descripcion="Servicio 1",
        costo_mano_obra=Decimal("1000.00"),
        componentes=[]
    ))
    
    agregar.ejecutar(AgregarServicioDTO(
        order_id=orden_dto.order_id,
        descripcion="Servicio 2",
        costo_mano_obra=Decimal("2000.00"),
        componentes=[]
    ))
    
    diagnosticar = EstablecerEstadoDiagnosticado(repo, auditoria)
    diagnosticar.ejecutar(EstablecerEstadoDiagnosticadoDTO(order_id=orden_dto.order_id))
    
    autorizar = Autorizar(repo, auditoria)
    autorizar.ejecutar(AutorizarDTO(order_id=orden_dto.order_id, timestamp=datetime.utcnow()))
    
    en_proceso = EstablecerEstadoEnProceso(repo, auditoria)
    en_proceso.ejecutar(EstablecerEstadoEnProcesoTDTO(order_id=orden_dto.order_id))
    
    orden = repo.obtener(orden_dto.order_id)
    orden.servicios[0].completado = True
    orden.servicios[1].completado = False
    orden.servicios[0].costo_real = Decimal("1000.00")
    orden.servicios[1].costo_real = Decimal("2000.00")
    repo.guardar(orden)
    
    completar = IntentarCompletar(repo, auditoria)
    try:
        completar.ejecutar(IntentarCompletarDTO(order_id=orden_dto.order_id))
        assert False, "Debe lanzar error por servicios no completados"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.INVALID_OPERATION
        assert "completar" in e.mensaje.lower()
        
        orden = repo.obtener(orden_dto.order_id)
        assert orden.estado == EstadoOrden.IN_PROGRESS


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
