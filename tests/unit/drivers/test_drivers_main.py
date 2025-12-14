from unittest.mock import Mock, patch, MagicMock
from fastapi import FastAPI
from app.drivers.api.main import app, lifespan


def test_app_creacion():
    assert isinstance(app, FastAPI)
    assert app.title == "GestionTalleres API"
    assert app.version == "1.0.0"


def test_lifespan_inicio():
    app_mock = Mock(spec=FastAPI)
    
    with patch('app.drivers.api.main.configurar_logging'):
        with patch('app.drivers.api.main.crear_engine_bd'):
            with patch('app.drivers.api.main.logger') as logger_mock:
                async def run_lifespan():
                    async with lifespan(app_mock):
                        pass
                
                import asyncio
                asyncio.run(run_lifespan())
                
                logger_mock.info.assert_called()


def test_lifespan_error_bd():
    app_mock = Mock(spec=FastAPI)
    
    with patch('app.drivers.api.main.configurar_logging'):
        with patch('app.drivers.api.main.crear_engine_bd', side_effect=Exception("Error BD")):
            with patch('app.drivers.api.main.logger') as logger_mock:
                async def run_lifespan():
                    async with lifespan(app_mock):
                        pass
                
                import asyncio
                asyncio.run(run_lifespan())
                
                logger_mock.error.assert_called()


def test_lifespan_cierre():
    app_mock = Mock(spec=FastAPI)
    
    with patch('app.drivers.api.main.configurar_logging'):
        with patch('app.drivers.api.main.crear_engine_bd'):
            with patch('app.drivers.api.main.logger') as logger_mock:
                async def run_lifespan():
                    async with lifespan(app_mock):
                        pass
                
                import asyncio
                asyncio.run(run_lifespan())
                
                assert logger_mock.info.call_count >= 2

