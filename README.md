# GestionTalleres

Sistema para gestionar órdenes de reparación en talleres automotrices. Cubre todo el ciclo: desde que llega un vehículo hasta que se entrega, pasando por diagnóstico, autorización del cliente, reparación y control de costos.

## ¿Qué hace este sistema?

Básicamente, resuelve el problema de gestionar órdenes de reparación de forma ordenada y con control de costos. Cuando un vehículo llega al taller:

1. Se crea una orden con el cliente y el vehículo
2. Se agregan los servicios necesarios (cambio de aceite, reparación de frenos, etc.) con sus componentes (aceite, pastillas, etc.)
3. Se diagnostica y se establece un costo estimado
4. El cliente autoriza el monto (con IVA incluido)
5. Se inicia la reparación
6. Se registran los costos reales (que pueden diferir de los estimados)
7. Si los costos reales exceden el 110% del autorizado, se requiere nueva autorización
8. Se completa y se entrega al cliente

Todo esto con trazabilidad completa: cada acción importante genera un evento que queda registrado para auditoría.

El sistema calcula automáticamente el IVA (16%), valida que no se excedan los límites de autorización, maneja estados de forma estricta (no puedes completar sin autorizar, no puedes entregar sin completar, etc.) y registra todo lo que pasa.

## Decisiones de arquitectura

Este proyecto usa **Arquitectura Hexagonal (Ports & Adapters)** porque necesitábamos separar claramente la lógica de negocio de los detalles técnicos. La idea es simple: el dominio (las reglas de negocio) no debe saber nada de FastAPI, PostgreSQL, ni de cómo se persisten los datos.

### ¿Por qué esta arquitectura?

Imagina que mañana quieres cambiar de PostgreSQL a MongoDB, o de REST a gRPC, o agregar una cola de mensajes. Con esta arquitectura, solo tocas la capa de infraestructura o drivers. El dominio (donde está toda la lógica importante) sigue igual, sin cambios.

### Estructura en capas

**Dominio (`domain/`)**: Aquí vive el corazón del sistema. Las entidades (`Orden`, `Servicio`, `Componente`), las reglas de negocio (validaciones de estado, cálculos monetarios, límite del 110%), y los enums. Este código no depende de nada externo. Si quitas FastAPI y PostgreSQL, el dominio sigue funcionando.

**Aplicación (`application/`)**: Los casos de uso que orquestan el dominio. Cada acción (crear orden, autorizar, completar, etc.) está en su propio módulo. Estos módulos usan las entidades del dominio y las interfaces (puertos) definidas, pero no conocen cómo se persisten los datos.

**Infraestructura (`infrastructure/`)**: Las implementaciones técnicas. Repositorios que hablan con SQLAlchemy, modelos de persistencia, configuración de BD, logging. Si quieres cambiar de PostgreSQL a otra cosa, solo modificas esta capa.

**Drivers (`drivers/api/`)**: El punto de entrada. FastAPI, endpoints, middlewares, dependency injection. Si quieres agregar una CLI o cambiar a gRPC, creas otro driver.

### Principios aplicados

- **SRP (Single Responsibility)**: Cada clase tiene una única razón para cambiar. `Orden` maneja estados y validaciones, `RepositorioOrden` solo persiste, `CrearOrden` solo crea órdenes.

- **DIP (Dependency Inversion)**: El dominio define interfaces (puertos), la infraestructura las implementa. Los casos de uso dependen de `RepositorioOrden` (interfaz), no de `RepositorioOrdenPostgres` (implementación).

- **OCP (Open/Closed)**: Para agregar una nueva acción, creas un nuevo módulo en `application/acciones/` sin tocar el código existente.

- **Encapsulación**: Las entidades protegen su estado interno. No puedes cambiar el estado de una orden directamente; debes usar métodos que validan las reglas de negocio.

### Decisiones técnicas

- **Decimal para dinero**: Nunca `float`. Todos los cálculos monetarios usan `Decimal` con redondeo half-even (banker's rounding) a 2 decimales.

- **PostgreSQL**: Base de datos relacional porque necesitamos integridad referencial y transacciones. Los modelos SQLAlchemy mapean las entidades de dominio a tablas.

- **FastAPI**: Framework moderno, rápido, con validación automática y documentación interactiva. Perfecto para APIs REST.

- **Eventos de dominio**: Cada acción importante genera un evento que se registra tanto en la entidad como en un almacén externo (por defecto logging, pero intercambiable).

- **Nomenclatura en español**: Todo el código interno está en español (clases, métodos, variables). La API acepta y retorna JSON con keys en inglés para mantener compatibilidad con contratos existentes. El mapeo se hace en la capa de mappers.

### ¿Qué ganas con esto?

- **Testeable**: Puedes testear el dominio sin necesidad de BD ni FastAPI. Los repositorios son interfaces, así que puedes usar implementaciones en memoria para tests.

- **Mantenible**: Si hay un bug en una regla de negocio, sabes exactamente dónde está (en el dominio). Si hay un problema de persistencia, está en infraestructura.

- **Extensible**: Agregar una nueva acción es crear un módulo nuevo. Cambiar de BD es cambiar una implementación. No hay efectos colaterales.

- **Independiente de frameworks**: El dominio no sabe que existe FastAPI. Si mañana quieres usar Django o Flask, solo cambias la capa de drivers.

## Instalación

Tienes dos opciones: Docker (recomendado, más fácil) o instalación local. Docker es más simple porque no tienes que configurar PostgreSQL manualmente.

### Opción 1: Con Docker (Recomendado)

Si tienes Docker y Docker Compose instalados, esto es lo más rápido:

1. **Crea el archivo `.env`** en la raíz del proyecto (dentro de `GestionTalleres/`):

```bash
POSTGRES_USER=talleres_user
POSTGRES_PASSWORD=talleres_pass
POSTGRES_DB=talleres
POSTGRES_VERSION=15
DB_HOST=db
DB_INTERNAL_PORT=5432
DB_EXTERNAL_PORT=5438
API_PORT=8000
TIMEZONE=America/Bogota
LOG_LEVEL=INFO
LOG_FORMAT=text
LOG_DIR=logs
CONTAINER_NAME_DB=gestion_talleres_db
CONTAINER_NAME_API=gestion_talleres_api
```

Puedes cambiar estos valores si quieres, pero estos funcionan bien para empezar.

2. **Levanta los servicios**:

```bash
docker-compose up --build
```

Esto construye la imagen de la API y levanta PostgreSQL. La primera vez puede tardar un poco mientras descarga las imágenes.

3. **Inicializa la base de datos**:

En otra terminal (o espera a que termine el paso anterior), ejecuta:

```bash
docker-compose exec api python init_db.py
```

Esto crea todas las tablas necesarias. Si ya existen, no hace nada (es idempotente).

4. **Listo**. La API está corriendo en `http://localhost:8000` y PostgreSQL en `localhost:5438`.

Para ver la documentación interactiva de la API, abre `http://localhost:8000/docs` en tu navegador.

**Comandos útiles**:

- Detener los servicios: `docker-compose down`
- Detener y eliminar datos (empezar de cero): `docker-compose down -v`
- Ver logs: `docker-compose logs -f api` (o `db` para la base de datos)
- Ejecutar comandos dentro del contenedor: `docker-compose exec api bash`

### Opción 2: Instalación local

Si prefieres correr todo localmente sin Docker:

1. **Requisitos**:
   - Python 3.11 o superior
   - PostgreSQL (cualquier versión reciente funciona, se prueba con 15)

2. **Crea un entorno virtual**:

```bash
cd GestionTalleres
python -m venv venv
```

Luego actívalo:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. **Instala las dependencias**:

```bash
pip install -r requirements.txt
```

Las principales son FastAPI, SQLAlchemy, psycopg2 para PostgreSQL, y pytest para tests.

4. **Configura la base de datos**:

Crea un archivo `.env` en la raíz del proyecto:

```bash
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_DB=talleres
DB_HOST=localhost
DB_INTERNAL_PORT=5432
TIMEZONE=America/Bogota
LOG_LEVEL=INFO
LOG_FORMAT=text
LOG_DIR=logs
```

Crea la base de datos en PostgreSQL:

```sql
CREATE DATABASE talleres;
```

5. **Inicializa las tablas**:

```bash
python init_db.py
```

Esto crea las tablas: `ordenes`, `clientes`, `vehiculos`, `servicios`, `componentes`, `eventos`.

6. **Ejecuta el servidor**:

```bash
uvicorn app.drivers.api.main:app --reload
```

El `--reload` hace que se recargue automáticamente cuando cambias código (útil para desarrollo).

La API estará disponible en `http://localhost:8000` y la documentación en `http://localhost:8000/docs`.

### Verificar que funciona

Una vez que tengas todo corriendo (Docker o local), puedes verificar:

1. **Health check**:
```bash
curl http://localhost:8000/health
```

Debería retornar algo como 
`
{
  "status": "ok",
  "api": "operativa",
  "database": "conectada",
  "tablas": [
    "clientes",
    "vehiculos",
    "ordenes",
    "servicios",
    "eventos",
    "componentes"
  ],
  "tablas_faltantes": [],
  "mensaje": null
}
`.

2. **Documentación interactiva**: Abre `http://localhost:8000/docs` en tu navegador. Ahí puedes probar los endpoints directamente.

3. **Ejecutar tests** (opcional):
```bash
pytest
```

O con cobertura:
```bash
pytest --cov=app --cov-report=html
```

Esto genera un reporte HTML en `htmlcov/index.html`.

### Variables de entorno disponibles

El archivo `.env` soporta estas variables (con valores por defecto si no las defines):

**Base de datos**:
- `POSTGRES_USER`: Usuario de PostgreSQL (default: `talleres_user`)
- `POSTGRES_PASSWORD`: Contraseña (default: `talleres_pass`)
- `POSTGRES_DB`: Nombre de la BD (default: `talleres`)
- `POSTGRES_VERSION`: Versión de PostgreSQL (default: `15`)
- `DB_HOST`: Host de la BD (`db` para Docker, `localhost` para local)
- `DB_INTERNAL_PORT`: Puerto interno (default: `5432`)
- `DB_EXTERNAL_PORT`: Puerto expuesto al host (default: `5438`)

**API**:
- `API_PORT`: Puerto de la API (default: `8000`)

**Zona horaria**:
- `TIMEZONE`: Zona horaria para cálculos de fecha/hora (default: `America/Bogota`). Formato IANA (ej: `America/Mexico_City`, `UTC`, `Europe/Madrid`).

**Logging**:
- `LOG_LEVEL`: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL) - default: `INFO`
- `LOG_FORMAT`: Formato (json, text) - default: `text`
- `LOG_DIR`: Directorio para logs - default: `logs/`
- `LOG_ROTATION`: Tipo de rotación (time, size, none) - default: `time`
- `LOG_TO_CONSOLE`: Habilitar logging a consola (true/false) - default: `false`

**CORS**:
- `CORS_ORIGINS`: Orígenes permitidos separados por comas (default: `*` para permitir todos)

## Estructura del proyecto

```
app/
├── domain/                    # Lógica de negocio pura
│   ├── entidades/             # Orden, Servicio, Componente, Cliente, Vehículo, Evento
│   ├── enums/                 # EstadoOrden, CodigoError
│   ├── exceptions.py          # ErrorDominio
│   ├── dinero.py              # Utilidades Decimal y redondeo
│   └── zona_horaria.py        # Manejo de timezone
│
├── application/               # Casos de uso (orquestación)
│   ├── acciones/              # Cada acción en su archivo
│   │   ├── orden.py           # CrearOrden, CancelarOrden, EntregarOrden
│   │   ├── servicios.py       # AgregarServicio, EstablecerCostoReal
│   │   ├── estados.py         # EstablecerEstadoDiagnosticado, EstablecerEstadoEnProceso
│   │   └── autorizacion.py    # Autorizar, Reautorizar, IntentarCompletar
│   ├── action_service.py      # Servicio orquestador que procesa comandos
│   ├── dtos.py                # Data Transfer Objects
│   ├── mappers.py             # Conversores entre JSON, DTOs y entidades
│   └── ports.py               # Interfaces (RepositorioOrden, AlmacenEventos)
│
├── infrastructure/            # Implementaciones técnicas
│   ├── models/                # Modelos SQLAlchemy para persistencia
│   ├── repositories/          # Implementaciones de repositorios
│   ├── db.py                  # Configuración de conexión a PostgreSQL
│   ├── logging_config.py       # Configuración del sistema de logging
│   └── logger.py              # Implementación de AlmacenEventos usando logging
│
└── drivers/                   # Puntos de entrada
    └── api/                    # API REST con FastAPI
        ├── main.py             # Aplicación FastAPI, configuración, lifespan
        ├── routes.py           # Todos los endpoints
        ├── dependencies.py    # Dependency injection
        ├── schemas.py          # Modelos Pydantic para requests/responses
        └── middleware.py       # Middleware de logging de requests

tests/
├── unit/                      # Tests unitarios organizados por capa
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

El endpoint más usado es `POST /commands` que procesa un batch de comandos en un solo request. Útil para ejecutar secuencias de operaciones de una vez.

- `GET /` - Información básica de la API
- `GET /health` - Health check de API y base de datos
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

La documentación completa está en `http://localhost:8000/docs` una vez que tengas el servidor corriendo.

## Tests

Los tests están organizados por capas en `tests/unit/` (domain, application, infrastructure, drivers) y hay tests de integración en `tests/integration/`.

Para ejecutar todos los tests:

```bash
pytest
```

Con cobertura:

```bash
pytest --cov=app --cov-report=html
```

Esto genera un reporte HTML en `htmlcov/index.html`. La cobertura actual ronda el 74% aproximadamente.

Para ejecutar solo tests de una capa:

```bash
pytest tests/unit/domain/
pytest tests/unit/application/
pytest tests/integration/
```

### Pruebas funcionales con REST Client

Además de los tests automatizados, hay un archivo `tests/integration/tests.rest` con pruebas funcionales que puedes ejecutar directamente. Este archivo contiene diferentes escenarios de uso:

- Flujo completo desde creación hasta entrega
- Casos donde se excede el 110% del monto autorizado
- Validaciones de estados y transiciones
- Manejo de errores y reautorizaciones

Para usarlo, necesitas la extensión **REST Client** en VS Code (o cualquier cliente HTTP que soporte el formato `.rest`). Una vez que tengas el servidor corriendo, simplemente abre el archivo y haz clic en "Send Request" sobre cada petición para ejecutarla. Es útil para probar manualmente los diferentes flujos del sistema y ver las respuestas en tiempo real.


