from sqlalchemy.ext.declarative import declarative_base
from ...domain.zona_horaria import ahora

Base = declarative_base()


def fecha_creacion_default():
    return ahora()

