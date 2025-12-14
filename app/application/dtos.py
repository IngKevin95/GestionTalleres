from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class CrearOrdenDTO(BaseModel):
    cliente: str
    vehiculo: str
    timestamp: datetime
    order_id: Optional[int] = None


class AgregarServicioDTO(BaseModel):
    order_id: int
    descripcion: str
    costo_mano_obra: Decimal
    componentes: List[Dict[str, Any]] = []


class EstablecerEstadoDiagnosticadoDTO(BaseModel):
    order_id: int


class AutorizarDTO(BaseModel):
    timestamp: datetime
    order_id: int


class EstablecerEstadoEnProcesoTDTO(BaseModel):
    order_id: int


class EstablecerCostoRealDTO(BaseModel):
    costo_real: Decimal
    order_id: int
    servicio_id: Optional[int] = None
    service_index: Optional[int] = None
    componentes_reales: Dict[int, Decimal] = {}
    completed: Optional[bool] = None


class IntentarCompletarDTO(BaseModel):
    order_id: int


class ReautorizarDTO(BaseModel):
    nuevo_monto_autorizado: Decimal
    timestamp: datetime
    order_id: int


class EntregarDTO(BaseModel):
    order_id: int


class CancelarDTO(BaseModel):
    order_id: int
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
    order_id: int
    type: str


class OrdenDTO(BaseModel):
    order_id: int
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
    order_id: Optional[int] = None
    code: str
    message: str


class ClienteDTO(BaseModel):
    id_cliente: int
    nombre: str


class VehiculoDTO(BaseModel):
    id_vehiculo: int
    descripcion: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    id_cliente: int
    cliente_nombre: Optional[str] = None


class CrearClienteDTO(BaseModel):
    nombre: str


class CrearVehiculoDTO(BaseModel):
    descripcion: str
    id_cliente: int
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None

