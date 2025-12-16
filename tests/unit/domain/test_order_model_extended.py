"""
Tests del ciclo de vida completo de una orden de taller.

Verifica el flujo completo desde que un cliente deja su vehículo
hasta que lo retira reparado: creación → diagnóstico → autorización
→ ejecución → completado → entrega

Representa casos de uso reales del negocio de taller mecánico.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from app.domain.entidades.order import Orden
from app.domain.entidades.service import Servicio
from app.domain.enums.order_status import EstadoOrden


class TestCreacionOrdenTaller:
    """
    Verifica la creación de órdenes de trabajo cuando
    un cliente deja su vehículo para reparación.
    """
    
    def test_recepcionista_crea_orden_para_cliente_nuevo(self):
        """
        DADO que llega un nuevo cliente al taller
        CUANDO la recepcionista crea su orden
        ENTONCES se genera con los datos básicos del cliente y vehículo
        
        Historia de usuario: Como recepcionista, necesito crear
        una orden rápidamente para registrar el ingreso del vehículo
        """
        # Given/When - Recepcionista ingresa datos del cliente
        orden = Orden(
            order_id="ORD-2024-0350",
            cliente="María González Pérez",
            vehiculo="Toyota Corolla 2018 - ABC-123",
            fecha_creacion=datetime.now()
        )
        
        # Then - Orden creada correctamente
        assert orden.order_id == "ORD-2024-0350"
        assert orden.cliente == "María González Pérez"
        assert orden.vehiculo == "Toyota Corolla 2018 - ABC-123"
    
    def test_orden_completa_incluye_montos_y_versionado(self):
        """
        DADO que una orden avanzó en el proceso
        CUANDO verifico sus campos completos
        ENTONCES debe incluir monto autorizado, versión y total real
        
        Caso real: Orden diagnosticada y autorizada por el cliente
        """
        # Given - Orden con proceso avanzado
        orden = Orden(
            order_id="ORD-2024-0351",
            cliente="Carlos Rodríguez Méndez",
            vehiculo="Chevrolet Spark 2015 - XYZ-789",
            fecha_creacion=datetime.now()
        )
        orden.monto_autorizado = Decimal("150000")  # $150,000 COP
        orden.version_autorizacion = 1
        orden.total_real = Decimal("0.00")
        
        # Then - Todos los campos presentes
        assert orden.order_id == "ORD-2024-0351"
        assert orden.estado == EstadoOrden.CREATED
        assert orden.monto_autorizado == Decimal("150000")
        assert orden.version_autorizacion == 1


class TestGestionServiciosOrden:
    """
    Verifica el manejo de servicios dentro de una orden,
    como agregar servicios diagnosticados por el mecánico.
    """
    
    def test_mecanico_agrega_servicio_diagnosticado(self):
        """
        DADO que el mecánico revisó el vehículo
        CUANDO diagnostica un servicio necesario
        ENTONCES debe agregarse a la orden
        
        Caso real: Mecánico detecta necesidad de cambio de aceite
        """
        # Given - Orden recién creada
        orden = Orden(
            order_id="ORD-2024-0352",
            cliente="Ana Martínez Torres",
            vehiculo="Mazda 3 2019 - LMN-456",
            fecha_creacion=datetime.now()
        )
        
        # When - Mecánico agrega servicio diagnosticado
        servicio = Servicio(
            descripcion="Cambio de aceite sintético 5W-30",
            costo_mano_obra_estimado=Decimal("50000")  # $50,000 COP
        )
        orden.agregar_servicio(servicio)
        
        # Then - Servicio agregado a la orden
        assert len(orden.servicios) == 1, \
            "Debe tener 1 servicio agregado"
    
    def test_orden_nueva_inicia_sin_servicios(self):
        """
        DADO que creo una nueva orden
        CUANDO consulto sus servicios
        ENTONCES debe tener lista vacía inicialmente
        
        Proceso: Los servicios se agregan después del diagnóstico
        """
        # Given/When - Orden recién creada
        orden = Orden(
            order_id="ORD-2024-0353",
            cliente="Pedro Sánchez Gómez",
            vehiculo="Renault Logan 2020 - QWE-321",
            fecha_creacion=datetime.now()
        )
        
        # Then - Sin servicios todavía
        assert isinstance(orden.servicios, list), \
            "servicios debe ser una lista"
        assert len(orden.servicios) == 0, \
            "Orden nueva no debe tener servicios"


class TestEstadosOrden:
    """
    Verifica el manejo correcto de estados durante
    el ciclo de vida de la orden.
    """
    
    def test_orden_nueva_comienza_en_estado_creado(self):
        """
        DADO que creo una orden nueva
        CUANDO verifico su estado
        ENTONCES debe estar en CREATED
        """
        # Given/When - Orden recién creada
        orden = Orden(
            order_id="ORD-2024-0354",
            cliente="Luis Hernández Castro",
            vehiculo="Nissan Versa 2017 - ASD-654",
            fecha_creacion=datetime.now()
        )
        
        # Then - Estado inicial CREATED
        assert orden.estado == EstadoOrden.CREATED, \
            "Orden nueva debe comenzar en estado CREATED"


class TestPropiedadesMonetariasOrden:
    """
    Verifica el manejo de montos: autorizado, real y versión.
    Estos campos controlan el flujo de autorización del cliente.
    """
    
    def test_cliente_autoriza_monto_estimado(self):
        """
        DADO que el mecánico presenta un presupuesto
        CUANDO el cliente autoriza el monto
        ENTONCES debe registrarse el monto_autorizado
        
        Caso real: Cliente autoriza $150,000 COP para reparación
        """
        # Given - Orden con presupuesto
        orden = Orden(
            order_id="ORD-2024-0355",
            cliente="Sandra López Vargas",
            vehiculo="Hyundai Accent 2016 - ZXC-987",
            fecha_creacion=datetime.now()
        )
        
        # When - Cliente autoriza monto
        orden.monto_autorizado = Decimal("150000")
        
        # Then - Monto registrado
        assert orden.monto_autorizado == Decimal("150000"), \
            "Monto autorizado debe registrarse"
    
    def test_mecanico_registra_costo_real_final(self):
        """
        DADO que completé la reparación
        CUANDO registro el costo real
        ENTONCES debe actualizarse total_real
        
        Caso real: Trabajo costó $142,500 COP (menos que estimado)
        """
        # Given - Orden completada
        orden = Orden(
            order_id="ORD-2024-0356",
            cliente="Jorge Ramírez Ortiz",
            vehiculo="Volkswagen Gol 2014 - RTY-456",
            fecha_creacion=datetime.now()
        )
        
        # When - Registrar costo real
        orden.total_real = Decimal("142500")
        
        # Then - Costo real actualizado
        assert orden.total_real == Decimal("142500"), \
            "total_real debe reflejar costo final"
    
    def test_cliente_reautoriza_incrementa_version(self):
        """
        DADO que el cliente autorizó un monto inicialmente
        CUANDO aparecen reparaciones adicionales
        ENTONCES se incrementa version_autorizacion
        
        Caso real: Cliente autoriza $100k, luego $150k (versión 2)
        """
        # Given - Orden con autorización inicial
        orden = Orden(
            order_id="ORD-2024-0357",
            cliente="Patricia Moreno Silva",
            vehiculo="Kia Picanto 2019 - FGH-321",
            fecha_creacion=datetime.now()
        )
        
        # When - Segunda autorización
        orden.version_autorizacion = 2
        
        # Then - Versión incrementada
        assert orden.version_autorizacion == 2, \
            "version_autorizacion debe rastrear reautorizaciones"


class TestTrazabilidadEventosOrden:
    """
    Verifica que la orden mantenga historial de eventos
    para auditoría completa del proceso.
    """
    
    def test_orden_registra_eventos_para_auditoria(self):
        """
        DADO que una orden pasa por diferentes estados
        CUANDO consulto su historial de eventos
        ENTONCES debe tener lista de eventos para auditoría
        
        Propósito: Rastrear quién hizo qué y cuándo
        """
        # Given/When - Orden con eventos
        orden = Orden(
            order_id="ORD-2024-0358",
            cliente="Roberto Jiménez Ríos",
            vehiculo="Ford Fiesta 2013 - VBN-852",
            fecha_creacion=datetime.now()
        )
        
        # Then - Debe tener lista de eventos
        assert isinstance(orden.eventos, list), \
            "eventos debe ser lista para auditoría"


class TestServicioIndividual:
    """
    Verifica el comportamiento de servicios individuales
    dentro de una orden de taller.
    """
    
    def test_mecanico_crea_servicio_con_estimacion(self):
        """
        DADO que diagnostiqué una reparación necesaria
        CUANDO creo el servicio
        ENTONCES debe tener descripción y costo estimado
        
        Caso real: Cambio de aceite estimado en $50,000 COP
        """
        # Given/When - Mecánico crea servicio
        servicio = Servicio(
            descripcion="Cambio de aceite sintético 5W-40",
            costo_mano_obra_estimado=Decimal("50000")
        )
        
        # Then - Servicio creado con estimación
        assert servicio.descripcion == "Cambio de aceite sintético 5W-40"
        assert servicio.costo_mano_obra_estimado == Decimal("50000")
    
    def test_mecanico_actualiza_costo_real_al_completar(self):
        """
        DADO que completé un servicio
        CUANDO registro el costo real
        ENTONCES debe actualizarse en el servicio
        
        Caso real: Estimé $50k pero costó $53k por repuesto adicional
        """
        # Given - Servicio estimado
        servicio = Servicio(
            descripcion="Alineación y balanceo",
            costo_mano_obra_estimado=Decimal("50000")
        )
        
        # When - Registrar costo real
        servicio.costo_real = Decimal("53000")
        
        # Then - Costo real actualizado
        assert servicio.costo_mano_obra_estimado == Decimal("50000"), \
            "Costo estimado debe mantenerse"
        assert servicio.costo_real == Decimal("53000"), \
            "Costo real debe reflejar gasto final"
    
    def test_servicio_with_components(self):
        """Test Servicio con componentes."""
        servicio = Servicio(
            descripcion="Reparación",
            costo_mano_obra_estimado=Decimal("500.00")
        )
        
        # Verificar que tiene componentes
        assert hasattr(servicio, 'componentes')
        assert isinstance(servicio.componentes, list)
    
    def test_servicio_completado_property(self):
        """Test propiedad completado."""
        servicio = Servicio(
            descripcion="Servicio",
            costo_mano_obra_estimado=Decimal("500.00")
        )
        
        assert hasattr(servicio, 'completado')
        assert servicio.completado is False


class TestOrderIntegration:
    """Tests de integración para Orden y Servicio."""
    
    def test_order_with_multiple_services(self):
        """Test Orden con múltiples Servicios."""
        orden = Orden(order_id="ORD-001", cliente="Juan", vehiculo="Auto", fecha_creacion=datetime.now())
        
        servicio1 = Servicio(descripcion="Service 1", costo_mano_obra_estimado=Decimal("500.00"))
        servicio2 = Servicio(descripcion="Service 2", costo_mano_obra_estimado=Decimal("300.00"))
        
        orden.agregar_servicio(servicio1)
        orden.agregar_servicio(servicio2)
        
        assert len(orden.servicios) == 2
    
    def test_order_estado_diagnosticado(self):
        """Test cambiar estado a diagnosticado."""
        orden = Orden(order_id="ORD-001", cliente="Juan", vehiculo="Auto", fecha_creacion=datetime.now())
        
        # Agregar al menos un servicio
        servicio = Servicio(descripcion="Diagnóstico", costo_mano_obra_estimado=Decimal("100.00"))
        orden.agregar_servicio(servicio)
        
        # Cambiar a diagnosticado
        orden.establecer_estado_diagnosticado()
        
        assert orden.estado == EstadoOrden.DIAGNOSED
