"""Tests adicionales para aumentar cobertura de domain.models"""
from decimal import Decimal
from datetime import datetime
import pytest

from app.domain.exceptions import ErrorDominio
from app.domain.enums import CodigoError


def test_orden_models_agregar_servicio_cancelada():
    """Test que agregar servicio a orden cancelada lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        orden.cancelar(motivo="Test")
        from app.domain.models.service import Servicio as ServicioModel
        servicio = ServicioModel("Servicio", Decimal("1000"))
        with pytest.raises(ErrorDominio) as exc:
            orden.agregar_servicio(servicio)
        assert exc.value.codigo == CodigoError.ORDER_CANCELLED
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_establecer_diagnosticado_cancelada():
    """Test que establecer diagnosticado en orden cancelada lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        orden.cancelar(motivo="Test")
        with pytest.raises(ErrorDominio) as exc:
            orden.establecer_estado_diagnosticado()
        assert exc.value.codigo == CodigoError.ORDER_CANCELLED
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_establecer_diagnosticado_estado_invalido():
    """Test que establecer diagnosticado desde estado inválido lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        from app.domain.models.service import Servicio as ServicioModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        servicio = ServicioModel("Servicio", Decimal("1000"))
        orden.agregar_servicio(servicio)
        orden.establecer_estado_diagnosticado()
        orden.autorizar(Decimal("1100"))
        with pytest.raises(ErrorDominio) as exc:
            orden.establecer_estado_diagnosticado()
        assert exc.value.codigo == CodigoError.SEQUENCE_ERROR
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_autorizar_cancelada():
    """Test que autorizar orden cancelada lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        from app.domain.models.service import Servicio as ServicioModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        servicio = ServicioModel("Servicio", Decimal("1000"))
        orden.agregar_servicio(servicio)
        orden.establecer_estado_diagnosticado()
        orden.cancelar(motivo="Test")
        with pytest.raises(ErrorDominio) as exc:
            orden.autorizar(Decimal("1100"))
        assert exc.value.codigo == CodigoError.ORDER_CANCELLED
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_autorizar_estado_invalido():
    """Test que autorizar desde estado inválido lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        from app.domain.models.service import Servicio as ServicioModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        servicio = ServicioModel("Servicio", Decimal("1000"))
        orden.agregar_servicio(servicio)
        with pytest.raises(ErrorDominio) as exc:
            orden.autorizar(Decimal("1100"))
        assert exc.value.codigo == CodigoError.SEQUENCE_ERROR
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_autorizar_sin_servicios():
    """Test que autorizar sin servicios lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        orden.establecer_estado_diagnosticado()
        with pytest.raises(ErrorDominio) as exc:
            orden.autorizar(Decimal("1100"))
        assert exc.value.codigo == CodigoError.NO_SERVICES
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_establecer_en_proceso_cancelada():
    """Test que establecer en proceso orden cancelada lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        orden.cancelar(motivo="Test")
        with pytest.raises(ErrorDominio) as exc:
            orden.establecer_estado_en_proceso()
        assert exc.value.codigo == CodigoError.ORDER_CANCELLED
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_establecer_costo_real_cancelada():
    """Test que establecer costo real en orden cancelada lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        orden.cancelar(motivo="Test")
        with pytest.raises(ErrorDominio) as exc:
            orden.establecer_costo_real("SERV-1", Decimal("1000"), True)
        assert exc.value.codigo == CodigoError.ORDER_CANCELLED
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_intentar_completar_cancelada():
    """Test que intentar completar orden cancelada lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        orden.cancelar(motivo="Test")
        with pytest.raises(ErrorDominio) as exc:
            orden.intentar_completar()
        assert exc.value.codigo == CodigoError.ORDER_CANCELLED
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_reautorizar_cancelada():
    """Test que reautorizar orden cancelada lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        orden.cancelar(motivo="Test")
        with pytest.raises(ErrorDominio) as exc:
            orden.reautorizar(Decimal("1200"))
        assert exc.value.codigo == CodigoError.ORDER_CANCELLED
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_entregar_cancelada():
    """Test que entregar orden cancelada lanza excepción"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        orden.cancelar(motivo="Test")
        with pytest.raises(ErrorDominio) as exc:
            orden.entregar()
        assert exc.value.codigo == CodigoError.ORDER_CANCELLED
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_establecer_costo_real_con_componentes_reales():
    """Test establecer costo real con componentes_reales especificados"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        from app.domain.models.service import Servicio as ServicioModel
        from app.domain.models.component import Componente as ComponenteModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        servicio = ServicioModel("Servicio", Decimal("1000"))
        comp1 = ComponenteModel("Componente 1", Decimal("50"))
        comp1.id_componente = 1
        comp2 = ComponenteModel("Componente 2", Decimal("30"))
        comp2.id_componente = 2
        servicio.componentes = [comp1, comp2]
        servicio.id_servicio = 1
        orden.agregar_servicio(servicio)
        orden.establecer_estado_diagnosticado()
        orden.autorizar(Decimal("1200"))
        orden.establecer_estado_en_proceso()
        
        # Establecer costo real con componentes_reales
        orden.establecer_costo_real(1, Decimal("1100"), {1: Decimal("60"), 2: Decimal("35")})
        
        assert servicio.costo_real == Decimal("1100")
        assert comp1.costo_real == Decimal("60")
        assert comp2.costo_real == Decimal("35")
    except ImportError:
        pytest.skip("domain.models not available")


def test_orden_models_establecer_costo_real_sin_componentes_reales():
    """Test establecer costo real sin componentes_reales (limpia componentes)"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        from app.domain.models.service import Servicio as ServicioModel
        from app.domain.models.component import Componente as ComponenteModel
        orden = OrdenModel("ORD-001", "Cliente", "Veh", datetime.utcnow())
        servicio = ServicioModel("Servicio", Decimal("1000"))
        comp1 = ComponenteModel("Componente 1", Decimal("50"))
        comp1.costo_real = Decimal("60")  # Ya tenía costo real
        servicio.componentes = [comp1]
        servicio.id_servicio = 1
        orden.agregar_servicio(servicio)
        orden.establecer_estado_diagnosticado()
        orden.autorizar(Decimal("1200"))
        orden.establecer_estado_en_proceso()
        
        # Establecer costo real sin componentes_reales (debería limpiar costos de componentes)
        orden.establecer_costo_real(1, Decimal("1100"), None)
        
        assert servicio.costo_real == Decimal("1100")
        assert comp1.costo_real is None  # Debe haberse limpiado
    except ImportError:
        pytest.skip("domain.models not available")
