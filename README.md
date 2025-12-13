# GestionTalleres

Sistema para gestionar el ciclo de vida de órdenes de reparación en una red de talleres automotrices. Permite crear órdenes, añadir servicios y componentes, controlar estados, registrar costos estimados y reales, manejar autorizaciones y mantener trazabilidad del proceso.

## Arquitectura

El sistema está implementado siguiendo **Arquitectura Hexagonal (Ports & Adapters)**, con separación clara entre:
- **Dominio**: Entidades y reglas de negocio puras (ubicadas en `domain/entidades/`)
- **Aplicación**: Casos de uso (acciones) que orquestan el dominio
- **Infraestructura**: Implementaciones concretas (repositorios SQL, modelos de persistencia)
- **Drivers**: Puntos de entrada (API FastAPI)

### Separación de Responsabilidades

- **Entidades de Dominio** (`domain/entidades/`): Entidades de negocio puras sin dependencias de frameworks
- **Modelos de Persistencia** (`infrastructure/models/`): Modelos SQLAlchemy para mapeo a base de datos
- **Repositorios** (`infrastructure/repositories/`): Implementaciones concretas de persistencia (solo SQL)

## Requisitos

### Desarrollo Local
- Python 3.11+
- PostgreSQL

### Docker
- Docker
- Docker Compose

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Configuración de Base de Datos

La aplicación usa PostgreSQL como única fuente de persistencia.

1. Crear archivo `.env` en la raíz del proyecto con la configuración de base de datos:
```bash
POSTGRES_USER=usuario
POSTGRES_PASSWORD=contraseña
POSTGRES_DB=talleres
DB_HOST=localhost
DB_INTERNAL_PORT=5432
```

2. Crear la base de datos en PostgreSQL:
```sql
CREATE DATABASE talleres;
```

3. Inicializar las tablas de la base de datos:
```bash
python init_db.py
```

   Esto creará las siguientes tablas:
   - `ordenes`
   - `clientes`
   - `vehiculos`
   - `servicios`
   - `componentes`
   - `eventos`

**Nota:** La `DATABASE_URL` se construye automáticamente usando las variables individuales. Para desarrollo local, usa `DB_HOST=localhost`. Para Docker, usa `DB_HOST=db`.

### Configuración Docker

El `docker-compose.yml` lee todas las configuraciones desde el archivo `.env`. 

**Variables de entorno disponibles en `.env`:**

#### Base de Datos PostgreSQL
- `POSTGRES_USER`: Usuario de PostgreSQL (default: `talleres_user`)
- `POSTGRES_PASSWORD`: Contraseña de PostgreSQL (default: `talleres_pass`)
- `POSTGRES_DB`: Nombre de la base de datos (default: `talleres`)
- `POSTGRES_VERSION`: Versión de PostgreSQL (default: `15`)
- `DB_HOST`: Host de la base de datos (default: `db` para Docker, usar `localhost` para conexiones locales)
- `DB_INTERNAL_PORT`: Puerto interno de PostgreSQL dentro del contenedor (default: `5432`)
- `DB_EXTERNAL_PORT`: Puerto expuesto de PostgreSQL al host (default: `5438`)

#### API
- `API_PORT`: Puerto de la API (default: `8000`)
- `CONTAINER_NAME_DB`: Nombre del contenedor de BD (default: `gestion_talleres_db`)
- `CONTAINER_NAME_API`: Nombre del contenedor de API (default: `gestion_talleres_api`)

#### Zona Horaria
- `TIMEZONE`: Zona horaria para todos los cálculos de fecha/hora (default: `America/Bogota`)
  - Formato: IANA timezone (ej: `America/Bogota`, `America/Mexico_City`, `UTC`, `Europe/Madrid`)
  - Se usa en todos los cálculos de datetime del sistema

#### Logging
- `LOG_LEVEL`: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL) - default: `INFO`
- `LOG_FORMAT`: Formato de logs (json, text) - default: `text`
- `LOG_DIR`: Directorio para archivos de log - default: `logs/`
- `LOG_ROTATION`: Tipo de rotación (time, size, none) - default: `time`
- `LOG_MAX_BYTES`: Tamaño máximo por archivo en bytes (si rotación por tamaño) - default: `10485760` (10MB)
- `LOG_BACKUP_COUNT`: Número de archivos de backup a mantener - default: `7`
- `LOG_TO_CONSOLE`: Habilitar logging a consola (true/false) - default: `false`

#### CORS
- `CORS_ORIGINS`: Orígenes permitidos separados por comas (default: `*` para permitir todos)

#### Healthcheck (opcional)
- `DB_HEALTHCHECK_INTERVAL`: Intervalo entre checks (default: `10s`)
- `DB_HEALTHCHECK_TIMEOUT`: Timeout del check (default: `5s`)
- `DB_HEALTHCHECK_RETRIES`: Número de reintentos (default: `5`)

**Nota:** La URL de conexión a la base de datos se construye automáticamente usando las variables individuales. Para cambiar cualquier configuración, edita el archivo `.env`.

## Ejecución

### Opción 1: Con Docker Compose (Recomendado)

1. Construir y levantar los servicios:
```bash
docker-compose up --build
```

2. Inicializar las tablas de la base de datos:
```bash
docker-compose exec api python init_db.py
```

3. Los servicios estarán disponibles en:
   - API: `http://localhost:8000`
   - PostgreSQL: `localhost:5438` (puerto externo)

Para detener los servicios:
```bash
docker-compose down
```

Para detener y eliminar los volúmenes (incluyendo datos de BD):
```bash
docker-compose down -v
```

### Opción 2: Servidor de desarrollo local

1. Asegúrate de tener PostgreSQL corriendo y configurado en `.env`
2. Inicializa las tablas:
```bash
python init_db.py
```

3. Ejecuta el servidor:
```bash
uvicorn app.drivers.api.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

### Documentación API

Una vez ejecutando el servidor:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Sistema de Logging

El sistema incluye un sistema de logging profesional y unificado con las siguientes características:

- **Rotación automática de archivos**: Por tiempo (diario) o por tamaño
- **Múltiples handlers**: 
  - `app.log`: Logs generales (INFO, WARNING)
  - `errors.log`: Solo errores (ERROR, CRITICAL)
  - `requests.log`: Requests HTTP (INFO)
- **Formato configurable**: JSON o texto legible
- **Logging estructurado**: Incluye contexto relevante (método, path, status_code, tiempo de respuesta, IP)
- **Eventos de dominio**: Los eventos de negocio se registran automáticamente con categoría especial

Los archivos de log se guardan en el directorio `logs/` (configurable mediante `LOG_DIR`).

## Tests

Ejecutar todos los tests:
```bash
pytest
```

Ejecutar tests con cobertura:
```bash
pytest --cov=app --cov-report=html
```

## Verificación y Pruebas

Para verificar que todo funciona correctamente:

1. **Health Check**: Verifica el estado de la API y la base de datos
   ```bash
   curl http://localhost:8000/health
   ```

2. **Crear tablas**: Si las tablas no existen, ejecuta:
   ```bash
   docker-compose exec api python init_db.py
   # O localmente:
   python init_db.py
   ```

3. **Documentación completa**: Ver `TESTING.md` para una guía detallada de pruebas y solución de problemas.

## Estructura del Proyecto

```
app/
├── domain/                    # Capa de dominio
│   ├── entidades/             # Entidades de negocio (Orden, Servicio, Componente, Cliente, Vehiculo, Evento)
│   ├── enums/                 # Enumeraciones del dominio
│   ├── exceptions.py           # Excepciones del dominio
│   └── ...
├── application/               # Capa de aplicación
│   ├── acciones/              # Casos de uso (CrearOrden, AgregarServicio, etc.)
│   ├── dtos.py                # Data Transfer Objects
│   ├── mappers.py             # Mappers dominio ↔ DTOs
│   ├── ports.py               # Interfaces/Ports (RepositorioOrden, AlmacenEventos)
│   └── action_service.py      # Servicio de acciones
├── infrastructure/            # Capa de infraestructura
│   ├── models/                # Modelos de persistencia SQLAlchemy
│   │   ├── orden_model.py
│   │   ├── cliente_model.py
│   │   ├── vehiculo_model.py
│   │   ├── servicio_model.py
│   │   ├── componente_model.py
│   │   └── evento_model.py
│   ├── repositories/          # Implementaciones de repositorios
│   │   ├── repositorio_orden.py
│   │   ├── repositorio_cliente.py
│   │   ├── repositorio_vehiculo.py
│   │   ├── repositorio_servicio.py
│   │   └── repositorio_evento.py
│   ├── db.py                  # Configuración de base de datos
│   ├── logging_config.py      # Configuración de logging
│   └── logger.py              # Logger para eventos de dominio
└── drivers/                   # Capa de drivers
    └── api/                   # API FastAPI
        ├── main.py            # Aplicación FastAPI principal
        ├── routes.py          # Endpoints de la API
        ├── dependencies.py    # Dependency injection
        ├── schemas.py         # Modelos Pydantic para API
        └── middleware.py      # Middleware de logging

tests/
├── unit/                      # Tests unitarios
└── integration/              # Tests de integración
```

## Modelo de Datos

### Tablas de Base de Datos

- **ordenes**: Órdenes de reparación
- **clientes**: Clientes (tabla separada)
- **vehiculos**: Vehículos (tabla separada, FK a clientes)
- **servicios**: Servicios de cada orden
- **componentes**: Componentes de cada servicio (tabla separada)
- **eventos**: Eventos de auditoría

### Relaciones

- `ordenes` → `clientes` (una orden tiene un cliente, ForeignKey)
- `ordenes` → `vehiculos` (una orden tiene un vehículo, ForeignKey)
- `vehiculos` → `clientes` (un vehículo pertenece a un cliente, ForeignKey)
- `servicios` → `componentes` (un servicio tiene muchos componentes, ForeignKey)
- `ordenes` → `servicios` (una orden tiene muchos servicios)
- `ordenes` → `eventos` (una orden tiene muchos eventos)

## Endpoints Principales

- `POST /commands` - Procesa batch de comandos (endpoint principal)
- `GET /orders/{order_id}` - Consulta una orden
- `POST /orders/{order_id}/set_state` - Establece estado de la orden
- `GET /health` - Health check de API y base de datos

### Formato de Comandos

El endpoint `/commands` acepta comandos en formato JSON. El sistema convierte automáticamente el formato `command` a `op` + `data` para compatibilidad interna.

Ejemplo:
```json
{
  "commands": [
    {
      "command": "CREATE_ORDER",
      "customer": "Juan Pérez",
      "vehicle": "Toyota Corolla 2020",
      "ts": "2024-01-15T10:00:00-05:00"
    }
  ]
}
```

## Reglas de Negocio

- **IVA**: 16% sobre subtotal estimado
- **Límite 110%**: Al completar, si el total real excede 110% del monto autorizado, requiere reautorización
- **Redondeo**: Half-even (banker's rounding) a 2 decimales
- **Estados**: Transiciones válidas según máquina de estados definida
- **Clientes y Vehículos**: Se crean automáticamente al recibir strings en el JSON, manteniendo compatibilidad con el formato de entrada

## Características Técnicas

- **Dependency Injection**: Uso de `Depends()` de FastAPI para inyección de dependencias
- **Exception Handlers Globales**: Manejo centralizado de excepciones (ErrorDominio, ValueError, SQLAlchemyError, etc.)
- **Middleware de Logging**: Registro automático de requests HTTP con métricas de tiempo
- **Lifespan Events**: Manejo adecuado de conexiones de base de datos al iniciar/cerrar la aplicación
- **Validaciones**: Validación de path parameters con regex (ej: `order_id` debe seguir formato `ORD-[0-9A-F]{8}`)
- **CORS Configurable**: Configuración de CORS mediante variables de entorno

## Compatibilidad

El sistema mantiene compatibilidad con el formato JSON de entrada existente. Los campos `customer` y `vehicle` se aceptan como strings y se resuelven automáticamente a entidades `Cliente` y `Vehiculo` en la base de datos.
