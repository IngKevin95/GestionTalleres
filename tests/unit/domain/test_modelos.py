from decimal import Decimal
from datetime import datetime
from app.domain.entidades import Orden, Servicio, Componente
from app.domain.enums import EstadoOrden, CodigoError
from app.domain.exceptions import ErrorDominio


def test_crear_orden():
    o = Orden("ORD-001", "Juan Pérez", "Toyota Corolla", datetime.utcnow())
    assert o.estado == EstadoOrden.CREATED
    assert len(o.servicios) == 0
    assert o.version_autorizacion == 0


def test_agregar_servicio():
    o = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    serv = Servicio("Cambio de aceite", Decimal("500.00"))
    o.agregar_servicio(serv)
    assert len(o.servicios) == 1


def test_no_agregar_servicio_despues_autorizar():
    o = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    o.estado = EstadoOrden.AUTHORIZED
    serv = Servicio("Servicio", Decimal("100"))
    
    try:
        o.agregar_servicio(serv)
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.NOT_ALLOWED_AFTER_AUTHORIZATION


def test_establecer_estado_diagnosticado():
    o = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    o.establecer_estado_diagnosticado()
    assert o.estado == EstadoOrden.DIAGNOSED
    assert len(o.eventos) == 1
    assert o.eventos[0].tipo == "DIAGNOSED"


def test_autorizar_sin_servicios():
    o = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    o.estado = EstadoOrden.DIAGNOSED
    
    try:
        o.autorizar(Decimal("1000"))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.NO_SERVICES


def test_autorizar():
    o = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    serv = Servicio("Servicio", Decimal("1000"))
    o.agregar_servicio(serv)
    o.estado = EstadoOrden.DIAGNOSED
    
    o.autorizar(Decimal("1160"))
    assert o.estado == EstadoOrden.AUTHORIZED
    assert o.monto_autorizado == Decimal("1160")
    assert o.version_autorizacion == 1


def test_intentar_completar_excede_110():
    o = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    serv = Servicio("Servicio", Decimal("1000"))
    o.agregar_servicio(serv)
    o.estado = EstadoOrden.IN_PROGRESS
    o.monto_autorizado = Decimal("1000")
    serv.costo_real = Decimal("1200")
    serv.completado = True
    o.total_real = Decimal("1200")
    
    try:
        o.intentar_completar()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.REQUIRES_REAUTH
        assert o.estado == EstadoOrden.WAITING_FOR_APPROVAL


def test_cancelar_orden():
    o = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    o.cancelar("Cliente canceló")
    assert o.estado == EstadoOrden.CANCELLED
    assert o.fecha_cancelacion is not None


def test_no_operaciones_despues_cancelar():
    o = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    o.cancelar("Cancelado")
    
    try:
        o.agregar_servicio(Servicio("Servicio", Decimal("100")))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED

