from dotenv import load_dotenv
import sys

load_dotenv()

from app.infrastructure.db import crear_engine_bd, obtener_url_bd
from app.infrastructure.models import Base
from app.infrastructure.logging_config import configurar_logging, obtener_logger

configurar_logging()
logger = obtener_logger("init_db")

if __name__ == "__main__":
    try:
        url = obtener_url_bd()
        url_mostrar = url.split('@')[1] if '@' in url else 'URL oculta'
        logger.info(f"Conectando a base de datos PostgreSQL en {url_mostrar}")
        
        engine = crear_engine_bd(url)
        
        logger.info("Creando tablas en base de datos")
        Base.metadata.create_all(engine)
        
        logger.info("Tablas creadas exitosamente")
        
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        tablas_esperadas = ["ordenes", "clientes", "vehiculos", "servicios", "componentes", "eventos"]
        tablas_encontradas = [t for t in tablas_esperadas if t in tablas]
        
        logger.info(f"Tablas existentes: {', '.join(tablas) if tablas else 'Ninguna'}")
        logger.info(f"Tablas principales: {', '.join(tablas_encontradas)}")
        
        if len(tablas_encontradas) < len(tablas_esperadas):
            faltantes = [t for t in tablas_esperadas if t not in tablas]
            logger.warning(f"Faltan tablas: {', '.join(faltantes)}")
        
    except Exception as e:
        logger.error(f"Error al crear tablas: {str(e)}", exc_info=True)
        sys.exit(1)
