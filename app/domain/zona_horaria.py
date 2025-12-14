import os
from zoneinfo import ZoneInfo
from datetime import datetime

def obtener_zona_horaria():
    tz = os.getenv("TIMEZONE", "America/Bogota")
    try:
        return ZoneInfo(tz)
    except Exception:
        return ZoneInfo("America/Bogota")

def ahora():
    return datetime.now(obtener_zona_horaria())

