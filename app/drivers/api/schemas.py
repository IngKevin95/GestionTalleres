from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

DESC_NOMBRE_CLIENTE = "Nombre del cliente"
DESC_DESCRIPCION_VEHICULO = "Descripción del vehículo"


class HealthResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "api": "operativa",
                "database": "conectada",
                "tablas": ["ordenes", "clientes", "vehiculos", "servicios", "componentes", "eventos"],
                "tablas_faltantes": [],
                "mensaje": None
            }
        }
    )
    status: str = Field(..., description="Estado general: 'ok', 'warning' o 'error'")
    api: str = Field(..., description="Estado de la API")
    database: Optional[str] = Field(None, description="Estado de la conexión a la base de datos")
    tablas: List[str] = Field(default_factory=list, description="Lista de tablas existentes en la BD")
    tablas_faltantes: List[str] = Field(default_factory=list, description="Lista de tablas que faltan")
    mensaje: Optional[str] = Field(None, description="Mensaje adicional si hay advertencias o errores")


class CommandsRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "commands": [
                    {
                        "command": "CREATE_ORDER",
                        "customer": "Juan Pérez",
                        "vehicle": "Toyota Corolla 2020",
                        "ts": "2024-01-15T10:00:00-05:00"
                    },
                    {
                        "command": "ADD_SERVICE",
                        "order_id": "ORD-12345678",
                        "description": "Cambio de aceite",
                        "labor_estimated_cost": 50000,
                        "components": [
                            {
                                "description": "Aceite sintético 5W-30",
                                "estimated_cost": 80000
                            }
                        ]
                    }
                ]
            }
        }
    )
    commands: List[Dict[str, Any]] = Field(
        ...,
        description="Lista de comandos a procesar",
        min_length=1
    )


class CommandsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "orders": [
                    {
                        "order_id": "ORD-12345678",
                        "status": "CREATED",
                        "customer": "Juan Pérez",
                        "vehicle": "Toyota Corolla 2020",
                        "services": [],
                        "authorization_version": 0,
                        "real_total": "0"
                    }
                ],
                "events": [
                    {
                        "type": "CREATED",
                        "ts": "2024-01-15T10:00:00Z",
                        "metadata": {}
                    }
                ],
                "errors": []
            }
        }
    )
    orders: List[Dict[str, Any]] = Field(..., description="Lista de órdenes procesadas")
    events: List[Dict[str, Any]] = Field(..., description="Lista de eventos generados")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de errores encontrados")


class SetStateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "state": "DIAGNOSED"
            }
        }
    )
    state: str = Field(
        ...,
        description="Estado a establecer",
        json_schema_extra={"enum": ["DIAGNOSED", "IN_PROGRESS"]}
    )


class CreateOrderRequest(BaseModel):
    customer: str
    vehicle: str
    order_id: Optional[int] = None
    ts: Optional[datetime] = None


class AddServiceRequest(BaseModel):
    description: Optional[str] = None
    service: Optional[Dict[str, Any]] = None
    labor_estimated_cost: Optional[Decimal] = None
    components: Optional[List[Dict[str, Any]]] = []


class SetRealCostRequest(BaseModel):
    service_id: Optional[int] = None
    service_index: Optional[int] = None
    real_cost: Decimal
    completed: Optional[bool] = None
    components_real: Optional[Dict[int, Decimal]] = {}


class AuthorizeRequest(BaseModel):
    ts: Optional[datetime] = None


class ReauthorizeRequest(BaseModel):
    new_authorized_amount: Decimal
    ts: Optional[datetime] = None


class CancelRequest(BaseModel):
    reason: str


class ClienteResponse(BaseModel):
    id_cliente: int
    nombre: str


class CreateClienteRequest(BaseModel):
    nombre: str


class UpdateClienteRequest(BaseModel):
    nombre: str


class ListClientesResponse(BaseModel):
    clientes: List[ClienteResponse]


class VehiculoResponse(BaseModel):
    id_vehiculo: int
    descripcion: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    id_cliente: int
    cliente_nombre: Optional[str] = None


class CreateVehiculoRequest(BaseModel):
    descripcion: str
    id_cliente: int
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None


class UpdateVehiculoRequest(BaseModel):
    descripcion: Optional[str] = None
    id_cliente: Optional[int] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None


class ListVehiculosResponse(BaseModel):
    vehiculos: List[VehiculoResponse]

