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
    ClienteDTO, VehiculoDTO
)


ZULU_TO_UTC_OFFSET = '+00:00'

def json_a_crear_orden_dto(json_data: dict, ts_comando: Optional[str] = None) -> CrearOrdenDTO:
    order_id = json_data.get("order_id", "")
    if not order_id or not str(order_id).strip():
        raise ValueError("order_id es requerido y no puede estar vacío")
    
    customer = json_data.get("customer", "")
    if not customer or not str(customer).strip():
        raise ValueError("customer es requerido y no puede estar vacío")
    
    vehicle = json_data.get("vehicle", "")
    if not vehicle or not str(vehicle).strip():
        raise ValueError("vehicle es requerido y no puede estar vacío")
    
    ts = ts_comando or json_data.get("ts")
    if not ts or (isinstance(ts, str) and not ts.strip()):
        ts = ahora().isoformat()
    
    ts_normalizado = str(ts).replace('Z', ZULU_TO_UTC_OFFSET)
    
    return CrearOrdenDTO(
        cliente=str(customer).strip(),
        vehiculo=str(vehicle).strip(),
        timestamp=datetime.fromisoformat(ts_normalizado),
        order_id=str(order_id).strip()
    )


def json_a_agregar_servicio_dto(json_data: dict) -> AgregarServicioDTO:
    service_obj = json_data.get("service")
    if service_obj:
        descripcion = service_obj.get("description", "")
        labor_cost = service_obj.get("labor_estimated_cost", 0)
        components = service_obj.get("components", [])
    else:
        descripcion = json_data.get("description", "")
        labor_cost = json_data.get("labor_estimated_cost", 0)
        components = json_data.get("components", [])
    
    # Normalizar componentes
    componentes = []
    for comp in components:
        tmp = {
            "description": comp.get("description", ""),
            "estimated_cost": str(comp.get("estimated_cost", 0))
        }
        componentes.append(tmp)
    
    order_id = json_data.get("order_id", "")
    return AgregarServicioDTO(
        order_id=str(order_id),
        descripcion=descripcion,
        costo_mano_obra=a_decimal(labor_cost),
        componentes=componentes
    )


def json_a_establecer_estado_diagnosticado_dto(json_data: dict) -> EstablecerEstadoDiagnosticadoDTO:
    order_id = json_data.get("order_id", "")
    return EstablecerEstadoDiagnosticadoDTO(order_id=str(order_id))


def json_a_autorizar_dto(json_data: dict, ts_comando: Optional[str] = None) -> AutorizarDTO:
    ts = ts_comando or json_data.get("ts") or ahora().isoformat()
    ts_fixed = ts.replace('Z', ZULU_TO_UTC_OFFSET)
    order_id = json_data.get("order_id", "")
    return AutorizarDTO(
        order_id=str(order_id),
        timestamp=datetime.fromisoformat(ts_fixed)
    )


def json_a_establecer_estado_en_proceso_dto(json_data: dict) -> EstablecerEstadoEnProcesoTDTO:
    order_id = json_data.get("order_id", "")
    return EstablecerEstadoEnProcesoTDTO(order_id=str(order_id))


def json_a_establecer_costo_real_dto(json_data: dict) -> EstablecerCostoRealDTO:
    comps_real = {}
    for comp_id, costo in json_data.get("components_real", {}).items():
        comps_real[int(comp_id)] = a_decimal(costo)
    
    order_id = json_data.get("order_id", "")
    servicio_id_raw = json_data.get("service_id")
    servicio_id_int = int(servicio_id_raw) if servicio_id_raw is not None else None
    
    return EstablecerCostoRealDTO(
        costo_real=a_decimal(json_data.get("real_cost", 0)),
        order_id=str(order_id),
        servicio_id=servicio_id_int,
        service_index=json_data.get("service_index"),
        componentes_reales=comps_real,
        completed=json_data.get("completed")
    )


def json_a_intentar_completar_dto(json_data: dict) -> IntentarCompletarDTO:
    order_id = json_data.get("order_id", "")
    return IntentarCompletarDTO(order_id=str(order_id))


def json_a_reautorizar_dto(json_data: dict, ts_comando: Optional[str] = None) -> ReautorizarDTO:
    ts = ts_comando or json_data.get("ts") or ahora().isoformat()
    order_id = json_data.get("order_id", "")
    monto = a_decimal(json_data.get("new_authorized_amount", 0))
    ts_parsed = datetime.fromisoformat(ts.replace('Z', ZULU_TO_UTC_OFFSET))
    return ReautorizarDTO(order_id=str(order_id), nuevo_monto_autorizado=monto, timestamp=ts_parsed)


def json_a_entregar_dto(json_data: dict) -> EntregarDTO:
    order_id = json_data.get("order_id", "")
    return EntregarDTO(order_id=str(order_id))


def json_a_cancelar_dto(json_data: dict) -> CancelarDTO:
    order_id = json_data.get("order_id", "")
    return CancelarDTO(
        order_id=str(order_id),
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
        descripcion=v.descripcion,
        marca=v.marca,
        modelo=v.modelo,
        anio=v.anio,
        kilometraje=v.kilometraje,
        id_cliente=v.id_cliente,
        cliente_nombre=cliente_nombre
    )

