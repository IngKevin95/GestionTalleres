import pytest
from decimal import Decimal
from datetime import datetime, timezone
from app.domain.entidades import Orden, Servicio, Componente, Cliente, Vehiculo
from app.domain.entidades.event import Evento
from app.domain.enums import EstadoOrden, CodigoError
from app.domain.exceptions import ErrorDominio


def test_cliente_crear():
    cliente = Cliente("Juan Pérez")
    assert cliente.nombre == "Juan Pérez"
    assert cliente.id_cliente is None


def test_cliente_con_id():
    cliente = Cliente("Juan Pérez")
    cliente.id_cliente = "CLI-001"
    assert cliente.id_cliente == "CLI-001"


def test_vehiculo_crear():
    vehiculo = Vehiculo("ABC-123", 1)
    assert vehiculo.placa == "ABC-123"
    assert vehiculo.id_cliente == 1
    assert vehiculo.id_vehiculo is None


def test_vehiculo_con_todos_los_campos():
    vehiculo = Vehiculo(
        "ABC-123",
        1,
        marca="Toyota",
        modelo="Corolla",
        anio=2020,
        id_vehiculo=1
    )
    assert vehiculo.placa == "ABC-123"
    assert vehiculo.marca == "Toyota"
    assert vehiculo.modelo == "Corolla"
    assert vehiculo.anio == 2020
    assert vehiculo.id_vehiculo == 1


def test_orden_reautorizar():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.WAITING_FOR_APPROVAL
    orden.monto_autorizado = Decimal("1160.00")
    orden.total_real = Decimal("1300.00")
    orden.version_autorizacion = 1
    
    orden.reautorizar(Decimal("1500.00"))
    assert orden.estado == EstadoOrden.AUTHORIZED
    assert orden.monto_autorizado == Decimal("1500.00")
    assert orden.version_autorizacion == 2


def test_orden_reautorizar_monto_insuficiente():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.WAITING_FOR_APPROVAL
    orden.monto_autorizado = Decimal("1160.00")
    orden.total_real = Decimal("1300.00")
    
    try:
        orden.reautorizar(Decimal("1200.00"))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.INVALID_AMOUNT


def test_orden_entregar():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.COMPLETED
    
    orden.entregar()
    assert orden.estado == EstadoOrden.DELIVERED
    assert len(orden.eventos) > 0
    assert any(e.tipo == "DELIVERED" for e in orden.eventos)


def test_orden_entregar_estado_invalido():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.IN_PROGRESS
    
    try:
        orden.entregar()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_orden_establecer_costo_real():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    servicio = Servicio("Servicio", Decimal("1000.00"))
    orden.servicios.append(servicio)
    
    orden.establecer_costo_real(servicio.id_servicio, Decimal("1200.00"))
    assert servicio.costo_real == Decimal("1200.00")
    assert orden.total_real == Decimal("1200.00")


def test_orden_establecer_costo_real_con_componentes():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    servicio = Servicio("Servicio", Decimal("1000.00"))
    componente = Componente("Componente", Decimal("200.00"))
    servicio.componentes.append(componente)
    orden.servicios.append(servicio)
    
    componentes_reales = {componente.id_componente: Decimal("250.00")}
    orden.establecer_costo_real(servicio.id_servicio, Decimal("1200.00"), componentes_reales)
    
    assert servicio.costo_real == Decimal("1200.00")
    assert componente.costo_real == Decimal("250.00")


def test_servicio_calcular_subtotal_estimado():
    servicio = Servicio("Servicio", Decimal("1000.00"))
    componente1 = Componente("Comp1", Decimal("200.00"))
    componente2 = Componente("Comp2", Decimal("300.00"))
    servicio.componentes.append(componente1)
    servicio.componentes.append(componente2)
    
    subtotal = servicio.calcular_subtotal_estimado()
    assert subtotal == Decimal("1500.00")


def test_servicio_calcular_costo_real():
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


def test_orden_intentar_completar_exactamente_110():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.IN_PROGRESS
    orden.monto_autorizado = Decimal("1160.00")
    
    servicio = Servicio("Servicio", Decimal("1000.00"))
    servicio.completado = True
    servicio.costo_real = Decimal("1000.00")
    orden.servicios.append(servicio)
    
    orden.intentar_completar()
    assert orden.estado == EstadoOrden.COMPLETED


def test_orden_intentar_completar_orden_cancelada():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.CANCELLED
    
    try:
        orden.intentar_completar()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_CANCELLED


def test_orden_establecer_estado_en_proceso():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.AUTHORIZED
    orden.monto_autorizado = Decimal("1160.00")
    
    orden.establecer_estado_en_proceso()
    assert orden.estado == EstadoOrden.IN_PROGRESS
    assert len(orden.eventos) > 0
    assert any(e.tipo == "IN_PROGRESS" for e in orden.eventos)


def test_orden_establecer_estado_en_proceso_estado_invalido():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.CREATED
    
    try:
        orden.establecer_estado_en_proceso()
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR


def test_evento_crear():
    evento = Evento(
        tipo="ORDEN_CREADA",
        timestamp=datetime.now(),
        metadatos={"order_id": "ORD-001"}
    )
    assert evento.tipo == "ORDEN_CREADA"
    assert evento.metadatos["order_id"] == "ORD-001"


def test_orden_establecer_costo_real_servicio_no_existe():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    
    try:
        orden.establecer_costo_real(999, Decimal("1000.00"), {})
        assert False, "Debería lanzar ErrorDominio"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.ORDER_NOT_FOUND
        assert "no encontrado" in str(e.mensaje).lower()


def test_orden_intentar_completar_no_in_progress():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.CREATED
    orden.monto_autorizado = Decimal("1160.00")
    
    try:
        orden.intentar_completar()
        assert False, "Debería lanzar ErrorDominio"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR
        assert "IN_PROGRESS" in str(e.mensaje)


def test_orden_intentar_completar_sin_autorizacion():
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.IN_PROGRESS
    orden.monto_autorizado = None
    
    try:
        orden.intentar_completar()
        assert False, "Debería lanzar ErrorDominio"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR
        assert "no autorizada" in str(e.mensaje).lower()


def test_orden_order_id_vacio_lanza_error():
    """Test que orden con order_id vacío lanza error."""
    with pytest.raises(ErrorDominio) as exc_info:
        Orden("", "Juan", "ABC-123", datetime.now(timezone.utc))
    assert exc_info.value.codigo == CodigoError.INVALID_OPERATION
    assert "order_id no puede estar vacío" in exc_info.value.mensaje


def test_orden_order_id_solo_espacios_lanza_error():
    """Test que orden con order_id solo espacios lanza error."""
    with pytest.raises(ErrorDominio) as exc_info:
        Orden("   ", "Juan", "ABC-123", datetime.now(timezone.utc))
    assert exc_info.value.codigo == CodigoError.INVALID_OPERATION


def test_orden_order_id_formato_invalido_lanza_error():
    """Test que orden con order_id con formato inválido lanza error."""
    with pytest.raises(ErrorDominio) as exc_info:
        Orden("ord-001", "Juan", "ABC-123", datetime.now(timezone.utc))
    assert exc_info.value.codigo == CodigoError.INVALID_OPERATION
    assert "formato inválido" in exc_info.value.mensaje


def test_orden_order_id_formato_valido():
    """Test que orden con order_id con formato válido se crea correctamente."""
    orden = Orden("ORD-001", "Juan", "ABC-123", datetime.now(timezone.utc))
    assert orden.order_id == "ORD-001"


def test_servicio_costo_negativo_lanza_error():
    """Test que servicio con costo negativo lanza error."""
    with pytest.raises(ErrorDominio) as exc_info:
        Servicio("Reparación", Decimal("-100.00"))
    assert exc_info.value.codigo == CodigoError.INVALID_AMOUNT
    assert "debe ser positivo" in exc_info.value.mensaje


def test_servicio_costo_cero_valido():
    """Test que servicio con costo cero es válido."""
    servicio = Servicio("Reparación", Decimal("0.00"))
    assert servicio.costo_mano_obra_estimado == Decimal("0.00")


def test_componente_costo_estimado_negativo_lanza_error():
    """Test que componente con costo estimado negativo lanza error."""
    with pytest.raises(ErrorDominio) as exc_info:
        Componente("Aceite", Decimal("-50.00"))
    assert exc_info.value.codigo == CodigoError.INVALID_AMOUNT
    assert "debe ser positivo" in exc_info.value.mensaje


def test_componente_costo_real_negativo_lanza_error():
    """Test que componente con costo real negativo lanza error."""
    with pytest.raises(ErrorDominio) as exc_info:
        Componente("Aceite", Decimal("50.00"), costo_real=Decimal("-30.00"))
    assert exc_info.value.codigo == CodigoError.INVALID_AMOUNT
    assert "debe ser positivo" in exc_info.value.mensaje


def test_componente_costo_real_none_valido():
    """Test que componente con costo_real None es válido."""
    componente = Componente("Aceite", Decimal("50.00"), costo_real=None)
    assert componente.costo_real is None


def test_componente_costo_cero_valido():
    """Test que componente con costo cero es válido."""
    componente = Componente("Aceite", Decimal("0.00"))
    assert componente.costo_estimado == Decimal("0.00")
    orden = Orden("ORD-001", "Juan", "Auto", datetime.now(timezone.utc))
    orden.estado = EstadoOrden.IN_PROGRESS
    orden.monto_autorizado = None
    
    try:
        orden.intentar_completar()
        assert False, "Debería lanzar ErrorDominio"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.SEQUENCE_ERROR
        assert "no autorizada" in str(e.mensaje).lower()


