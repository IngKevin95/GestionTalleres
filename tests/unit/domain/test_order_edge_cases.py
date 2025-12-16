from decimal import Decimal
from datetime import datetime
from app.domain.entidades import Orden, Servicio, Componente
from app.domain.enums import EstadoOrden, CodigoError
from app.domain.exceptions import ErrorDominio


def test_diagnostico_orden_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.establecer_estado_diagnosticado()
        assert False
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_diagnostico_estado_invalido():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.DIAGNOSED
    
    try:
        orden.establecer_estado_diagnosticado()
        assert False
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_autorizar_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.autorizar(Decimal("1160.00"))
        assert False
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_autorizar_estado_incorrecto():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CREATED
    
    try:
        orden.autorizar(Decimal("1160.00"))
        assert False
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_en_proceso_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.establecer_estado_en_proceso()
        assert False
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_costo_real_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    servicio = Servicio("Servicio", Decimal("1000.00"))
    orden.servicios.append(servicio)
    
    try:
        orden.establecer_costo_real(servicio.id_servicio, Decimal("1200.00"))
        assert False
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_costo_real_con_componentes():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    componente = Componente("Comp", Decimal("200.00"))
    servicio.componentes.append(componente)
    orden.servicios.append(servicio)
    
    componentes_reales = {componente.id_componente: Decimal("250.00")}
    orden.establecer_costo_real(servicio.id_servicio, Decimal("1200.00"), componentes_reales)
    
    assert servicio.costo_real == Decimal("1200.00")
    assert componente.costo_real == Decimal("250.00")


def test_costo_real_sin_componentes():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    servicio = Servicio("Servicio", Decimal("1000.00"))
    componente = Componente("Comp", Decimal("200.00"))
    componente.costo_real = Decimal("250.00")
    servicio.componentes.append(componente)
    orden.servicios.append(servicio)
    
    orden.establecer_costo_real(servicio.id_servicio, Decimal("1200.00"), None)
    
    assert servicio.costo_real == Decimal("1200.00")
    assert componente.costo_real is None


def test_reautorizar_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.reautorizar(Decimal("1500.00"))
        assert False
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_reautorizar_estado_incorrecto():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.AUTHORIZED
    
    try:
        orden.reautorizar(Decimal("1500.00"))
        assert False
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_entregar_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.entregar()
        assert False
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_cancelar_ya_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.cancelar("Motivo")
        assert False
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED

