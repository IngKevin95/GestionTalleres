import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base


_engine = None
SessionLocal = None


def obtener_url_bd() -> str:
    usuario = os.getenv("POSTGRES_USER", "talleres_user")
    contraseña = os.getenv("POSTGRES_PASSWORD", "talleres_pass")
    host = os.getenv("DB_HOST", "localhost")
    puerto = os.getenv("DB_INTERNAL_PORT", "5432")
    nombre_bd = os.getenv("POSTGRES_DB", "talleres")
    
    return f"postgresql://{usuario}:{contraseña}@{host}:{puerto}/{nombre_bd}"


def crear_engine_bd(url: str = None):
    global _engine
    if _engine is None:
        if url is None:
            url = obtener_url_bd()
        _engine = create_engine(url)
    return _engine


def obtener_sesion() -> Session:
    global SessionLocal
    if SessionLocal is None:
        engine = crear_engine_bd()
        SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
