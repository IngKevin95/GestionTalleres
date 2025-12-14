"""Tests para dependencias inyectables de la API."""
import pytest


class TestDependencies:
    """Tests para dependencias inyectables."""
    
    def test_obtener_action_service_callable(self):
        """Test que obtener_action_service es callable."""
        from app.drivers.api.dependencies import obtener_action_service
        
        assert callable(obtener_action_service)
    
    def test_obtener_sesion_callable(self):
        """Test que obtener_sesion es callable."""
        from app.drivers.api.dependencies import obtener_sesion
        
        assert callable(obtener_sesion)
    
    def test_obtener_repositorio_callable(self):
        """Test que obtener_repositorio es callable."""
        from app.drivers.api.dependencies import obtener_repositorio
        
        assert callable(obtener_repositorio)
    
    def test_obtener_repositorio_cliente_callable(self):
        """Test que obtener_repositorio_cliente es callable."""
        from app.drivers.api.dependencies import obtener_repositorio_cliente
        
        assert callable(obtener_repositorio_cliente)
    
    def test_obtener_repositorio_vehiculo_callable(self):
        """Test que obtener_repositorio_vehiculo es callable."""
        from app.drivers.api.dependencies import obtener_repositorio_vehiculo
        
        assert callable(obtener_repositorio_vehiculo)
