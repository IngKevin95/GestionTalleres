from decimal import Decimal
from datetime import datetime
from app.domain.entidades import Orden, Servicio, Componente
from app.domain.enums import EstadoOrden, CodigoError
from app.domain.exceptions import ErrorDominio


def test_orden_reautorizar():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.WAITING_FOR_APPROVAL
    orden.monto_autorizado = Decimal("1160.00")
    orden.total_real = Decimal("1300.00")
    orden.version_autorizacion = 1
    
    orden.reautorizar(Decimal("1500.00"))
    assert orden.estado == EstadoOrden.AUTHORIZED
    assert orden.monto_autorizado == Decimal("1500.00")
    assert orden.version_autorizacion == 2


def test_orden_reautorizar_monto_insuficiente():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.WAITING_FOR_APPROVAL
    orden.monto_autorizado = Decimal("1160.00")
    orden.total_real = Decimal("1300.00")
    
    try:
        orden.reautorizar(Decimal("1200.00"))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.INVALID_AMOUNT


def test_orden_entregar():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.COMPLETED
    
    orden.entregar()
    assert orden.estado == EstadoOrden.DELIVERED
    assert len(orden.eventos) > 0
    assert any(e.tipo == "DELIVERED" for e in orden.eventos)


def test_orden_entregar_estado_invalido():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.IN_PROGRESS
    
    try:
        orden.entregar()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_orden_establecer_costo_real():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    orden.servicios.append(servicio)
    
    orden.establecer_costo_real(servicio.id_servicio, Decimal("1200.00"))
    assert servicio.costo_real == Decimal("1200.00")
    assert orden.total_real == Decimal("1200.00")


def test_orden_establecer_costo_real_con_componentes():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    componente = Componente("Componente", Decimal("200.00"))
    servicio.componentes.append(componente)
    orden.servicios.append(servicio)
    
    componentes_reales = {componente.id_componente: Decimal("250.00")}
    orden.establecer_costo_real(servicio.id_servicio, Decimal("1200.00"), componentes_reales)
    
    assert servicio.costo_real == Decimal("1200.00")
    assert componente.costo_real == Decimal("250.00")


def test_orden_establecer_costo_real_servicio_no_encontrado():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    
    try:
        orden.establecer_costo_real("SERV-999", Decimal("1200.00"))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND


def test_orden_intentar_completar_exactamente_110():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.IN_PROGRESS
    orden.monto_autorizado = Decimal("1160.00")
    
    servicio = Servicio("Servicio", Decimal("1000.00"))
    servicio.completado = True
    servicio.costo_real = Decimal("1000.00")
    orden.servicios.append(servicio)
    
    orden.intentar_completar()
    assert orden.estado == EstadoOrden.COMPLETED


def test_orden_intentar_completar_orden_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.intentar_completar()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_orden_intentar_completar_sin_autorizacion():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.IN_PROGRESS
    
    try:
        orden.intentar_completar()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_orden_intentar_completar_estado_invalido():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CREATED
    orden.monto_autorizado = Decimal("1160.00")
    
    try:
        orden.intentar_completar()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_orden_establecer_estado_en_proceso():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.AUTHORIZED
    orden.monto_autorizado = Decimal("1160.00")
    
    orden.establecer_estado_en_proceso()
    assert orden.estado == EstadoOrden.IN_PROGRESS
    assert len(orden.eventos) > 0
    assert any(e.tipo == "IN_PROGRESS" for e in orden.eventos)


def test_orden_establecer_estado_en_proceso_estado_invalido():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CREATED
    
    try:
        orden.establecer_estado_en_proceso()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_servicio_calcular_subtotal_estimado():
    servicio = Servicio("Servicio", Decimal("1000.00"))
    componente1 = Componente("Comp1", Decimal("200.00"))
    componente2 = Componente("Comp2", Decimal("300.00"))
    servicio.componentes.append(componente1)
    servicio.componentes.append(componente2)
    
    subtotal = servicio.calcular_subtotal_estimado()
    assert subtotal == Decimal("1500.00")


def test_servicio_calcular_costo_real_con_costo_real():
    servicio = Servicio("Servicio", Decimal("1000.00"))
    servicio.costo_real = Decimal("1200.00")
    
    costo = servicio.calcular_costo_real()
    assert costo == Decimal("1200.00")


def test_servicio_calcular_costo_real_sin_costo_real():
    servicio = Servicio("Servicio", Decimal("1000.00"))
    componente = Componente("Comp", Decimal("200.00"))
    componente.costo_real = Decimal("250.00")
    servicio.componentes.append(componente)
    
    costo = servicio.calcular_costo_real()
    assert costo == Decimal("1250.00")


def test_servicio_calcular_costo_real_sin_nada():
    servicio = Servicio("Servicio", Decimal("1000.00"))
    componente = Componente("Comp", Decimal("200.00"))
    servicio.componentes.append(componente)
    
    costo = servicio.calcular_costo_real()
    assert costo == Decimal("1200.00")


def test_orden_crear_orden_existente():
    from app.application.acciones import CrearOrden
    from app.application.dtos import CrearOrdenDTO
    from app.application.ports import RepositorioOrden, AlmacenEventos
    from app.domain.entidades import Evento
    
    class RepoMock(RepositorioOrden):
        def __init__(self):
            self.orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
        def obtener(self, id_orden: str):
            return self.orden if id_orden == "ORD-001" else None
        def guardar(self, orden: Orden):
            pass
    
    class AuditMock(AlmacenEventos):
        def registrar(self, evento: Evento):
            pass
    
    repo = RepoMock()
    audit = AuditMock()
    accion = CrearOrden(repo, audit)
    
    from app.application.dtos import CustomerIdentifierDTO, VehicleIdentifierDTO
    
    dto = CrearOrdenDTO(
        order_id="ORD-001",
        customer=CustomerIdentifierDTO(nombre="Juan"),
        vehicle=VehicleIdentifierDTO(placa="Auto"),
        timestamp=datetime.utcnow()
    )
    
    resultado = accion.ejecutar(dto)
    assert resultado.order_id == "ORD-001"

