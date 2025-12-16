"""Test del ejemplo numérico de referencia del documento de evaluación técnica.

Valida los cálculos exactos:
- Subtotal estimado: 11,500.00
- IVA 16%: 1,840.00
- Monto autorizado: 13,340.00
- Límite 110%: 14,674.00
"""

import pytest
from decimal import Decimal

from app.domain.entidades.order import Orden
from app.domain.entidades.service import Servicio
from app.domain.entidades.component import Componente
from app.domain.enums import EstadoOrden
from app.domain.dinero import redondear_mitad_par
from app.domain.zona_horaria import ahora


def test_ejemplo_numerico_referencia_autorizacion():
    """Valida el cálculo de autorización con los valores exactos del documento."""
    orden = Orden(
        order_id="R001",
        cliente="ACME",
        vehiculo="ABC-123",
        fecha_creacion=ahora()
    )
    
    servicio = Servicio(
        descripcion="Engine repair",
        costo_mano_obra_estimado=Decimal("10000.00")
    )
    
    componente = Componente(
        descripcion="Oil pump",
        costo_estimado=Decimal("1500.00")
    )
    servicio.componentes.append(componente)
    orden.servicios.append(servicio)
    
    orden.establecer_estado_diagnosticado()
    
    subtotal_estimado = sum(s.calcular_subtotal_estimado() for s in orden.servicios)
    assert subtotal_estimado == Decimal("11500.00"), f"Subtotal esperado 11500.00, obtenido {subtotal_estimado}"
    
    monto_autorizado = redondear_mitad_par(subtotal_estimado * Decimal("1.16"), 2)
    assert monto_autorizado == Decimal("13340.00"), f"Monto autorizado esperado 13340.00, obtenido {monto_autorizado}"
    
    orden.autorizar(monto_autorizado)
    assert orden.monto_autorizado == Decimal("13340.00")
    assert orden.estado == EstadoOrden.AUTHORIZED


def test_ejemplo_numerico_referencia_limite_110():
    """Valida el cálculo del límite 110% con los valores exactos del documento."""
    orden = Orden(
        order_id="R001",
        cliente="ACME",
        vehiculo="ABC-123",
        fecha_creacion=ahora()
    )
    
    servicio = Servicio(
        descripcion="Engine repair",
        costo_mano_obra_estimado=Decimal("10000.00")
    )
    
    componente = Componente(
        descripcion="Oil pump",
        costo_estimado=Decimal("1500.00")
    )
    servicio.componentes.append(componente)
    orden.servicios.append(servicio)
    
    orden.establecer_estado_diagnosticado()
    
    subtotal_estimado = Decimal("11500.00")
    monto_autorizado = redondear_mitad_par(subtotal_estimado * Decimal("1.16"), 2)
    orden.autorizar(monto_autorizado)
    
    limite_110 = redondear_mitad_par(monto_autorizado * Decimal("1.10"), 2)
    assert limite_110 == Decimal("14674.00"), f"Límite 110% esperado 14674.00, obtenido {limite_110}"
    
    orden.establecer_estado_en_proceso()
    
    servicio.costo_real = Decimal("15000.00")
    servicio.completado = True
    orden._recalcular_total_real()
    
    assert orden.total_real == Decimal("15000.00")
    assert orden.total_real > limite_110, "El costo real debe exceder el límite 110%"
    
    with pytest.raises(Exception) as exc_info:
        orden.intentar_completar()
    
    assert orden.estado == EstadoOrden.WAITING_FOR_APPROVAL


def test_ejemplo_numerico_referencia_calculo_iva():
    """Valida que el IVA se calcula correctamente como 16% del subtotal."""
    subtotal = Decimal("11500.00")
    iva_esperado = subtotal * Decimal("0.16")
    assert iva_esperado == Decimal("1840.00"), f"IVA esperado 1840.00, obtenido {iva_esperado}"
    
    monto_con_iva = subtotal * Decimal("1.16")
    monto_autorizado = redondear_mitad_par(monto_con_iva, 2)
    assert monto_autorizado == Decimal("13340.00"), f"Monto con IVA esperado 13340.00, obtenido {monto_autorizado}"

