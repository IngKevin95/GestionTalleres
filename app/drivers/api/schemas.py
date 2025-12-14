from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator

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
                        "op": "CREATE_ORDER",
                        "ts": "2025-03-01T09:00:00Z",
                        "data": {
                            "order_id": "R001",
                            "customer": "ACME",
                            "vehicle": "ABC-123"
                        }
                    },
                    {
                        "op": "ADD_SERVICE",
                        "ts": "2025-03-01T09:05:00Z",
                        "data": {
                            "order_id": "R001",
                            "service": {
                                "description": "Engine repair",
                                "labor_estimated_cost": "10000.00",
                                "components": [
                                    {
                                        "description": "Oil pump",
                                        "estimated_cost": "1500.00"
                                    }
                                ]
                            }
                        }
                    },
                    {
                        "op": "SET_STATE_DIAGNOSED",
                        "ts": "2025-03-01T09:10:00Z",
                        "data": {
                            "order_id": "R001"
                        }
                    },
                    {
                        "op": "AUTHORIZE",
                        "ts": "2025-03-01T09:11:00Z",
                        "data": {
                            "order_id": "R001"
                        }
                    },
                    {
                        "op": "SET_STATE_IN_PROGRESS",
                        "ts": "2025-03-01T09:15:00Z",
                        "data": {
                            "order_id": "R001"
                        }
                    },
                    {
                        "op": "SET_REAL_COST",
                        "ts": "2025-03-01T09:20:00Z",
                        "data": {
                            "order_id": "R001",
                            "service_index": 1,
                            "real_cost": "15000.00",
                            "completed": True
                        }
                    },
                    {
                        "op": "TRY_COMPLETE",
                        "ts": "2025-03-01T09:25:00Z",
                        "data": {
                            "order_id": "R001"
                        }
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
    customer: str = Field(..., min_length=1, max_length=500, description="Nombre del cliente")
    vehicle: str = Field(..., min_length=1, max_length=500, description="Descripción del vehículo")
    order_id: str = Field(..., min_length=1, max_length=100, description="ID de la orden")
    ts: Optional[str] = Field(None, description="Timestamp opcional en formato ISO. Si se envía como string vacío, se ignora.")
    
    @field_validator('customer')
    @classmethod
    def validate_customer(cls, v):
        if not v or not str(v).strip():
            raise ValueError("customer es requerido y no puede estar vacío")
        return str(v).strip()
    
    @field_validator('vehicle')
    @classmethod
    def validate_vehicle(cls, v):
        if not v or not str(v).strip():
            raise ValueError("vehicle es requerido y no puede estar vacío")
        return str(v).strip()
    
    @field_validator('order_id')
    @classmethod
    def validate_order_id(cls, v):
        if not v or not str(v).strip():
            raise ValueError("order_id es requerido y no puede estar vacío")
        return str(v).strip()
    
    @field_validator('ts', mode='before')
    @classmethod
    def validate_ts(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        if isinstance(v, str):
            if not v or not v.strip():
                return None
            return v.strip()
        return v


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
    identificacion: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    celular: Optional[str] = None


class CreateClienteRequest(BaseModel):
    nombre: str
    identificacion: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    celular: Optional[str] = None


class UpdateClienteRequest(BaseModel):
    nombre: Optional[str] = None
    identificacion: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    celular: Optional[str] = None


class ListClientesResponse(BaseModel):
    clientes: List[ClienteResponse]


class CustomerIdentifier(BaseModel):
    id_cliente: Optional[int] = None
    identificacion: Optional[str] = None
    nombre: Optional[str] = None


class VehicleIdentifier(BaseModel):
    id_vehiculo: Optional[int] = None
    placa: Optional[str] = None


class VehiculoResponse(BaseModel):
    id_vehiculo: int
    placa: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    kilometraje: Optional[int] = None
    id_cliente: int
    cliente_nombre: Optional[str] = None


class CreateVehiculoRequest(BaseModel):
    placa: str
    customer: CustomerIdentifier
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    kilometraje: Optional[int] = None


class UpdateVehiculoRequest(BaseModel):
    placa: Optional[str] = None
    customer: Optional[Union[CustomerIdentifier, str]] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    kilometraje: Optional[int] = None
    
    @field_validator('customer', mode='before')
    @classmethod
    def validate_customer(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return CustomerIdentifier(nombre=v)
        if isinstance(v, dict):
            return CustomerIdentifier(**v)
        return v


class ListVehiculosResponse(BaseModel):
    vehiculos: List[VehiculoResponse]

