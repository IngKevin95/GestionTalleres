from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class CustomerIdentifierDTO(BaseModel):
    id_cliente: Optional[int] = None
    identificacion: Optional[str] = None
    nombre: Optional[str] = None


class VehicleIdentifierDTO(BaseModel):
    id_vehiculo: Optional[int] = None
    placa: Optional[str] = None


class CrearOrdenDTO(BaseModel):
    customer: CustomerIdentifierDTO
    vehicle: VehicleIdentifierDTO
    timestamp: datetime
    order_id: str
    customer_extra: Optional[Dict[str, Any]] = None
    vehicle_extra: Optional[Dict[str, Any]] = None


class AgregarServicioDTO(BaseModel):
    order_id: str
    descripcion: str
    costo_mano_obra: Decimal
    componentes: List[Dict[str, Any]] = []


class EstablecerEstadoDiagnosticadoDTO(BaseModel):
    order_id: str


class AutorizarDTO(BaseModel):
    timestamp: datetime
    order_id: str


class EstablecerEstadoEnProcesoTDTO(BaseModel):
    order_id: str


class EstablecerCostoRealDTO(BaseModel):
    costo_real: Decimal
    order_id: str
    servicio_id: Optional[int] = None
    service_index: Optional[int] = None
    componentes_reales: Dict[int, Decimal] = {}
    completed: Optional[bool] = None


class IntentarCompletarDTO(BaseModel):
    order_id: str


class ReautorizarDTO(BaseModel):
    nuevo_monto_autorizado: Decimal
    timestamp: datetime
    order_id: str


class EntregarDTO(BaseModel):
    order_id: str


class CancelarDTO(BaseModel):
    order_id: str
    motivo: str


class ComponenteDTO(BaseModel):
    id_componente: int
    descripcion: str
    costo_estimado: str
    costo_real: Optional[str] = None


class ServicioDTO(BaseModel):
    id_servicio: int
    descripcion: str
    costo_mano_obra_estimado: str
    componentes: List[ComponenteDTO]
    completado: bool
    costo_real: Optional[str] = None


class EventoDTO(BaseModel):
    order_id: str
    type: str


class OrdenDTO(BaseModel):
    order_id: str
    status: str
    customer: str
    vehicle: str
    services: List[ServicioDTO]
    subtotal_estimated: str
    authorized_amount: Optional[str] = None
    authorization_version: int
    real_total: str
    events: List[EventoDTO] = []


class ErrorDTO(BaseModel):
    op: Optional[str] = None
    order_id: Optional[str] = None
    code: str
    message: str


class ClienteDTO(BaseModel):
    id_cliente: int
    nombre: str
    identificacion: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    celular: Optional[str] = None


class VehiculoDTO(BaseModel):
    id_vehiculo: int
    placa: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    kilometraje: Optional[int] = None
    id_cliente: int
    cliente_nombre: Optional[str] = None


class CrearClienteDTO(BaseModel):
    nombre: str
    identificacion: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    celular: Optional[str] = None


class CrearVehiculoDTO(BaseModel):
    placa: str
    id_cliente: int
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    kilometraje: Optional[int] = None

