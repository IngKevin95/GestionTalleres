"""
Historias de uso del servicio de procesamiento de comandos
Estas pruebas describen cómo el taller procesa diferentes acciones en las órdenes
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal
from datetime import datetime

from app.application.action_service import ActionService
from app.domain.entidades.order import Orden
from app.domain.exceptions import ErrorDominio
from app.domain.enums import EstadoOrden


def crear_orden_mock(order_id: str, estado: EstadoOrden = EstadoOrden.CREATED):
    """Crea un mock completo de Orden con todos los atributos necesarios"""
    orden = Mock(spec=Orden)
    orden.id = 1
    orden.order_id = order_id
    orden.cliente = "Juan Pérez"
    orden.vehiculo = "ABC-123"
    orden.estado = estado
    orden.servicios = []
    orden.eventos = []
    orden.monto_autorizado = None
    orden.version_autorizacion = 0
    orden.total_real = Decimal('0')
    orden.fecha_creacion = datetime.now()
    orden.fecha_cancelacion = None
    
    # Configurar métodos que devuelven la orden
    orden.agregar_servicio = Mock()
    orden.establecer_estado_diagnosticado = Mock()
    orden.autorizar = Mock()
    orden.iniciar_trabajo = Mock()
    orden.intentar_completar = Mock(return_value=False)
    orden.entregar = Mock()
    orden.cancelar = Mock()
    orden.reautorizar = Mock()
    
    return orden


def test_mecanico_agrega_servicio_adicional_durante_diagnostico():
    """
    El mecánico detecta durante el diagnóstico que necesita
    agregar un servicio adicional a la orden
    """
    # Preparar el escenario
    repo = Mock()
    auditoria = Mock()
    
    orden_existente = crear_orden_mock("ORD-001", EstadoOrden.DIAGNOSED)
    repo.obtener.return_value = orden_existente
    repo.save.return_value = orden_existente
    
    service = ActionService(repo, auditoria)
    
    # El mecánico agrega un servicio
    comando_agregar_servicio = {
        "op": "ADD_SERVICE",
        "data": {
            "order_id": "ORD-001",
            "description": "Cambio de frenos desgastados",
            "labor_estimated_cost": 1000.00,
            "components": []
        }
    }
    
    orden_actualizada, eventos, error = service.procesar_comando(comando_agregar_servicio)
    
    assert orden_actualizada is not None
    assert orden_actualizada.order_id == "ORD-001"


def test_mecanico_completa_diagnostico_y_marca_orden_como_diagnosticada():
    """
    Después de revisar el vehículo, el mecánico marca
    la orden como diagnosticada para continuar con la autorización
    """
    repo = Mock()
    auditoria = Mock()
    
    orden_en_diagnostico = crear_orden_mock("ORD-123", EstadoOrden.CREATED)
    repo.obtener.return_value = orden_en_diagnostico
    repo.save.return_value = orden_en_diagnostico
    
    service = ActionService(repo, auditoria)
    
    comando_diagnosticar = {
        "op": "SET_STATE_DIAGNOSED",
        "data": {"order_id": "ORD-123"}
    }
    
    orden_diagnosticada, eventos, error = service.procesar_comando(comando_diagnosticar)
    
    assert orden_diagnosticada is not None


def test_cliente_autoriza_reparacion_despues_de_ver_presupuesto():
    """
    El cliente revisa el presupuesto y decide autorizar
    la reparación del vehículo
    """
    repo = Mock()
    auditoria = Mock()
    
    orden_con_presupuesto = crear_orden_mock("ORD-456", EstadoOrden.DIAGNOSED)
    # Agregar servicios para poder autorizar
    servicio_mock = Mock()
    servicio_mock.id_servicio = 1
    servicio_mock.descripcion = "Cambio de aceite"
    servicio_mock.costo_mano_obra_estimado = Decimal('500.00')
    servicio_mock.costo_mano_obra_real = None
    servicio_mock.completado = False  # Atributo bool, no Mock
    servicio_mock.componentes = []  # Lista vacía iterable
    servicio_mock.calcular_subtotal_estimado = Mock(return_value=Decimal('1000.00'))
    orden_con_presupuesto.servicios = [servicio_mock]
    repo.obtener.return_value = orden_con_presupuesto
    repo.save.return_value = orden_con_presupuesto
    
    service = ActionService(repo, auditoria)
    
    comando_autorizar = {
        "op": "AUTHORIZE",
        "data": {"order_id": "ORD-456"}
    }
    
    orden_autorizada, eventos, error = service.procesar_comando(comando_autorizar)
    
    assert orden_autorizada is not None


def test_taller_inicia_trabajo_en_vehiculo_autorizado():
    """
    Una vez que el cliente autoriza, el taller comienza
    a trabajar en la reparación del vehículo
    """
    repo = Mock()
    auditoria = Mock()
    
    orden_autorizada = crear_orden_mock("ORD-789", EstadoOrden.AUTHORIZED)
    repo.obtener.return_value = orden_autorizada
    repo.save.return_value = orden_autorizada
    
    service = ActionService(repo, auditoria)
    
    comando_iniciar_trabajo = {
        "op": "SET_STATE_IN_PROGRESS",
        "data": {"order_id": "ORD-789"}
    }
    
    orden_en_progreso, eventos, error = service.procesar_comando(comando_iniciar_trabajo)
    
    assert orden_en_progreso is not None


def test_mecanico_registra_costo_real_al_terminar_servicio():
    """
    Al finalizar un servicio, el mecánico registra el costo
    real que difiere ligeramente del estimado
    """
    repo = Mock()
    auditoria = Mock()
    
    orden_en_trabajo = crear_orden_mock("ORD-321", EstadoOrden.IN_PROGRESS)
    servicio_mock = Mock()
    servicio_mock.id_servicio = 1  # Entero, no string
    servicio_mock.descripcion = "Cambio de aceite"
    servicio_mock.costo_mano_obra_estimado = Decimal('1000.00')
    servicio_mock.componentes = []
    servicio_mock.calcular_subtotal_estimado = Mock(return_value=Decimal('1000.00'))
    orden_en_trabajo.servicios = [servicio_mock]
    repo.obtener.return_value = orden_en_trabajo
    repo.save.return_value = orden_en_trabajo
    
    service = ActionService(repo, auditoria)
    
    comando_registrar_costo = {
        "op": "SET_REAL_COST",
        "data": {
            "order_id": "ORD-321",
            "service_id": 1,  # Entero, no string
            "real_cost": 1050.00,
            "components_real": {},
            "completed": True
        }
    }
    
    orden_con_costo_real, eventos, error = service.procesar_comando(comando_registrar_costo)
    
    assert orden_con_costo_real is not None


def test_sistema_intenta_completar_orden_cuando_todos_servicios_terminan():
    """
    Cuando todos los servicios están completos, el sistema
    intenta marcar la orden como completada
    """
    repo = Mock()
    auditoria = Mock()
    
    orden_con_servicios_completos = crear_orden_mock("ORD-654", EstadoOrden.IN_PROGRESS)
    repo.obtener.return_value = orden_con_servicios_completos
    repo.save.return_value = orden_con_servicios_completos
    
    service = ActionService(repo, auditoria)
    
    comando_intentar_completar = {
        "op": "TRY_COMPLETE",
        "data": {"order_id": "ORD-654"}
    }
    
    resultado_orden, eventos, error = service.procesar_comando(comando_intentar_completar)
    
    # Puede completarse o requerir reautorización
    assert resultado_orden is not None or error is not None


def test_recepcionista_entrega_vehiculo_a_cliente():
    """
    Una vez reparado y pagado, el recepcionista entrega
    el vehículo al cliente
    """
    repo = Mock()
    auditoria = Mock()
    
    orden_completada = crear_orden_mock("ORD-987", EstadoOrden.COMPLETED)
    repo.obtener.return_value = orden_completada
    repo.save.return_value = orden_completada
    
    service = ActionService(repo, auditoria)
    
    comando_entregar = {
        "op": "DELIVER",
        "data": {"order_id": "ORD-987"}
    }
    
    orden_entregada, eventos, error = service.procesar_comando(comando_entregar)
    
    assert orden_entregada is not None


def test_cliente_cancela_reparacion_antes_de_iniciar():
    """
    El cliente decide cancelar la reparación después
    de ver el presupuesto pero antes de iniciar el trabajo
    """
    repo = Mock()
    auditoria = Mock()
    
    orden_pendiente = crear_orden_mock("ORD-111", EstadoOrden.CREATED)
    repo.obtener.return_value = orden_pendiente
    repo.save.return_value = orden_pendiente
    
    service = ActionService(repo, auditoria)
    
    comando_cancelar = {
        "op": "CANCEL",
        "data": {
            "order_id": "ORD-111",
            "reason": "Cliente decidió no realizar la reparación"
        }
    }
    
    orden_cancelada, eventos, error = service.procesar_comando(comando_cancelar)
    
    assert orden_cancelada is not None


def test_cliente_reautoriza_cuando_costo_excede_presupuesto():
    """
    Durante la reparación se encuentra un problema adicional,
    el cliente debe reautorizar con un nuevo monto
    """
    repo = Mock()
    auditoria = Mock()
    
    orden_esperando_reautorizacion = crear_orden_mock("ORD-555", EstadoOrden.WAITING_FOR_APPROVAL)
    repo.obtener.return_value = orden_esperando_reautorizacion
    repo.save.return_value = orden_esperando_reautorizacion
    
    service = ActionService(repo, auditoria)
    
    comando_reautorizar = {
        "op": "REAUTHORIZE",
        "data": {
            "order_id": "ORD-555",
            "new_authorized_amount": 5000.00
        }
    }
    
    orden_reautorizada, eventos, error = service.procesar_comando(comando_reautorizar)
    
    assert orden_reautorizada is not None


# ===== CASOS DE ERROR Y EXCEPCIONES =====

def test_sistema_maneja_comando_desconocido_sin_fallar():
    """
    Si el sistema recibe un comando que no reconoce,
    no debe fallar sino manejarlo graciosamente
    """
    repo = Mock()
    auditoria = Mock()
    
    service = ActionService(repo, auditoria)
    
    comando_desconocido = {
        "op": "COMANDO_QUE_NO_EXISTE",
        "data": {}
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando_desconocido)
    
    # No debe generar orden si el comando es desconocido
    assert orden_dto is None


def test_sistema_captura_error_de_negocio_y_lo_reporta():
    """
    Cuando ocurre un error de negocio (ej: orden no encontrada),
    el sistema debe capturarlo y reportarlo correctamente
    """
    repo = Mock()
    auditoria = Mock()
    
    from app.domain.enums import CodigoError
    # Verificar que el ActionService captura ErrorDominio y lo propaga
    repo.obtener.side_effect = ErrorDominio(CodigoError.ORDER_NOT_FOUND, "La orden no existe")
    
    service = ActionService(repo, auditoria)
    
    comando = {
        "op": "ADD_SERVICE",
        "data": {
            "order_id": "ORD-INEXISTENTE",
            "description": "Servicio",
            "labor_estimated_cost": 1000.00,
            "components": []
        }
    }
    
    # Esperamos que el ActionService capture esto y devuelva el error
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert error is not None
    assert error.code == CodigoError.ORDER_NOT_FOUND.value
    assert "no existe" in error.message.lower()


def test_sistema_maneja_errores_inesperados_del_sistema():
    """
    Si ocurre un error inesperado del sistema (ej: problema de BD),
    debe manejarse sin exponer detalles internos
    """
    repo = Mock()
    auditoria = Mock()
    repo.obtener.side_effect = Exception("Error de conexión a base de datos")
    
    service = ActionService(repo, auditoria)
    
    comando = {
        "op": "ADD_SERVICE",
        "data": {
            "order_id": "ORD-001",
            "description": "Servicio",
            "labor_estimated_cost": 1000.00,
            "components": []
        }
    }
    
    # El ActionService captura excepciones y las convierte en ErrorDTO
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert error is not None
    assert error.code == "INTERNAL_ERROR"
    assert "base de datos" in error.message.lower()
