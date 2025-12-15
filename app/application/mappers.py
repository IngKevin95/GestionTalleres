from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal
from ..domain.entidades import Orden, Servicio, Componente, Evento, Cliente, Vehiculo
from ..domain.zona_horaria import ahora
from ..domain.dinero import a_decimal
from .dtos import (
    CrearOrdenDTO, AgregarServicioDTO, EstablecerEstadoDiagnosticadoDTO,
    AutorizarDTO, EstablecerEstadoEnProcesoTDTO, EstablecerCostoRealDTO,
    IntentarCompletarDTO, ReautorizarDTO, EntregarDTO, CancelarDTO,
    OrdenDTO, ServicioDTO, ComponenteDTO, EventoDTO,
    ClienteDTO, VehiculoDTO, CustomerIdentifierDTO, VehicleIdentifierDTO
)


ZULU_OFFSET = '+00:00'

def crear_orden_dto(json_data: dict, ts_comando: Optional[str] = None) -> CrearOrdenDTO:
    order_id = json_data.get("order_id", "")
    if not order_id or not str(order_id).strip():
        raise ValueError("order_id es requerido y no puede estar vacío")
    
    customer_data = json_data.get("customer")
    if not customer_data:
        raise ValueError("customer es requerido y no puede estar vacío")
    
    if isinstance(customer_data, str):
        customer_identifier = CustomerIdentifierDTO(nombre=customer_data.strip())
    elif isinstance(customer_data, dict):
        customer_identifier = CustomerIdentifierDTO(
            id_cliente=customer_data.get("id_cliente"),
            identificacion=customer_data.get("identificacion"),
            nombre=customer_data.get("nombre")
        )
        criterios = sum([1 for v in [customer_identifier.id_cliente, customer_identifier.identificacion, customer_identifier.nombre] if v is not None])
        if criterios != 1:
            raise ValueError("customer debe tener exactamente uno de: id_cliente, identificacion, o nombre")
    else:
        raise ValueError("customer debe ser un string o un objeto con id_cliente, identificacion o nombre")
    
    vehicle_data = json_data.get("vehicle")
    if not vehicle_data:
        raise ValueError("vehicle es requerido y no puede estar vacío")
    
    if isinstance(vehicle_data, str):
        vehicle_identifier = VehicleIdentifierDTO(placa=vehicle_data.strip())
    elif isinstance(vehicle_data, dict):
        vehicle_identifier = VehicleIdentifierDTO(
            id_vehiculo=vehicle_data.get("id_vehiculo"),
            placa=vehicle_data.get("placa")
        )
        criterios = sum([1 for v in [vehicle_identifier.id_vehiculo, vehicle_identifier.placa] if v is not None])
        if criterios != 1:
            raise ValueError("vehicle debe tener exactamente uno de: id_vehiculo o placa")
    else:
        raise ValueError("vehicle debe ser un string (placa) o un objeto con id_vehiculo o placa")
    
    ts = ts_comando or json_data.get("ts")
    if not ts or (isinstance(ts, str) and not ts.strip()):
        ts = ahora().isoformat()
    
    ts_normalizado = str(ts).replace('Z', ZULU_OFFSET)
    
    customer_extra = None
    if isinstance(customer_data, dict):
        customer_extra = {
            "correo": customer_data.get("correo"),
            "direccion": customer_data.get("direccion"),
            "celular": customer_data.get("celular")
        }
        if all(v is None for v in customer_extra.values()):
            customer_extra = None
    
    vehicle_extra = None
    if isinstance(vehicle_data, dict):
        vehicle_extra = {
            "marca": vehicle_data.get("marca"),
            "modelo": vehicle_data.get("modelo"),
            "anio": vehicle_data.get("anio"),
            "kilometraje": vehicle_data.get("kilometraje")
        }
        if all(v is None for v in vehicle_extra.values()):
            vehicle_extra = None
    
    return CrearOrdenDTO(
        customer=customer_identifier,
        vehicle=vehicle_identifier,
        timestamp=datetime.fromisoformat(ts_normalizado),
        order_id=str(order_id).strip(),
        customer_extra=customer_extra,
        vehicle_extra=vehicle_extra
    )


def agregar_servicio_dto(json_data: dict) -> AgregarServicioDTO:
    srv = json_data.get("service")
    if srv:
        desc = srv.get("description", "")
        labor = srv.get("labor_estimated_cost", 0)
        comps = srv.get("components", [])
    else:
        desc = json_data.get("description", "")
        labor = json_data.get("labor_estimated_cost", 0)
        comps = json_data.get("components", [])
    
    componentes = []
    for c in comps:
        componentes.append({
            "description": c.get("description", ""),
            "estimated_cost": str(c.get("estimated_cost", 0))
        })
    
    return AgregarServicioDTO(
        order_id=str(json_data.get("order_id", "")),
        descripcion=desc,
        costo_mano_obra=a_decimal(labor),
        componentes=componentes
    )


def estado_diagnosticado_dto(json_data: dict) -> EstablecerEstadoDiagnosticadoDTO:
    return EstablecerEstadoDiagnosticadoDTO(order_id=str(json_data.get("order_id", "")))


def autorizar_dto(json_data: dict, ts_comando: Optional[str] = None) -> AutorizarDTO:
    ts = ts_comando or json_data.get("ts") or ahora().isoformat()
    ts_fixed = ts.replace('Z', ZULU_OFFSET)
    return AutorizarDTO(
        order_id=str(json_data.get("order_id", "")),
        timestamp=datetime.fromisoformat(ts_fixed)
    )


def estado_en_proceso_dto(json_data: dict) -> EstablecerEstadoEnProcesoTDTO:
    return EstablecerEstadoEnProcesoTDTO(order_id=str(json_data.get("order_id", "")))


def costo_real_dto(json_data: dict) -> EstablecerCostoRealDTO:
    comps_real = {}
    for comp_id, costo in json_data.get("components_real", {}).items():
        comps_real[int(comp_id)] = a_decimal(costo)
    
    srv_id = json_data.get("service_id")
    return EstablecerCostoRealDTO(
        costo_real=a_decimal(json_data.get("real_cost", 0)),
        order_id=str(json_data.get("order_id", "")),
        servicio_id=int(srv_id) if srv_id is not None else None,
        service_index=json_data.get("service_index"),
        componentes_reales=comps_real,
        completed=json_data.get("completed")
    )


def intentar_completar_dto(json_data: dict) -> IntentarCompletarDTO:
    return IntentarCompletarDTO(order_id=str(json_data.get("order_id", "")))


def reautorizar_dto(json_data: dict, ts_comando: Optional[str] = None) -> ReautorizarDTO:
    ts = ts_comando or json_data.get("ts") or ahora().isoformat()
    monto = a_decimal(json_data.get("new_authorized_amount", 0))
    ts_parsed = datetime.fromisoformat(ts.replace('Z', ZULU_OFFSET))
    return ReautorizarDTO(
        order_id=str(json_data.get("order_id", "")),
        nuevo_monto_autorizado=monto,
        timestamp=ts_parsed
    )


def entregar_dto(json_data: dict) -> EntregarDTO:
    return EntregarDTO(order_id=str(json_data.get("order_id", "")))


def cancelar_dto(json_data: dict) -> CancelarDTO:
    return CancelarDTO(
        order_id=str(json_data.get("order_id", "")),
        motivo=json_data.get("reason", "")
    )


def componente_a_dto(comp: Componente) -> ComponenteDTO:
    costo_real_str = str(comp.costo_real) if comp.costo_real else None
    if comp.id_componente is None:
        raise ValueError("Componente debe tener id_componente asignado")
    return ComponenteDTO(
        id_componente=comp.id_componente,
        descripcion=comp.descripcion,
        costo_estimado=str(comp.costo_estimado),
        costo_real=costo_real_str
    )


def servicio_a_dto(servicio: Servicio) -> ServicioDTO:
    comps = []
    for c in servicio.componentes:
        comps.append(componente_a_dto(c))
    
    costo_real_str = str(servicio.costo_real) if servicio.costo_real else None
    if servicio.id_servicio is None:
        raise ValueError("Servicio debe tener id_servicio asignado")
    return ServicioDTO(
        id_servicio=servicio.id_servicio,
        descripcion=servicio.descripcion,
        costo_mano_obra_estimado=str(servicio.costo_mano_obra_estimado),
        componentes=comps,
        completado=servicio.completado,
        costo_real=costo_real_str
    )


def evento_a_dto(evento: Evento, order_id: str) -> EventoDTO:
    return EventoDTO(
        order_id=order_id,
        type=evento.tipo
    )


def orden_a_dto(orden: Orden) -> OrdenDTO:
    if not orden.order_id:
        raise ValueError("Orden debe tener order_id asignado")
    
    subtotal = sum(s.calcular_subtotal_estimado() for s in orden.servicios)
    
    servicios_dto = []
    for s in orden.servicios:
        servicios_dto.append(servicio_a_dto(s))
    
    eventos_dto = []
    for e in orden.eventos:
        eventos_dto.append(evento_a_dto(e, orden.order_id))
    
    auth_amount = f"{orden.monto_autorizado:.2f}" if orden.monto_autorizado else None
    
    return OrdenDTO(
        order_id=orden.order_id,
        status=orden.estado.value,
        customer=orden.cliente,
        vehicle=orden.vehiculo,
        services=servicios_dto,
        subtotal_estimated=f"{subtotal:.2f}",
        authorized_amount=auth_amount,
        authorization_version=orden.version_autorizacion,
        real_total=f"{orden.total_real:.2f}",
        events=eventos_dto
    )


def cliente_a_dto(c: Cliente) -> ClienteDTO:
    if c.id_cliente is None:
        raise ValueError("Cliente debe tener id_cliente asignado")
    return ClienteDTO(
        id_cliente=c.id_cliente,
        nombre=c.nombre,
        identificacion=c.identificacion,
        correo=c.correo,
        direccion=c.direccion,
        celular=c.celular
    )


def vehiculo_a_dto(v: Vehiculo, cliente_nombre: Optional[str] = None) -> VehiculoDTO:
    if v.id_vehiculo is None or v.id_cliente is None:
        raise ValueError("Vehículo debe tener id_vehiculo e id_cliente asignados")
    return VehiculoDTO(
        id_vehiculo=v.id_vehiculo,
        placa=v.placa,
        marca=v.marca,
        modelo=v.modelo,
        anio=v.anio,
        kilometraje=v.kilometraje,
        id_cliente=v.id_cliente,
        cliente_nombre=cliente_nombre
    )

