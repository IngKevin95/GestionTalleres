"""
Tests de validaciones para órdenes canceladas.

Verifica que todas las operaciones sobre una orden cancelada
lancen las excepciones correctas, protegiendo la integridad del negocio.
"""
from decimal import Decimal
from datetime import datetime, timezone
import pytest

from app.domain.exceptions import ErrorDominio
from app.domain.enums import CodigoError


# ==================== FIXTURES REUTILIZABLES ====================

@pytest.fixture
def orden_taller_ejemplo():
    """Crea una orden de taller con datos realistas de cliente"""
    try:
        from app.domain.models.order import Orden as OrdenModel
        return OrdenModel(
            order_id="ORD-2024-0156",
            cliente="María González Pérez",
            vehiculo="Toyota Corolla 2018 - Placa ABC-123",
            fecha_creacion=datetime.now(timezone.utc)
        )
    except ImportError:
        pytest.skip("Módulo domain.models no disponible")


@pytest.fixture
def servicio_mantenimiento_basico():
    """Crea un servicio de mantenimiento básico típico del taller"""
    try:
        from app.domain.models.service import Servicio as ServicioModel
        return ServicioModel(
            descripcion="Cambio de aceite sintético y filtro",
            costo_mano_obra_estimado=Decimal("50000")  # $50,000 COP
        )
    except ImportError:
        pytest.skip("Módulo domain.models no disponible")


# ==================== TESTS DE VALIDACIÓN ====================

class TestOperacionesProhibidasEnOrdenCancelada:
    """
    Verifica que ninguna operación de negocio se pueda realizar
    sobre una orden que ha sido cancelada por el cliente.
    
    Contexto: Cuando un cliente cancela una orden, el sistema debe
    prevenir cualquier modificación posterior para mantener integridad.
    """

    def test_no_se_puede_agregar_servicio_a_orden_cancelada(
        self, 
        orden_taller_ejemplo, 
        servicio_mantenimiento_basico
    ):
        """
        DADO que tengo una orden cancelada por el cliente
        CUANDO intento agregar un nuevo servicio
        ENTONCES el sistema rechaza la operación con error ORDER_CANCELLED
        """
        # Given - Cliente canceló la orden
        orden_taller_ejemplo.cancelar(motivo="Cliente no autoriza reparación")
        
        # When/Then - Intento agregar servicio debe fallar
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.agregar_servicio(servicio_mantenimiento_basico)
        
        assert error_info.value.codigo == CodigoError.ORDER_CANCELLED, \
            "Debe rechazar agregar servicios a orden cancelada"

    def test_no_se_puede_diagnosticar_orden_ya_cancelada(self, orden_taller_ejemplo):
        """
        DADO que el cliente canceló su orden
        CUANDO el mecánico intenta establecer diagnóstico
        ENTONCES el sistema impide la operación
        """
        # Given - Orden cancelada por cliente
        orden_taller_ejemplo.cancelar(motivo="Cliente desiste de la reparación")
        
        # When/Then - No se puede diagnosticar orden cancelada
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.establecer_estado_diagnosticado()
        
        assert error_info.value.codigo == CodigoError.ORDER_CANCELLED, \
            "No se debe poder diagnosticar una orden cancelada"

    def test_no_se_puede_autorizar_trabajo_en_orden_cancelada(
        self, 
        orden_taller_ejemplo, 
        servicio_mantenimiento_basico
    ):
        """
        DADO que preparé un diagnóstico pero el cliente canceló
        CUANDO intento autorizar el monto de reparación
        ENTONCES el sistema rechaza la autorización
        """
        # Given - Preparar orden con diagnóstico, luego cancelar
        orden_taller_ejemplo.agregar_servicio(servicio_mantenimiento_basico)
        orden_taller_ejemplo.establecer_estado_diagnosticado()
        orden_taller_ejemplo.cancelar(motivo="Cliente decide no reparar vehículo")
        
        # When/Then - No se puede autorizar orden cancelada
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.autorizar(monto=Decimal("55000"))
        
        assert error_info.value.codigo == CodigoError.ORDER_CANCELLED

    def test_no_se_puede_iniciar_trabajo_en_orden_cancelada(self, orden_taller_ejemplo):
        """
        DADO que una orden fue cancelada
        CUANDO intento marcarla como "en proceso"
        ENTONCES el sistema previene iniciar trabajo
        """
        # Given - Orden cancelada
        orden_taller_ejemplo.cancelar(motivo="Cliente no responde llamadas")
        
        # When/Then - No se puede marcar como en proceso
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.establecer_estado_en_proceso()
        
        assert error_info.value.codigo == CodigoError.ORDER_CANCELLED

    def test_no_se_puede_registrar_costo_real_en_orden_cancelada(self, orden_taller_ejemplo):
        """
        DADO que cancelaron una orden de trabajo
        CUANDO el mecánico intenta registrar costos reales
        ENTONCES el sistema rechaza la operación
        """
        # Given - Orden cancelada
        orden_taller_ejemplo.cancelar(motivo="Vehículo fue vendido por el cliente")
        
        # When/Then - No se pueden registrar costos
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.establecer_costo_real(
                servicio_id=1,
                costo_real=Decimal("52000"),
                componentes_reales=None
            )
        
        assert error_info.value.codigo == CodigoError.ORDER_CANCELLED

    def test_no_se_puede_completar_orden_cancelada(self, orden_taller_ejemplo):
        """
        DADO que una orden está cancelada
        CUANDO intento marcarla como completada
        ENTONCES el sistema rechaza completar trabajo no realizado
        """
        # Given - Orden cancelada
        orden_taller_ejemplo.cancelar(motivo="Taller cerrado temporalmente")
        
        # When/Then - No se puede completar
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.intentar_completar()
        
        assert error_info.value.codigo == CodigoError.ORDER_CANCELLED

    def test_no_se_puede_reautorizar_orden_cancelada(self, orden_taller_ejemplo):
        """
        DADO que el cliente canceló su orden
        CUANDO intento ajustar el monto autorizado
        ENTONCES el sistema impide reautorizar
        """
        # Given - Orden cancelada
        orden_taller_ejemplo.cancelar(motivo="Cliente encontró mejor precio")
        
        # When/Then - No se puede reautorizar
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.reautorizar(nuevo_monto=Decimal("60000"))
        
        assert error_info.value.codigo == CodigoError.ORDER_CANCELLED

    def test_no_se_puede_entregar_vehiculo_de_orden_cancelada(self, orden_taller_ejemplo):
        """
        DADO que una orden fue cancelada
        CUANDO intento registrar entrega del vehículo
        ENTONCES el sistema previene marcar como entregado
        """
        # Given - Orden cancelada
        orden_taller_ejemplo.cancelar(motivo="Cliente retiró vehículo sin reparar")
        
        # When/Then - No se puede entregar
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.entregar()
        
        assert error_info.value.codigo == CodigoError.ORDER_CANCELLED


class TestValidacionesSecuenciaEstados:
    """
    Verifica que las operaciones se ejecuten en el orden correcto
    según el flujo de negocio del taller mecánico.
    
    Flujo correcto: CREATED → DIAGNOSED → AUTHORIZED → IN_PROGRESS → COMPLETED → DELIVERED
    """

    def test_no_se_puede_diagnosticar_orden_dos_veces(
        self, 
        orden_taller_ejemplo, 
        servicio_mantenimiento_basico
    ):
        """
        DADO que ya diagnostiqué una orden y la autoricé
        CUANDO intento volver a diagnosticar
        ENTONCES el sistema rechaza por secuencia incorrecta
        """
        # Given - Orden ya diagnosticada y autorizada
        orden_taller_ejemplo.agregar_servicio(servicio_mantenimiento_basico)
        orden_taller_ejemplo.establecer_estado_diagnosticado()
        orden_taller_ejemplo.autorizar(monto=Decimal("55000"))
        
        # When/Then - No se puede volver a diagnosticar
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.establecer_estado_diagnosticado()
        
        assert error_info.value.codigo == CodigoError.SEQUENCE_ERROR, \
            "El diagnóstico solo debe hacerse una vez en estado CREATED"

    def test_no_se_puede_autorizar_antes_de_diagnosticar(
        self, 
        orden_taller_ejemplo, 
        servicio_mantenimiento_basico
    ):
        """
        DADO que agregué servicios a una orden nueva
        CUANDO intento autorizar sin haber diagnosticado
        ENTONCES el sistema exige diagnosticar primero
        """
        # Given - Orden con servicio pero sin diagnosticar
        orden_taller_ejemplo.agregar_servicio(servicio_mantenimiento_basico)
        
        # When/Then - Autorización requiere diagnóstico previo
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.autorizar(monto=Decimal("55000"))
        
        assert error_info.value.codigo == CodigoError.SEQUENCE_ERROR

    def test_no_se_puede_autorizar_orden_sin_servicios(self, orden_taller_ejemplo):
        """
        DADO que diagnostiqué una orden pero no agregué servicios
        CUANDO intento autorizar
        ENTONCES el sistema rechaza por falta de servicios
        """
        # Given - Orden diagnosticada sin servicios
        orden_taller_ejemplo.establecer_estado_diagnosticado()
        
        # When/Then - Autorización requiere al menos un servicio
        with pytest.raises(ErrorDominio) as error_info:
            orden_taller_ejemplo.autorizar(monto=Decimal("55000"))
        
        assert error_info.value.codigo == CodigoError.NO_SERVICES, \
            "No se puede autorizar sin servicios registrados"


class TestRegistroCostosRealesConComponentes:
    """
    Verifica el correcto manejo de costos reales de servicios
    incluyendo el detalle de componentes utilizados.
    
    Casos de uso:
    - Registrar costo con detalle de cada componente
    - Actualizar costo sin detalle (limpia componentes previos)
    """

    def test_registrar_costo_real_con_detalle_de_cada_componente(self):
        """
        DADO que completé un servicio usando múltiples componentes
        CUANDO registro el costo real especificando cada componente
        ENTONCES el sistema actualiza correctamente todos los costos
        
        Caso real: Cambio de pastillas de freno con 2 componentes
        """
        try:
            from app.domain.models.order import Orden as OrdenModel
            from app.domain.models.service import Servicio as ServicioModel
            from app.domain.models.component import Componente as ComponenteModel
            
            # Given - Orden con servicio de frenos y componentes
            orden = OrdenModel(
                "ORD-2024-0200",
                "Carlos Rodríguez Méndez",
                "Chevrolet Spark 2015 - XYZ-789",
                datetime.now(timezone.utc)
            )
            
            servicio_frenos = ServicioModel(
                "Cambio completo de pastillas de freno",
                Decimal("80000")  # Estimado inicial
            )
            
            # Componentes utilizados
            pastilla_delantera = ComponenteModel(
                "Pastilla freno delantera (2 unidades)",
                Decimal("35000")
            )
            pastilla_delantera.id_componente = 1
            
            pastilla_trasera = ComponenteModel(
                "Pastilla freno trasera (2 unidades)",
                Decimal("25000")
            )
            pastilla_trasera.id_componente = 2
            
            servicio_frenos.componentes = [pastilla_delantera, pastilla_trasera]
            servicio_frenos.id_servicio = 1
            
            # Preparar orden autorizada
            orden.agregar_servicio(servicio_frenos)
            orden.establecer_estado_diagnosticado()
            orden.autorizar(Decimal("90000"))
            orden.establecer_estado_en_proceso()
            
            # When - Registrar costos reales con detalle
            costos_componentes = {
                1: Decimal("38000"),  # Pastillas delanteras costaron más
                2: Decimal("27000")   # Pastillas traseras costaron más
            }
            orden.establecer_costo_real(1, Decimal("85000"), costos_componentes)
            
            # Then - Verificar actualización correcta
            assert servicio_frenos.costo_real == Decimal("85000"), \
                "Costo total del servicio debe actualizarse"
            assert pastilla_delantera.costo_real == Decimal("38000"), \
                "Costo de pastilla delantera debe registrarse"
            assert pastilla_trasera.costo_real == Decimal("27000"), \
                "Costo de pastilla trasera debe registrarse"
            
        except ImportError:
            pytest.skip("Módulo domain.models no disponible")

    def test_registrar_costo_real_sin_detalle_limpia_costos_previos(self):
        """
        DADO que un servicio tenía costos reales en componentes
        CUANDO actualizo el costo real sin especificar componentes
        ENTONCES el sistema limpia los costos previos
        
        Caso real: Ajuste de precio sin desglose de componentes
        """
        try:
            from app.domain.models.order import Orden as OrdenModel
            from app.domain.models.service import Servicio as ServicioModel
            from app.domain.models.component import Componente as ComponenteModel
            
            # Given - Servicio con componente que ya tiene costo real
            orden = OrdenModel(
                "ORD-2024-0201",
                "Ana Martínez Torres",
                "Mazda 3 2019 - LMN-456",
                datetime.now(timezone.utc)
            )
            
            servicio = ServicioModel(
                "Alineación y balanceo completo",
                Decimal("60000")
            )
            
            componente_balanceo = ComponenteModel(
                "Plomos de balanceo",
                Decimal("5000")
            )
            componente_balanceo.costo_real = Decimal("6000")  # Ya tenía costo
            
            servicio.componentes = [componente_balanceo]
            servicio.id_servicio = 1
            
            # Preparar orden
            orden.agregar_servicio(servicio)
            orden.establecer_estado_diagnosticado()
            orden.autorizar(Decimal("70000"))
            orden.establecer_estado_en_proceso()
            
            # When - Registrar costo sin detalle de componentes
            orden.establecer_costo_real(1, Decimal("65000"), None)
            
            # Then - Costo de componente debe limpiarse
            assert servicio.costo_real == Decimal("65000"), \
                "Costo total del servicio debe actualizarse"
            assert componente_balanceo.costo_real is None, \
                "El costo del componente debe limpiarse al no especificar detalle"
            
        except ImportError:
            pytest.skip("Módulo domain.models no disponible")

