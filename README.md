# GestionTalleres

Sistema completo para gestionar el ciclo de vida de órdenes de reparación en talleres automotrices. Cubre desde la creación de órdenes hasta la entrega, pasando por diagnóstico, autorización, reparación y control de costos. Incluye gestión de clientes y vehículos, cálculo automático de IVA, validación de límites de autorización, y trazabilidad completa mediante eventos de auditoría.

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

### Endpoints de Órdenes

El endpoint principal es `POST /commands` que procesa un batch de comandos en un solo request. Es útil para ejecutar secuencias de operaciones de una vez.

- `GET /` - Información básica de la API (versión, mensaje de bienvenida)
- `GET /health` - Health check de API y base de datos (incluye estado de tablas)
- `POST /commands` - Procesa batch de comandos (el más usado para operaciones múltiples)
- `GET /orders/{order_id}` - Obtiene una orden completa con todos sus servicios, componentes y eventos
- `POST /orders` - Crea una nueva orden (endpoint individual, con find-or-create de cliente/vehículo)
- `PATCH /orders/{order_id}` - Actualiza datos básicos de una orden (cliente, vehículo)
- `POST /orders/{order_id}/set_state` - Cambia el estado de una orden (DIAGNOSED, IN_PROGRESS)
- `POST /orders/{order_id}/services` - Añade un servicio a una orden (con componentes opcionales)
- `POST /orders/{order_id}/authorize` - Autoriza una orden (calcula IVA automáticamente al 16%)
- `POST /orders/{order_id}/set_real_cost` - Establece costos reales de servicios y componentes
- `POST /orders/{order_id}/try_complete` - Intenta completar la orden (valida límite 110%, puede requerir reautorización)
- `POST /orders/{order_id}/reauthorize` - Reautoriza cuando se excede el límite (incrementa versión de autorización)
- `POST /orders/{order_id}/deliver` - Marca la orden como entregada (solo si está COMPLETED)
- `POST /orders/{order_id}/cancel` - Cancela una orden (requiere motivo, bloquea todas las operaciones)

### Endpoints de Clientes y Vehículos

El sistema incluye endpoints completos para gestionar clientes y vehículos con identificación flexible:

**Clientes:**
- `GET /customers` - Lista todos los clientes
- `GET /customers?{id_cliente|identificacion|nombre}` - Obtiene un cliente por ID, identificación o nombre
- `POST /customers` - Crea un cliente (si ya existe, retorna el existente)
- `PATCH /customers?{id_cliente|identificacion|nombre}` - Actualiza un cliente identificado flexiblemente

**Vehículos:**
- `GET /vehicles` - Lista todos los vehículos
- `GET /vehicles?{id_vehiculo|placa}` - Obtiene un vehículo por ID o placa
- `GET /customers/vehicles?{id_cliente|identificacion|nombre}` - Obtiene vehículos de un cliente
- `POST /vehicles` - Crea un vehículo (si ya existe, retorna el existente)
- `PATCH /vehicles?{id_vehiculo|placa}` - Actualiza vehículo usando query parameters
- `PATCH /vehicles/{vehicle_identifier}` - Actualiza vehículo usando path parameter (ID numérico o placa)

#### Identificación Flexible

Tanto clientes como vehículos pueden identificarse de múltiples formas:

**Clientes:**
- Por `id_cliente` (número)
- Por `identificacion` (string único)
- Por `nombre` (string único)

**Vehículos:**
- Por `id_vehiculo` (número)
- Por `placa` (string único)

Ejemplos:
```bash
# Obtener cliente por nombre
GET /customers?nombre=Juan Pérez

# Obtener vehículo por placa
GET /vehicles?placa=ABC-123

# Actualizar vehículo usando placa en el path
PATCH /vehicles/ABC-123
{
  "customer": "Kevin"
}
```

#### Find-or-Create (Búsqueda o Creación)

Al crear órdenes, clientes o vehículos, el sistema implementa lógica **find-or-create**:

- Si el cliente/vehículo ya existe (según los criterios de identificación), se usa el existente
- Si no existe, se crea uno nuevo
- Esto evita duplicados y simplifica el uso de la API

**Ejemplo de creación de orden:**
```json
{
  "customer": {
    "nombre": "Juan Pérez"
  },
  "vehicle": {
    "placa": "ABC-123"
  },
  "order_id": "ORD-001"
}
```

Si el cliente "Juan Pérez" ya existe, se relaciona la orden con ese cliente. Lo mismo aplica para el vehículo con placa "ABC-123".

#### Transferencia de Propiedad de Vehículos

Los vehículos pueden transferirse entre clientes mediante actualización:

```bash
# Transferir vehículo ABC-123 al cliente "Kevin"
PATCH /vehicles/ABC-123
{
  "customer": "Kevin"
}
```

El sistema valida que el cliente destino exista y actualiza la relación. Si intentas crear una orden con un vehículo que ya está registrado a otro cliente, recibirás un error específico indicando que debes actualizar el vehículo primero.

#### Restricciones de Unicidad

Los siguientes campos son únicos en la base de datos:
- `clientes.identificacion` - Identificación del cliente
- `clientes.nombre` - Nombre del cliente
- `vehiculos.placa` - Placa del vehículo

Si intentas crear un cliente o vehículo con un valor duplicado, el sistema retornará un error de validación.

### Formato de Comandos

El endpoint `/commands` acepta un array de comandos (máximo 100 por request). Cada comando tiene una operación (`op`) y datos (`data`). Los comandos se procesan secuencialmente y si uno falla, se registra el error pero se continúa con el siguiente.

**Comandos disponibles:**

- `CREATE_ORDER` - Crea una nueva orden en estado CREATED
- `ADD_SERVICE` - Agrega un servicio a una orden (solo en CREATED o DIAGNOSED)
- `SET_STATE_DIAGNOSED` - Cambia el estado a DIAGNOSED
- `SET_STATE_IN_PROGRESS` - Cambia el estado a IN_PROGRESS (requiere autorización previa)
- `AUTHORIZE` - Calcula monto autorizado con IVA y cambia a AUTHORIZED
- `SET_REAL_COST` - Establece costos reales de servicios/componentes
- `TRY_COMPLETE` - Valida límite 110% y completa o requiere reautorización
- `REAUTHORIZE` - Nueva autorización desde WAITING_FOR_APPROVAL
- `DELIVER` - Cambia estado a DELIVERED (requiere COMPLETED)
- `CANCEL` - Cancela la orden con motivo

Ejemplo de flujo completo:

```json
{
  "commands": [
    {
      "op": "CREATE_ORDER",
      "data": {
        "order_id": "ORD-001",
        "customer": "Juan Pérez",
        "vehicle": "ABC-123"
      },
      "ts": "2024-01-15T10:00:00-05:00"
    },
    {
      "op": "ADD_SERVICE",
      "data": {
        "order_id": "ORD-001",
        "description": "Cambio de aceite",
        "labor_estimated_cost": 50000,
        "components": [
          {
            "description": "Aceite 5W-30",
            "estimated_cost": 80000
          }
        ]
      }
    },
    {
      "op": "SET_STATE_DIAGNOSED",
      "data": {
        "order_id": "ORD-001"
      }
    },
    {
      "op": "AUTHORIZE",
      "data": {
        "order_id": "ORD-001"
      }
    },
    {
      "op": "SET_STATE_IN_PROGRESS",
      "data": {
        "order_id": "ORD-001"
      }
    },
    {
      "op": "SET_REAL_COST",
      "data": {
        "order_id": "ORD-001",
        "service_index": 1,
        "real_cost": 135000,
        "components_real": {
          "1": 85000
        },
        "completed": true
      }
    },
    {
      "op": "TRY_COMPLETE",
      "data": {
        "order_id": "ORD-001"
      }
    },
    {
      "op": "DELIVER",
      "data": {
        "order_id": "ORD-001"
      }
    }
  ]
}
```

El sistema retorna un JSON con:
- `orders`: Array de órdenes modificadas (con todos sus datos actualizados)
- `events`: Array de eventos generados durante el procesamiento
- `errors`: Array de errores si algún comando falló (el procesamiento continúa)

## Reglas de Negocio

### Máquina de Estados

Las órdenes siguen un flujo de estados estricto:

```
CREATED → DIAGNOSED → AUTHORIZED → IN_PROGRESS → COMPLETED → DELIVERED
                                    ↓
                            WAITING_FOR_APPROVAL → AUTHORIZED → ...
    
Cualquier estado → CANCELLED (bloquea todas las operaciones)
```

**Estados disponibles:**
- `CREATED`: Orden recién creada, puede agregar servicios
- `DIAGNOSED`: Diagnóstico completado, lista para autorizar
- `AUTHORIZED`: Autorizada con monto (incluye IVA), puede iniciar reparación
- `IN_PROGRESS`: En proceso de reparación, puede establecer costos reales
- `COMPLETED`: Completada dentro del límite 110%, lista para entregar
- `WAITING_FOR_APPROVAL`: Excedió el 110%, requiere reautorización
- `DELIVERED`: Entregada al cliente
- `CANCELLED`: Cancelada (bloquea todas las operaciones)

**Restricciones de transición:**
- No puedes autorizar sin haber diagnosticado primero
- No puedes pasar a IN_PROGRESS sin autorización previa
- No puedes completar sin estar en IN_PROGRESS
- No puedes reautorizar sin estar en WAITING_FOR_APPROVAL
- No puedes entregar sin estar en COMPLETED
- Una vez cancelada, la orden no puede cambiar de estado

### Cálculos Monetarios

- **IVA**: 16% sobre el subtotal estimado. El monto autorizado se calcula como `subtotal * 1.16`, redondeado con half-even (banker's rounding) a 2 decimales.
- **Límite 110%**: Al intentar completar, si el `total_real` excede el 110% del `monto_autorizado`, la orden pasa a `WAITING_FOR_APPROVAL` y necesitas reautorizar.
- **Redondeo**: Todos los cálculos monetarios usan `Decimal` (nunca `float`) y se redondean con half-even a 2 decimales.
- **Versiones de autorización**: Cada reautorización incrementa `authorization_version`, permitiendo rastrear cuántas veces se reautorizó una orden.

### Gestión de Clientes y Vehículos

- **Find-or-Create**: Al crear órdenes, clientes o vehículos, el sistema busca si ya existen según criterios de identificación. Si existen, los reutiliza; si no, los crea automáticamente.
- **Identificación flexible**: 
  - Clientes: por `id_cliente`, `identificacion` o `nombre` (todos únicos)
  - Vehículos: por `id_vehiculo` o `placa` (placa es única)
- **Transferencia de propiedad**: Los vehículos pueden transferirse entre clientes actualizando el campo `customer` en el endpoint de actualización.
- **Unicidad**: Los campos `identificacion`, `nombre` (clientes) y `placa` (vehículos) son únicos en la base de datos. Intentar crear duplicados retorna error.

### Validaciones Adicionales

- No se pueden agregar servicios después de autorizar (excepto establecer costos reales)
- Los costos estimados y reales deben ser positivos
- Los servicios pueden marcarse como completados individualmente
- Los componentes pueden tener costos reales diferentes a los estimados

## Características Técnicas

### Arquitectura y Diseño

- **Dependency Injection**: Usa `Depends()` de FastAPI para inyectar repositorios y servicios. Esto facilita el testing porque puedes mockear dependencias fácilmente.
- **Exception Handlers Globales**: Handlers centralizados que capturan `ErrorDominio` (errores de negocio) y otros errores, convirtiéndolos a respuestas HTTP apropiadas (400, 404, 500, etc.).
- **Validaciones**: Los path parameters se validan con regex (ej: `order_id` debe tener formato específico). Si no cumple, FastAPI devuelve 422 antes de llegar al código de negocio.

### Logging y Auditoría

- **Middleware de Logging**: Cada request HTTP se loguea automáticamente con métricas de tiempo de respuesta, status code, IP, método, path, etc.
- **Eventos de Dominio**: Cada acción importante (autorizar, completar, cancelar, etc.) genera eventos que se registran tanto en la entidad `Orden` como en el sistema de auditoría externo.
- **Almacén de Eventos**: Implementación flexible que por defecto usa logging, pero puede cambiarse a BD o servicio externo sin tocar el dominio.

### Configuración y Despliegue

- **Lifespan Events**: FastAPI tiene eventos de inicio/cierre donde se configuran las conexiones a BD. Si hay un problema al iniciar, se loguea pero no crashea todo.
- **CORS Configurable**: Puedes configurar qué orígenes permitir vía variable de entorno. Por defecto permite todos (`*`) pero puedes restringirlo.
- **Health Check Mejorado**: El endpoint `/health` verifica no solo la conexión a BD, sino también qué tablas existen y cuáles faltan, facilitando el diagnóstico de problemas.
- **Zona Horaria Configurable**: Todos los cálculos de fecha/hora usan la zona horaria configurada en `TIMEZONE` (default: `America/Bogota`).

## Notas de Implementación

### Convenciones de Nomenclatura

El código interno está completamente en español (clases, métodos, variables, comentarios), pero la API acepta y retorna JSON con keys en inglés para mantener compatibilidad con contratos existentes. El mapeo entre ambos se hace en la capa de mappers (`application/mappers.py`).

### Identificación Flexible de Clientes y Vehículos

Los campos `customer` y `vehicle` en el JSON pueden ser strings simples o objetos con criterios de identificación flexibles. El sistema busca si ese cliente/vehículo ya existe en la BD y si no, lo crea automáticamente. Esto simplifica el uso de la API y evita duplicados.

**Ejemplo con objetos (recomendado):**
```json
{
  "customer": {
    "nombre": "Juan Pérez"
  },
  "vehicle": {
    "placa": "ABC-123"
  },
  "order_id": "ORD-001"
}
```

**Ejemplo con strings simples (compatibilidad hacia atrás):**
```json
{
  "customer": "Juan Pérez",
  "vehicle": "ABC-123",
  "order_id": "ORD-001"
}
```

### Precisión Monetaria

Todos los cálculos monetarios usan `Decimal` desde el inicio. No hay conversiones a `float` en ninguna parte del código, lo que evita los problemas típicos de precisión flotante. El redondeo se hace con half-even (banker's rounding) a 2 decimales.

### Eventos y Trazabilidad

El sistema registra eventos de dominio en cada acción importante. Estos eventos incluyen:
- Tipo de evento (CREATED, AUTHORIZED, COMPLETED, CANCELLED, etc.)
- Timestamp con zona horaria
- Metadatos relevantes (montos, motivos, versiones de autorización)

Los eventos se guardan tanto en la entidad `Orden` (lista interna) como en el sistema de auditoría externo (implementado con logging por defecto, pero intercambiable).

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
