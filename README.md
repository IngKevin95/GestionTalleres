# GestionTalleres

Sistema para gestionar el ciclo de vida completo de órdenes de reparación en talleres automotrices. Permite crear órdenes, añadir servicios y componentes, controlar estados a lo largo del proceso, registrar costos estimados y reales, manejar autorizaciones con control de límites, y mantener trazabilidad completa mediante eventos de auditoría.

## Arquitectura

El sistema está implementado siguiendo **Arquitectura Hexagonal (Ports & Adapters)**, separando claramente las responsabilidades en capas:

- **Dominio** (`domain/`): Entidades y reglas de negocio puras, sin dependencias de frameworks. Aquí está el corazón del sistema: `Orden`, `Servicio`, `Componente`, validaciones de estado, cálculos monetarios, etc.
- **Aplicación** (`application/`): Casos de uso que orquestan el dominio. Cada acción (crear orden, autorizar, completar, etc.) está en su propio módulo.
- **Infraestructura** (`infrastructure/`): Implementaciones técnicas - repositorios SQL con SQLAlchemy, modelos de persistencia, configuración de BD y logging.
- **Drivers** (`drivers/api/`): Punto de entrada REST con FastAPI, endpoints, middlewares, dependency injection.

La idea es que el dominio no sepa nada de FastAPI ni PostgreSQL. Si mañana quieres cambiar la BD o usar gRPC en lugar de REST, solo tocas infraestructura y drivers, el dominio sigue igual.

### Separación de Responsabilidades

- **Entidades de Dominio** (`domain/entidades/`): Clases de negocio puras como `Orden`, `Servicio`, `Componente`. Toda la lógica de validación y reglas de negocio vive aquí.
- **Modelos de Persistencia** (`infrastructure/models/`): Modelos SQLAlchemy que mapean las entidades a tablas de PostgreSQL. Son solo estructura de datos.
- **Repositorios** (`infrastructure/repositories/`): Implementan las interfaces definidas en `application/ports.py`. Aquí está el código que habla con SQLAlchemy para guardar/cargar entidades.

## Requisitos

Para desarrollo local necesitas:
- Python 3.11 o superior
- PostgreSQL (cualquier versión reciente funciona, pero se prueba con 15)

Si prefieres usar Docker (recomendado para evitar problemas de configuración):
- Docker y Docker Compose

## Instalación

Primero clona el repo y entra a la carpeta:

```bash
cd GestionTalleres
```

Luego crea un entorno virtual (si no tienes uno ya):

```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Las principales dependencias son FastAPI para la API, SQLAlchemy para ORM, psycopg2 para PostgreSQL, y pytest para los tests.

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

Los tests están organizados por capas en `tests/unit/` (domain, application, infrastructure, drivers) y hay tests de integración en `tests/integration/`.

Para ejecutar todos los tests:

```bash
pytest
```

Si quieres ver la cobertura:

```bash
pytest --cov=app --cov-report=html
```

Esto genera un reporte HTML en `htmlcov/index.html` que puedes abrir en el navegador. La cobertura actual ronda el 74% aproximadamente, con algunas áreas que aún podrían mejorar (principalmente los endpoints y algunas rutas edge case).

Para ejecutar solo tests de una capa:

```bash
pytest tests/unit/domain/
pytest tests/unit/application/
pytest tests/integration/
```

Los tests de integración usan una BD de test real (puedes configurarla en variables de entorno o usar SQLite en memoria si prefieres).

## Verificación y Pruebas

Una vez que tengas todo corriendo, puedes verificar que funciona:

1. **Health Check**: Verifica que la API y la BD estén bien
   ```bash
   curl http://localhost:8000/health
   ```
   Debería retornar algo como `{"status": "ok", "api": "ok", "database": "ok"}`

2. **Crear tablas**: Si es la primera vez, necesitas inicializar la BD:
   ```bash
   # Con Docker:
   docker-compose exec api python init_db.py
   
   # Localmente:
   python init_db.py
   ```
   Esto crea todas las tablas necesarias. Si ya existen, no hace nada.

3. **Documentación de la API**: Una vez corriendo, abre `http://localhost:8000/docs` en el navegador. Ahí está la documentación interactiva de Swagger donde puedes probar los endpoints directamente.

4. **Tests**: Para correr los tests (asegúrate de tener una BD de test configurada):
   ```bash
   pytest
   ```

Si quieres más detalles sobre cómo probar el sistema o solucionar problemas comunes, hay documentación más completa en los archivos `TESTING.md` y `GUIA_TESTS.md` en la raíz del proyecto.

## Estructura del Proyecto

```
app/
├── domain/                    # Capa de dominio (lógica de negocio pura)
│   ├── entidades/             # Entidades: order.py, service.py, component.py, cliente.py, vehiculo.py, event.py
│   ├── enums/                 # Enums: order_status.py, error_code.py
│   ├── exceptions.py          # ErrorDominio
│   ├── dinero.py              # Utilidades para Decimal y redondeo
│   └── zona_horaria.py        # Manejo de timezone
│
├── application/               # Capa de aplicación (orquestación)
│   ├── acciones/              # Casos de uso, cada uno en su archivo:
│   │   ├── orden.py           # CrearOrden, CancelarOrden, EntregarOrden
│   │   ├── servicios.py       # AgregarServicio, EstablecerCostoReal
│   │   ├── estados.py         # EstablecerEstadoDiagnosticado, EstablecerEstadoEnProceso
│   │   └── autorizacion.py    # Autorizar, Reautorizar, IntentarCompletar
│   ├── action_service.py      # Servicio orquestador que procesa comandos
│   ├── dtos.py                # Data Transfer Objects (entrada/salida)
│   ├── mappers.py             # Conversores entre JSON, DTOs y entidades
│   └── ports.py               # Interfaces (RepositorioOrden, AlmacenEventos)
│
├── infrastructure/            # Capa de infraestructura (implementaciones técnicas)
│   ├── models/                # Modelos SQLAlchemy para persistencia
│   │   ├── orden_model.py
│   │   ├── cliente_model.py
│   │   ├── vehiculo_model.py
│   │   ├── servicio_model.py
│   │   ├── componente_model.py
│   │   └── evento_model.py
│   ├── repositories/          # Implementaciones de repositorios (hablan con SQLAlchemy)
│   │   ├── repositorio_orden.py
│   │   ├── repositorio_cliente.py
│   │   ├── repositorio_vehiculo.py
│   │   ├── repositorio_servicio.py
│   │   └── repositorio_evento.py
│   ├── db.py                  # Configuración de conexión a PostgreSQL
│   ├── logging_config.py      # Configuración del sistema de logging
│   └── logger.py              # Implementación de AlmacenEventos usando logging
│
└── drivers/                   # Capa de drivers (puntos de entrada)
    └── api/                   # API REST con FastAPI
        ├── main.py            # Aplicación FastAPI, configuración, lifespan
        ├── routes.py          # Todos los endpoints
        ├── dependencies.py    # Dependency injection (repositorios, servicios)
        ├── schemas.py         # Modelos Pydantic para requests/responses
        └── middleware.py      # Middleware de logging de requests

tests/
├── unit/                      # Tests unitarios organizados por capa
│   ├── domain/                # Tests de entidades, enums, utilidades
│   ├── application/           # Tests de acciones, DTOs, mappers
│   ├── infrastructure/        # Tests de repositorios, modelos
│   └── drivers/               # Tests de API, schemas, middleware
└── integration/               # Tests end-to-end con TestClient
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

El endpoint principal es `POST /commands` que procesa un batch de comandos en un solo request. Es útil para ejecutar secuencias de operaciones de una vez.

- `POST /commands` - Procesa batch de comandos (el más usado)
- `GET /orders/{order_id}` - Obtiene una orden completa con todos sus servicios y eventos
- `POST /orders` - Crea una nueva orden (endpoint individual)
- `POST /orders/{order_id}/services` - Añade un servicio a una orden
- `POST /orders/{order_id}/authorize` - Autoriza una orden (calcula IVA automáticamente)
- `POST /orders/{order_id}/set-real-cost` - Establece costos reales de servicios
- `POST /orders/{order_id}/try-complete` - Intenta completar la orden (valida límite 110%)
- `POST /orders/{order_id}/reauthorize` - Reautoriza cuando se excede el límite
- `POST /orders/{order_id}/deliver` - Marca la orden como entregada
- `POST /orders/{order_id}/cancel` - Cancela una orden
- `GET /health` - Health check de API y base de datos

También hay endpoints para gestionar clientes y vehículos si los necesitas.

### Formato de Comandos

El endpoint `/commands` acepta un array de comandos. Cada comando tiene una operación (`op`) y datos (`data`). Ejemplo de flujo completo:

```json
{
  "commands": [
    {
      "op": "CREATE_ORDER",
      "data": {
        "customer": "Juan Pérez",
        "vehicle": "Toyota Corolla 2020"
      },
      "ts": "2024-01-15T10:00:00-05:00"
    },
    {
      "op": "ADD_SERVICE",
      "data": {
        "order_id": "ORD-ABC12345",
        "description": "Cambio de aceite",
        "labor_cost": 50000,
        "components": [
          {
            "description": "Aceite 5W-30",
            "estimated_cost": 80000
          }
        ]
      }
    },
    {
      "op": "AUTHORIZE",
      "data": {
        "order_id": "ORD-ABC12345"
      }
    }
  ]
}
```

El sistema procesa los comandos secuencialmente y retorna un JSON con las órdenes modificadas, los eventos generados, y cualquier error que haya ocurrido. Si un comando falla, se registra el error pero se sigue procesando el siguiente.

## Reglas de Negocio

Las reglas principales que implementa el sistema:

- **IVA**: 16% sobre el subtotal estimado. El monto autorizado se calcula como `subtotal * 1.16`, redondeado con half-even.
- **Límite 110%**: Cuando intentas completar una orden, si el `total_real` excede el 110% del `monto_autorizado`, la orden pasa a estado `WAITING_FOR_APPROVAL` y necesitas reautorizar.
- **Redondeo**: Usa half-even (banker's rounding) a 2 decimales en todos los cálculos monetarios. No uses float para dinero, siempre Decimal.
- **Máquina de estados**: Las transiciones están bien definidas. No puedes saltarte estados (ej: no puedes autorizar sin haber diagnosticado primero).
- **Clientes y Vehículos**: Se crean automáticamente si no existen. Solo pasas el nombre del cliente y la descripción del vehículo como strings, el sistema se encarga del resto.
- **Versiones de autorización**: Cada reautorización incrementa la versión, así puedes rastrear cuántas veces se reautorizó una orden.

## Características Técnicas

Algunas cosas que están implementadas:

- **Dependency Injection**: Usa `Depends()` de FastAPI para inyectar repositorios y servicios. Esto hace que los tests sean más fáciles porque puedes mockear dependencias fácilmente.
- **Exception Handlers Globales**: Hay handlers centralizados que capturan `ErrorDominio` (errores de negocio) y otros errores, y los convierten a respuestas HTTP apropiadas.
- **Middleware de Logging**: Cada request se loguea automáticamente con métricas de tiempo de respuesta, status code, IP, etc. Los logs se guardan en `logs/` con rotación automática.
- **Lifespan Events**: FastAPI tiene eventos de inicio/cierre donde se configuran las conexiones a BD. Si hay un problema al iniciar, se loguea pero no crashea todo.
- **Validaciones**: Los path parameters se validan con regex (ej: `order_id` debe ser `ORD-XXXXXXXX` con formato específico). Si no cumple, FastAPI devuelve 422 antes de llegar a tu código.
- **CORS Configurable**: Puedes configurar qué orígenes permitir vía variable de entorno. Por defecto permite todos (`*`) pero puedes restringirlo.

## Notas de Implementación

El código interno está en español (clases, métodos, variables), pero la API acepta y retorna JSON con keys en inglés para mantener compatibilidad con contratos existentes. El mapeo entre ambos se hace en la capa de mappers.

Los campos `customer` y `vehicle` en el JSON se aceptan como strings simples. El sistema busca si ese cliente/vehículo ya existe en la BD y si no, lo crea automáticamente. Esto simplifica bastante el uso de la API.

Todos los cálculos monetarios usan `Decimal` desde el inicio. No hay conversiones a float en ninguna parte del código, lo que evita los problemas típicos de precisión flotante.

El sistema registra eventos de dominio en cada acción importante (autorizar, completar, cancelar, etc.). Estos eventos se guardan tanto en la entidad `Orden` como en el sistema de auditoría externo (que por defecto usa logging, pero podrías cambiar a BD o un servicio externo sin tocar el dominio).

## Empezar Rápido

Si quieres probar el sistema rápido:

1. **Con Docker** (más fácil):
   ```bash
   docker-compose up --build
   docker-compose exec api python init_db.py
   ```
   Luego abre `http://localhost:8000/docs` y prueba el endpoint `POST /commands` con el ejemplo de arriba.

2. **Localmente**:
   - Crea un `.env` con las variables de BD
   - Crea la BD en PostgreSQL
   - Ejecuta `python init_db.py`
   - Corre `uvicorn app.drivers.api.main:app --reload`

## Documentación Adicional

En la raíz del proyecto hay varios archivos con documentación más detallada:
- `DOCUMENTACION_COMPLETA.md` - Documentación exhaustiva del sistema
- `ARQUITECTURA.md` - Detalles de la arquitectura hexagonal
- `TESTING.md` y `GUIA_TESTS.md` - Guías de testing
- `APLICACION_PRINCIPIOS.md` - Cómo se aplicaron los principios SOLID y Clean Code
