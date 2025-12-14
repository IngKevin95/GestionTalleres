"""Tests para aplicación principal FastAPI."""
import pytest


class TestMainApp:
    """Tests para app principal."""
    
    def test_app_instance_exists(self):
        """Test que app FastAPI existe."""
        from app.drivers.api.main import app
        from fastapi import FastAPI
        
        assert isinstance(app, FastAPI)
    
    def test_app_has_routes(self):
        """Test que app tiene rutas."""
        from app.drivers.api.main import app
        
        routes = list(app.routes)
        assert len(routes) > 0
    
    def test_app_router_exists(self):
        """Test que app tiene router."""
        from app.drivers.api.main import app
        
        assert app.router is not None
    
    def test_app_routes_existence(self):
        """Test existencia de rutas en app."""
        from app.drivers.api.main import app
        
        routes = [route.path for route in app.routes]
        assert len(routes) > 0
    
    def test_app_router_is_valid(self):
        """Test que app router es válido."""
        from app.drivers.api.main import app
        
        assert app.router is not None
        assert len(app.routes) >= 1
