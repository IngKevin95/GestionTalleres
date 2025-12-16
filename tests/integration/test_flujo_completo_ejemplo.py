"""Test de integración end-to-end del flujo completo del ejemplo del documento de evaluación técnica.

Valida el flujo completo desde creación hasta entrega, incluyendo:
- Creación de orden
- Agregado de servicio con componentes
- Transiciones de estado
- Autorización con cálculo de IVA
- Validación del límite 110%
- Reautorización si aplica
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


def test_flujo_completo_ejemplo_documento_excede_110():
    """Test del flujo completo del ejemplo del documento que excede el 110%."""
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
    
    assert orden.estado == EstadoOrden.CREATED
    assert len(orden.servicios) == 1
    
    orden.establecer_estado_diagnosticado()
    assert orden.estado == EstadoOrden.DIAGNOSED
    
    subtotal_estimado = sum(s.calcular_subtotal_estimado() for s in orden.servicios)
    assert subtotal_estimado == Decimal("11500.00")
    
    monto_autorizado = redondear_mitad_par(subtotal_estimado * Decimal("1.16"), 2)
    assert monto_autorizado == Decimal("13340.00")
    
    orden.autorizar(monto_autorizado)
    assert orden.estado == EstadoOrden.AUTHORIZED
    assert orden.monto_autorizado == Decimal("13340.00")
    assert orden.version_autorizacion == 1
    
    orden.establecer_estado_en_proceso()
    assert orden.estado == EstadoOrden.IN_PROGRESS
    
    servicio.costo_real = Decimal("15000.00")
    servicio.completado = True
    orden._recalcular_total_real()
    
    assert orden.total_real == Decimal("15000.00")
    
    limite_110 = redondear_mitad_par(monto_autorizado * Decimal("1.10"), 2)
    assert limite_110 == Decimal("14674.00")
    assert orden.total_real > limite_110
    
    with pytest.raises(ErrorDominio) as exc_info:
        orden.intentar_completar()
    
    assert exc_info.value.codigo == CodigoError.REQUIRES_REAUTH
    assert orden.estado == EstadoOrden.WAITING_FOR_APPROVAL
    
    nuevo_monto = Decimal("17400.00")
    orden.reautorizar(nuevo_monto)
    assert orden.estado == EstadoOrden.AUTHORIZED
    assert orden.monto_autorizado == nuevo_monto
    assert orden.version_autorizacion == 2
    
    orden.establecer_estado_en_proceso()
    assert orden.estado == EstadoOrden.IN_PROGRESS
    
    nuevo_limite = redondear_mitad_par(nuevo_monto * Decimal("1.10"), 2)
    assert orden.total_real <= nuevo_limite
    
    orden.intentar_completar()
    assert orden.estado == EstadoOrden.COMPLETED
    
    orden.entregar()
    assert orden.estado == EstadoOrden.DELIVERED


def test_flujo_completo_ejemplo_documento_dentro_limite():
    """Test del flujo completo cuando el costo real está dentro del límite 110%."""
    orden = Orden(
        order_id="R002",
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
    
    orden.establecer_estado_en_proceso()
    
    servicio.costo_real = Decimal("13000.00")
    servicio.completado = True
    orden._recalcular_total_real()
    
    limite_110 = redondear_mitad_par(monto_autorizado * Decimal("1.10"), 2)
    assert orden.total_real <= limite_110
    
    orden.intentar_completar()
    assert orden.estado == EstadoOrden.COMPLETED
    
    orden.entregar()
    assert orden.estado == EstadoOrden.DELIVERED


def test_flujo_completo_ejemplo_documento_exactamente_110():
    """Test del flujo completo cuando el costo real es exactamente el 110%."""
    orden = Orden(
        order_id="R003",
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
    
    orden.establecer_estado_en_proceso()
    
    limite_110 = redondear_mitad_par(monto_autorizado * Decimal("1.10"), 2)
    servicio.costo_real = limite_110
    servicio.completado = True
    orden._recalcular_total_real()
    
    assert orden.total_real == limite_110
    
    orden.intentar_completar()
    assert orden.estado == EstadoOrden.COMPLETED
    
    orden.entregar()
    assert orden.estado == EstadoOrden.DELIVERED

