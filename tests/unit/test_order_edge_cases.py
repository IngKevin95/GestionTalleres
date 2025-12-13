from decimal import Decimal
from datetime import datetime
from app.domain.entidades import Orden, Servicio
from app.domain.enums import EstadoOrden, CodigoError
from app.domain.exceptions import ErrorDominio


def test_establecer_estado_diagnosticado_orden_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.establecer_estado_diagnosticado()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_establecer_estado_diagnosticado_estado_invalido():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.DIAGNOSED
    
    try:
        orden.establecer_estado_diagnosticado()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_autorizar_orden_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.autorizar(Decimal("1160.00"))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_autorizar_estado_invalido():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CREATED
    
    try:
        orden.autorizar(Decimal("1160.00"))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_establecer_estado_en_proceso_orden_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.establecer_estado_en_proceso()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_establecer_costo_real_orden_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    servicio = Servicio("Servicio", Decimal("1000.00"))
    orden.servicios.append(servicio)
    
    try:
        orden.establecer_costo_real(servicio.id_servicio, Decimal("1200.00"))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_establecer_costo_real_con_componentes_reales():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    from app.domain.entidades import Componente
    componente = Componente("Comp", Decimal("200.00"))
    servicio.componentes.append(componente)
    orden.servicios.append(servicio)
    
    componentes_reales = {componente.id_componente: Decimal("250.00")}
    orden.establecer_costo_real(servicio.id_servicio, Decimal("1200.00"), componentes_reales)
    
    assert servicio.costo_real == Decimal("1200.00")
    assert componente.costo_real == Decimal("250.00")


def test_establecer_costo_real_sin_componentes_reales():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    from app.domain.entidades import Componente
    componente = Componente("Comp", Decimal("200.00"))
    componente.costo_real = Decimal("250.00")
    servicio.componentes.append(componente)
    orden.servicios.append(servicio)
    
    orden.establecer_costo_real(servicio.id_servicio, Decimal("1200.00"), None)
    
    assert servicio.costo_real == Decimal("1200.00")
    assert componente.costo_real is None


def test_reautorizar_orden_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.reautorizar(Decimal("1500.00"))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_reautorizar_estado_invalido():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.AUTHORIZED
    
    try:
        orden.reautorizar(Decimal("1500.00"))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_entregar_orden_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.entregar()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_cancelar_orden_ya_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.cancelar("Motivo")
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED

