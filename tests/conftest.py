import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
try:
    from starlette.testclient import TestClient
except ImportError:
    from fastapi.testclient import TestClient

# Configurar variables de entorno para PostgreSQL en Docker
# Usa localhost:5438 ya que está ejecutándose en Docker con puerto expuesto
os.environ["DB_HOST"] = "localhost"
os.environ["POSTGRES_USER"] = "talleres_user"
os.environ["POSTGRES_PASSWORD"] = "talleres_pass"
os.environ["DB_INTERNAL_PORT"] = "5438"  # Puerto expuesto desde Docker
os.environ["POSTGRES_DB"] = "talleres"  # Base de datos existente en Docker

from app.infrastructure.models import Base
from app.infrastructure import db as db_module
from app.drivers.api.main import app


@pytest.fixture(scope="function")
def client():
    """Proporciona un cliente de prueba de FastAPI apuntando a PostgreSQL."""
    
    # Resetear el engine y la sesión global
    db_module._engine = None
    db_module.SessionLocal = None
    
    # Obtener URL de base de datos desde las variables de entorno
    from app.infrastructure.db import obtener_url_bd
    db_url = obtener_url_bd()
    
    # Crear engine con PostgreSQL
    test_engine = create_engine(db_url)
    
    # Crear todas las tablas
    Base.metadata.create_all(test_engine)
    
    # Crear la sesión para esta prueba
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    def get_test_db():
        db_session = TestingSessionLocal()
        try:
            yield db_session
        finally:
            db_session.close()
    
    # Reemplazar la dependencia de base de datos
    from app.drivers.api.dependencies import obtener_sesion_db
    app.dependency_overrides[obtener_sesion_db] = get_test_db
    
    # Crear el cliente de prueba
    from fastapi.testclient import TestClient
    test_client = TestClient(app)
    
    yield test_client
    
    # Limpiar después del test - eliminar todas las tablas
    try:
        Base.metadata.drop_all(test_engine)
    except Exception as e:
        print(f"Error limpiando tablas: {e}")
    
    test_engine.dispose()
    app.dependency_overrides.clear()
    
    # Resetear los globals
    db_module._engine = None
    db_module.SessionLocal = None


