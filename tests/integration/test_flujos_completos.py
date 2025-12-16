"""Tests de integración end-to-end para flujos completos del sistema.

Valida escenarios complejos con múltiples órdenes, reautorizaciones,
cancelaciones y batches grandes de comandos.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock

from app.domain.entidades.order import Orden
from app.domain.entidades.service import Servicio
from app.domain.entidades.component import Componente
from app.domain.enums import EstadoOrden, CodigoError
from app.domain.exceptions import ErrorDominio
from app.domain.dinero import redondear_mitad_par
from app.domain.zona_horaria import ahora


def test_flujo_multiple_ordenes_paralelas():
    """Test de múltiples órdenes procesadas en paralelo."""
    orden1 = Orden("ORD-001", "Cliente1", "ABC-123", ahora())
    orden2 = Orden("ORD-002", "Cliente2", "XYZ-789", ahora())
    
    servicio1 = Servicio("Mantenimiento", Decimal("5000.00"))
    servicio2 = Servicio("Reparación", Decimal("8000.00"))
    
    orden1.servicios.append(servicio1)
    orden2.servicios.append(servicio2)
    
    orden1.establecer_estado_diagnosticado()
    orden2.establecer_estado_diagnosticado()
    
    subtotal1 = sum(s.calcular_subtotal_estimado() for s in orden1.servicios)
    subtotal2 = sum(s.calcular_subtotal_estimado() for s in orden2.servicios)
    
    monto1 = redondear_mitad_par(subtotal1 * Decimal("1.16"), 2)
    monto2 = redondear_mitad_par(subtotal2 * Decimal("1.16"), 2)
    
    orden1.autorizar(monto1)
    orden2.autorizar(monto2)
    
    assert orden1.estado == EstadoOrden.AUTHORIZED
    assert orden2.estado == EstadoOrden.AUTHORIZED
    assert orden1.monto_autorizado == monto1
    assert orden2.monto_autorizado == monto2


def test_flujo_reautorizacion_multiple():
    """Test de reautorización múltiple de una orden."""
    orden = Orden("ORD-001", "Cliente", "ABC-123", ahora())
    servicio = Servicio("Reparación", Decimal("10000.00"))
    orden.servicios.append(servicio)
    
    orden.establecer_estado_diagnosticado()
    subtotal = Decimal("10000.00")
    monto1 = redondear_mitad_par(subtotal * Decimal("1.16"), 2)
    orden.autorizar(monto1)
    
    assert orden.version_autorizacion == 1
    
    orden.establecer_estado_en_proceso()
    servicio.costo_real = Decimal("15000.00")
    servicio.completado = True
    orden._recalcular_total_real()
    
    limite = redondear_mitad_par(monto1 * Decimal("1.10"), 2)
    assert orden.total_real > limite
    
    with pytest.raises(ErrorDominio) as exc_info:
        orden.intentar_completar()
    assert exc_info.value.codigo == CodigoError.REQUIRES_REAUTH
    assert orden.estado == EstadoOrden.WAITING_FOR_APPROVAL
    
    monto2 = Decimal("18000.00")
    orden.reautorizar(monto2)
    assert orden.version_autorizacion == 2
    assert orden.estado == EstadoOrden.AUTHORIZED
    
    orden.establecer_estado_en_proceso()
    nuevo_limite = redondear_mitad_par(monto2 * Decimal("1.10"), 2)
    assert orden.total_real <= nuevo_limite
    
    orden.intentar_completar()
    assert orden.estado == EstadoOrden.COMPLETED


def test_flujo_cancelacion_bloquea_operaciones():
    """Test que cancelación bloquea todas las operaciones."""
    orden = Orden("ORD-001", "Cliente", "ABC-123", ahora())
    servicio = Servicio("Reparación", Decimal("5000.00"))
    orden.servicios.append(servicio)
    
    orden.establecer_estado_diagnosticado()
    subtotal = Decimal("5000.00")
    monto = redondear_mitad_par(subtotal * Decimal("1.16"), 2)
    orden.autorizar(monto)
    
    orden.cancelar("Cliente canceló")
    assert orden.estado == EstadoOrden.CANCELLED
    assert orden.fecha_cancelacion is not None
    
    with pytest.raises(ErrorDominio) as exc_info:
        orden.agregar_servicio(Servicio("Otro", Decimal("1000.00")))
    assert exc_info.value.codigo == CodigoError.ORDER_CANCELLED
    
    with pytest.raises(ErrorDominio) as exc_info:
        orden.establecer_estado_en_proceso()
    assert exc_info.value.codigo == CodigoError.ORDER_CANCELLED
    
    with pytest.raises(ErrorDominio) as exc_info:
        orden.intentar_completar()
    assert exc_info.value.codigo == CodigoError.ORDER_CANCELLED


def test_flujo_batch_grande():
    """Test de procesamiento de batch grande de comandos."""
    ordenes = []
    for i in range(10):
        orden = Orden(f"ORD-{i:03d}", f"Cliente{i}", f"ABC-{i:03d}", ahora())
        servicio = Servicio(f"Servicio{i}", Decimal(f"{1000 + i * 100}.00"))
        orden.servicios.append(servicio)
        ordenes.append(orden)
    
    for orden in ordenes:
        orden.establecer_estado_diagnosticado()
        subtotal = sum(s.calcular_subtotal_estimado() for s in orden.servicios)
        monto = redondear_mitad_par(subtotal * Decimal("1.16"), 2)
        orden.autorizar(monto)
        assert orden.estado == EstadoOrden.AUTHORIZED
        assert orden.monto_autorizado == monto
    
    assert len(ordenes) == 10
    assert all(o.estado == EstadoOrden.AUTHORIZED for o in ordenes)


def test_flujo_con_errores_y_recuperacion():
    """Test de flujo con errores y recuperación."""
    orden = Orden("ORD-001", "Cliente", "ABC-123", ahora())
    
    with pytest.raises(ErrorDominio) as exc_info:
        orden.autorizar(Decimal("1000.00"))
    assert exc_info.value.codigo == CodigoError.SEQUENCE_ERROR
    
    orden.establecer_estado_diagnosticado()
    
    with pytest.raises(ErrorDominio) as exc_info:
        orden.autorizar(Decimal("1000.00"))
    assert exc_info.value.codigo == CodigoError.NO_SERVICES
    
    servicio = Servicio("Reparación", Decimal("5000.00"))
    orden.servicios.append(servicio)
    
    subtotal = Decimal("5000.00")
    monto = redondear_mitad_par(subtotal * Decimal("1.16"), 2)
    orden.autorizar(monto)
    assert orden.estado == EstadoOrden.AUTHORIZED

