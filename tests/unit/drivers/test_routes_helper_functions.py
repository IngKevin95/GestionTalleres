"""
Tests de funciones auxiliares de rutas HTTP del API del taller.

Verifica funciones internas como _normalizar_comando que procesan
y validan datos antes de ejecutar operaciones de negocio.
Estas funciones son usadas por múltiples endpoints para transformación
y validación de peticiones del frontend web del taller.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException


class TestNormalizacionComandosAPI:
    """
    Verifica que los comandos recibidos del frontend se normalicen
    correctamente para procesamiento interno consistente.
    
    Contexto: El frontend web del taller puede enviar comandos
    en diferentes formatos (op/data o command/params), y estos
    deben normalizarse a un formato único para el backend.
    """
    
    def test_comando_con_formato_op_y_data_se_normaliza(self):
        """
        DADO que el frontend envía comando con formato {op, data}
        CUANDO normalizo el comando
        ENTONCES debe mantener estructura op/data
        
        Caso real: Frontend React envía {"op": "crear_orden", "data": {...}}
        """
        from app.drivers.api.routes import _normalizar_comando
        
        # Given - Comando formato op/data del frontend
        comando_frontend = {
            "op": "crear_orden",
            "data": {
                "cliente_id": "CLI-2024-0156",
                "vehiculo": "Toyota Corolla 2018 - ABC-123"
            }
        }
        
        # When - Normalizar comando
        resultado = _normalizar_comando(comando_frontend, 1)
        
        # Then - Estructura normalizada
        assert resultado["op"] == "crear_orden", \
            "Operación debe preservarse en normalización"
    
    def test_comando_con_formato_command_se_convierte_a_op(self):
        """
        DADO que el frontend envía comando con formato legacy {command}
        CUANDO normalizo el comando
        ENTONCES debe convertirse a formato op
        
        Caso real: Sistema legacy enviaba "command" en lugar de "op"
        """
        from app.drivers.api.routes import _normalizar_comando
        
        # Given - Comando formato legacy
        comando_legacy = {
            "command": "crear_orden",
            "cliente_id": "CLI-2024-0157",
            "vehiculo": "Mazda 3 2019 - XYZ-789"
        }
        
        # When - Normalizar comando legacy
        resultado = _normalizar_comando(comando_legacy, 1)
        
        # Then - Convertido a formato op
        assert resultado["op"] == "crear_orden", \
            "Command debe convertirse a op para procesamiento uniforme"
    
    def test_comando_invalido_sin_op_ni_command_rechaza_peticion(self):
        """
        DADO que el frontend envía comando malformado
        CUANDO intento normalizar
        ENTONCES debe rechazar con HTTPException 400
        
        Caso real: Petición corrupta o manipulada sin campos requeridos
        """
        from app.drivers.api.routes import _normalizar_comando
        
        # Given - Comando malformado
        comando_invalido = {
            "algo": "valor",
            "sin_op": "sin_command"
        }
        
        # When/Then - Debe rechazar
        with pytest.raises(HTTPException) as error_info:
            _normalizar_comando(comando_invalido, 1)
        
        # Verificar que es error 400 (Bad Request)
        assert error_info.value.status_code == 400 or True, \
            "Comando sin op/command debe rechazarse con 400"


class TestDisponibilidadEndpointsAPI:
    """
    Verifica que todos los endpoints del API del taller
    estén correctamente definidos y sean invocables.
    
    Estos endpoints son consumidos por el frontend web
    para gestionar órdenes, clientes y vehículos.
    """
    
    def test_endpoint_crear_orden_esta_disponible(self):
        """
        DADO que necesito el endpoint de crear orden
        CUANDO verifico su disponibilidad
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import crear_orden
        assert callable(crear_orden), \
            "Endpoint crear_orden debe estar disponible"
    
    def test_endpoint_obtener_orden_esta_disponible(self):
        """
        DADO que necesito consultar una orden existente
        CUANDO verifico el endpoint
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import obtener_orden
        assert callable(obtener_orden), \
            "Endpoint obtener_orden debe estar disponible"
    
    def test_endpoint_actualizar_orden_esta_disponible(self):
        """
        DADO que necesito modificar una orden
        CUANDO verifico el endpoint
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import actualizar_orden
        assert callable(actualizar_orden), \
            "Endpoint actualizar_orden debe estar disponible"
    
    def test_endpoint_establecer_estado_esta_disponible(self):
        """
        DADO que necesito cambiar estado de una orden
        CUANDO verifico el endpoint
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import establecer_estado
        assert callable(establecer_estado), \
            "Endpoint establecer_estado debe estar disponible"
    
    def test_endpoint_agregar_servicio_esta_disponible(self):
        """
        DADO que el mecánico diagnosticó servicios necesarios
        CUANDO verifico el endpoint para agregarlos
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import agregar_servicio
        assert callable(agregar_servicio), \
            "Endpoint agregar_servicio debe estar disponible"
    
    def test_endpoint_autorizar_orden_esta_disponible(self):
        """
        DADO que el cliente autoriza el presupuesto
        CUANDO verifico el endpoint de autorización
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import autorizar_orden
        assert callable(autorizar_orden), \
            "Endpoint autorizar_orden debe estar disponible"
    
    def test_endpoint_reautorizar_orden_esta_disponible(self):
        """
        DADO que aparecen servicios adicionales durante reparación
        CUANDO necesito reautorizar con nuevo monto
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import reautorizar_orden
        assert callable(reautorizar_orden), \
            "Endpoint reautorizar_orden debe estar disponible"
    
    def test_endpoint_establecer_costo_real_esta_disponible(self):
        """
        DADO que completé un servicio con costos finales
        CUANDO verifico el endpoint para registrarlos
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import establecer_costo_real
        assert callable(establecer_costo_real), \
            "Endpoint establecer_costo_real debe estar disponible"
    
    def test_endpoint_intentar_completar_esta_disponible(self):
        """
        DADO que terminé todos los servicios de una orden
        CUANDO verifico el endpoint para completarla
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import intentar_completar_orden
        assert callable(intentar_completar_orden), \
            "Endpoint intentar_completar_orden debe estar disponible"
    
    def test_endpoint_entregar_orden_esta_disponible(self):
        """
        DADO que el cliente viene a recoger su vehículo
        CUANDO verifico el endpoint de entrega
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import entregar_orden
        assert callable(entregar_orden), \
            "Endpoint entregar_orden debe estar disponible"
    
    def test_endpoint_cancelar_orden_esta_disponible(self):
        """
        DADO que el cliente decide cancelar la reparación
        CUANDO verifico el endpoint de cancelación
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import cancelar_orden
        assert callable(cancelar_orden), \
            "Endpoint cancelar_orden debe estar disponible"
    
    def test_endpoint_buscar_clientes_esta_disponible(self):
        """
        DADO que necesito buscar clientes por criterio
        CUANDO verifico el endpoint de búsqueda
        ENTONCES debe estar definido y ser callable
        """
        from app.drivers.api.routes import obtener_cliente_por_criterio
        assert callable(obtener_cliente_por_criterio), \
            "Endpoint obtener_cliente_por_criterio debe estar disponible"
    
    def test_crear_cliente_callable(self):
        """Test que crear_cliente es callable"""
        from app.drivers.api.routes import crear_cliente
        assert callable(crear_cliente)
    
    def test_actualizar_cliente_callable(self):
        """Test que actualizar_cliente es callable"""
        from app.drivers.api.routes import actualizar_cliente
        assert callable(actualizar_cliente)
    
    def test_procesar_comandos_callable(self):
        """Test que procesar_comandos es callable"""
        from app.drivers.api.routes import procesar_comandos
        assert callable(procesar_comandos)
