from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator


class HealthResponse(BaseModel):
    status: str
    api: str
    database: Optional[str] = None
    tablas: List[str] = Field(default_factory=list)
    tablas_faltantes: List[str] = Field(default_factory=list)
    mensaje: Optional[str] = None


class CommandsRequest(BaseModel):
    commands: List[Dict[str, Any]] = Field(..., min_length=1)


class CommandsResponse(BaseModel):
    orders: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    errors: List[Dict[str, Any]] = Field(default_factory=list)


class SetStateRequest(BaseModel):
    state: str


class CreateOrderRequest(BaseModel):
    customer: str = Field(..., min_length=1)
    vehicle: str = Field(..., min_length=1)
    order_id: str = Field(..., min_length=1)
    ts: Optional[str] = None
    
    @field_validator('customer', 'vehicle', 'order_id')
    @classmethod
    def validar_campo(cls, v):
        if not v or not str(v).strip():
            raise ValueError("campo requerido y no puede estar vacío")
        return str(v).strip()
    
    @field_validator('ts', mode='before')
    @classmethod
    def validar_ts(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        if isinstance(v, str) and v.strip():
            return v.strip()
        return None if isinstance(v, str) else v


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
    def normalizar_customer(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return CustomerIdentifier(nombre=v)
        if isinstance(v, dict):
            return CustomerIdentifier(**v)
        return v


class ListVehiculosResponse(BaseModel):
    vehiculos: List[VehiculoResponse]

