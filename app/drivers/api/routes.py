from fastapi import APIRouter, HTTPException, Depends, status, Path, Body
from typing import List, Dict, Any, Optional

from ...application.action_service import ActionService
from ...application.dtos import OrdenDTO, EventoDTO, ErrorDTO, CrearOrdenDTO, AgregarServicioDTO, AutorizarDTO, ReautorizarDTO, EstablecerCostoRealDTO, IntentarCompletarDTO, EntregarDTO, CancelarDTO
from ...application.mappers import orden_a_dto, cliente_a_dto, vehiculo_a_dto, json_a_crear_orden_dto, json_a_agregar_servicio_dto, json_a_autorizar_dto, json_a_reautorizar_dto, json_a_establecer_costo_real_dto, json_a_intentar_completar_dto, json_a_entregar_dto, json_a_cancelar_dto
from ...infrastructure.repositories import RepositorioOrden, RepositorioClienteSQL, RepositorioVehiculoSQL
from ...domain.exceptions import ErrorDominio
from ...domain.entidades import Cliente, Vehiculo
from ...domain.zona_horaria import ahora
from .dependencies import obtener_action_service, obtener_repositorio, obtener_repositorio_cliente, obtener_repositorio_vehiculo
from .schemas import (
    HealthResponse, CommandsRequest, CommandsResponse, SetStateRequest,
    CreateOrderRequest, AddServiceRequest, SetRealCostRequest, AuthorizeRequest,
    ReauthorizeRequest, CancelRequest, ClienteResponse, CreateClienteRequest,
    UpdateClienteRequest, ListClientesResponse, VehiculoResponse, CreateVehiculoRequest,
    UpdateVehiculoRequest, ListVehiculosResponse
)
from ...infrastructure.logging_config import obtener_logger


logger = obtener_logger("app.drivers.api.routes")

router = APIRouter()

DESC_ORDER_ID = "ID de la orden"
DESC_CUSTOMER_ID = "ID del cliente"

@router.get(
    "/",
    tags=["Health"],
    summary="Información de la API",
    description="Retorna información básica sobre la API y su versión.",
    response_description="Información de la API"
)
def root():
    return {"message": "GestionTalleres API", "version": "1.0.0"}

@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check",
    description="""
    Verifica el estado de la API y la conexión a la base de datos.
    
    Retorna:
    - **status**: Estado general ('ok', 'warning', 'error')
    - **api**: Estado de la API
    - **database**: Estado de la conexión a la BD
    - **tablas**: Lista de tablas existentes
    - **mensaje**: Mensaje adicional si hay problemas
    
    Si alguna tabla esperada no existe, retorna status 'warning' con un mensaje indicando que se debe ejecutar `python init_db.py`.
    """,
    response_description="Estado de la API y base de datos",
    responses={
        200: {
            "description": "API y base de datos operativas",
        },
        503: {
            "description": "Error en la conexión a la base de datos",
        }
    }
)
def health_check():
    estado = {
        "status": "ok",
        "api": "operativa",
        "database": None,
        "tablas": [],
        "tablas_faltantes": []
    }
    
    try:
        from ...infrastructure.db import crear_engine_bd, obtener_url_bd
        from sqlalchemy import inspect, text
        
        url = obtener_url_bd()
        engine = crear_engine_bd(url)
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        
        estado["database"] = "conectada"
        
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        estado["tablas"] = tablas
        
        tablas_esperadas = ["ordenes", "clientes", "vehiculos", "servicios", "componentes", "eventos"]
        tablas_faltantes = [t for t in tablas_esperadas if t not in tablas]
        
        if tablas_faltantes:
            estado["status"] = "warning"
            estado["mensaje"] = f"Base de datos conectada pero faltan tablas: {', '.join(tablas_faltantes)}. Ejecuta: python init_db.py"
            estado["tablas_faltantes"] = tablas_faltantes
        
    except Exception as e:
        estado["status"] = "error"
        estado["database"] = f"error: {str(e)}"
        estado["mensaje"] = "No se pudo conectar a la base de datos. Verifica la configuración en .env"
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=estado)
    
    if estado["status"] != "ok":
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=estado)
    
    return estado


def _formatear_orden_respuesta(orden_dto: OrdenDTO) -> Dict[str, Any]:
    return {
        "order_id": orden_dto.order_id,
        "status": orden_dto.status,
        "customer": orden_dto.customer,
        "vehicle": orden_dto.vehicle,
        "subtotal_estimated": orden_dto.subtotal_estimated,
        "authorized_amount": orden_dto.authorized_amount if orden_dto.authorized_amount else "0.00",
        "real_total": orden_dto.real_total
    }


def _normalizar_comando(comando_raw: dict, idx: int) -> dict:
    comando = comando_raw.copy()
    
    if "op" not in comando or "data" not in comando:
        if "command" in comando:
            op = comando.pop("command")
            comando = {"op": op, "data": comando}
        else:
            error_msg = "Comando debe tener 'op' y 'data' o 'command'"
            logger.error(f"Comando {idx}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    
    return comando


def _procesar_comando_individual(
    comando: dict,
    idx: int,
    action_service: ActionService,
    orders_dict: dict,
    events: list,
    errors: list
) -> None:
    op = comando.get("op")
    
    try:
        orden_dto, eventos_dto, error_dto = action_service.procesar_comando(comando)
        
        if orden_dto:
            order_id = orden_dto.order_id
            if order_id:
                orders_dict[order_id] = _formatear_orden_respuesta(orden_dto)
        
        if error_dto:
            errors.append(error_dto.model_dump())
            logger.warning(f"Comando {idx} ({op}): {error_dto.message}")
        
        events.extend([e.model_dump() for e in eventos_dto])
        
    except Exception:
        logger.error(f"Error procesando comando {idx}: {op}", exc_info=True)
        raise


@router.post(
    "/commands",
    response_model=CommandsResponse,
    status_code=status.HTTP_200_OK,
    tags=["Comandos"],
    summary="Procesar comandos batch",
    name="procesar_comandos",
    description="""
    Procesa un lote de comandos para gestionar órdenes de reparación.
    
    Comandos soportados:
    - **CREATE_ORDER**: Crear una nueva orden
    - **ADD_SERVICE**: Agregar un servicio a una orden
    - **SET_STATE_DIAGNOSED**: Establecer orden como diagnosticada
    - **AUTHORIZE**: Autorizar monto para reparación
    - **SET_STATE_IN_PROGRESS**: Iniciar reparación
    - **SET_REAL_COST**: Establecer costos reales
    - **TRY_COMPLETE**: Intentar completar la orden
    - **REAUTHORIZE**: Reautorizar con nuevo monto
    - **DELIVER**: Entregar orden al cliente
    - **CANCEL**: Cancelar orden
    
    Retorna las órdenes procesadas, eventos generados y errores encontrados.
    """,
    response_description="Resultado del procesamiento de comandos",
    responses={
        200: {
            "description": "Comandos procesados exitosamente",
        },
        400: {
            "description": "Error en el procesamiento de comandos",
        }
    }
)
def procesar_comandos(
    request_body: CommandsRequest,
    action_service: ActionService = Depends(obtener_action_service)
):
    orders_dict = {}
    events = []
    errors = []
    
    for idx, comando_raw in enumerate(request_body.commands, 1):
        comando = _normalizar_comando(comando_raw, idx)
        _procesar_comando_individual(
            comando, idx, action_service,
            orders_dict, events, errors
        )
    
    orders = list(orders_dict.values())
    
    if not isinstance(orders, list):
        orders = list(orders) if orders else []
    if not isinstance(events, list):
        events = list(events) if events else []
    if not isinstance(errors, list):
        errors = list(errors) if errors else []
    
    return CommandsResponse(orders=orders, events=events, errors=errors)


@router.post(
    "/orders",
    response_model=OrdenDTO,
    status_code=status.HTTP_201_CREATED,
    tags=["Ordenes"]
)
def crear_orden(
    request: CreateOrderRequest,
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {
        "customer": request.customer,
        "vehicle": request.vehicle,
        "order_id": request.order_id,
        "ts": request.ts.isoformat() if request.ts else ahora().isoformat()
    }
    dto = json_a_crear_orden_dto(data)
    from ...application.acciones.orden import CrearOrden
    accion = CrearOrden(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.get(
    "/orders/{order_id}",
    response_model=OrdenDTO,
    tags=["Ordenes"],
    summary="Obtener orden por ID",
    description="Consulta una orden de reparación por su ID.",
    response_description="Datos de la orden solicitada",
    responses={
        200: {
            "description": "Orden encontrada",
        },
        404: {
            "description": "Orden no encontrada",
        }
    }
)
def obtener_orden(
    order_id: str = Path(..., description=f"{DESC_ORDER_ID} a consultar", examples=["ORD-12345678"]),
    repo: RepositorioOrden = Depends(obtener_repositorio)
):
    o = repo.obtener(order_id)
    if o is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Orden {order_id} no encontrada")
    
    return orden_a_dto(o)


@router.patch(
    "/orders/{order_id}",
    response_model=OrdenDTO,
    tags=["Ordenes"],
    summary="Actualizar orden",
    description="Actualiza información básica de una orden (cliente y vehículo). Nota: Los estados y servicios se actualizan mediante endpoints específicos.",
    response_description="Orden actualizada",
    responses={
        200: {
            "description": "Orden actualizada exitosamente",
        },
        400: {
            "description": "Error en los datos proporcionados",
        },
        404: {
            "description": "Orden no encontrada",
        }
    }
)
def actualizar_orden(
    order_id: str = Path(..., description=DESC_ORDER_ID, examples=["ORD-12345678"]),
    customer: Optional[str] = Body(None, description="Nombre del cliente"),
    vehicle: Optional[str] = Body(None, description="Descripción del vehículo"),
    repo: RepositorioOrden = Depends(obtener_repositorio)
):
    orden = repo.obtener(order_id)
    if orden is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Orden {order_id} no encontrada")
    
    if customer is not None:
        orden.cliente = customer
    if vehicle is not None:
        orden.vehiculo = vehicle
    
    repo.guardar(orden)
    return orden_a_dto(orden)


@router.post(
    "/orders/{order_id}/set_state",
    response_model=OrdenDTO,
    tags=["Ordenes"],
    summary="Establecer estado de orden"
)
def establecer_estado(
    order_id: str = Path(..., description=DESC_ORDER_ID, examples=["ORD-12345678"]),
    request: SetStateRequest = ...,
    repo: RepositorioOrden = Depends(obtener_repositorio),
    action_service: ActionService = Depends(obtener_action_service)
):
    o = repo.obtener(order_id)
    if o is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Orden {order_id} no encontrada")
    
    from ...application.acciones.estados import EstablecerEstadoDiagnosticado, EstablecerEstadoEnProceso
    from ...application.dtos import EstablecerEstadoDiagnosticadoDTO, EstablecerEstadoEnProcesoTDTO
    
    try:
        if request.state == "DIAGNOSED":
            dto = EstablecerEstadoDiagnosticadoDTO(order_id=order_id)
            action = EstablecerEstadoDiagnosticado(repo, action_service.auditoria)
            orden_dto = action.ejecutar(dto)
        elif request.state == "IN_PROGRESS":
            dto = EstablecerEstadoEnProcesoTDTO(order_id=order_id)
            action = EstablecerEstadoEnProceso(repo, action_service.auditoria)
            orden_dto = action.ejecutar(dto)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estado {request.state} no válido")
        
        return orden_dto
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)




@router.post(
    "/orders/{order_id}/services",
    response_model=OrdenDTO,
    tags=["Ordenes"]
)
def agregar_servicio(
    order_id: str = Path(..., description=DESC_ORDER_ID, examples=["ORD-12345678"]),
    request: AddServiceRequest = ...,
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {
        "order_id": order_id,
        "description": request.description,
        "service": request.service,
        "labor_estimated_cost": request.labor_estimated_cost,
        "components": request.components
    }
    dto = json_a_agregar_servicio_dto(data)
    from ...application.acciones.servicios import AgregarServicio
    accion = AgregarServicio(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post(
    "/orders/{order_id}/authorize",
    response_model=OrdenDTO,
    tags=["Ordenes"]
)
def autorizar_orden(
    order_id: str = Path(..., description=DESC_ORDER_ID, examples=["ORD-12345678"]),
    request: AuthorizeRequest = ...,
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {
        "order_id": order_id,
        "ts": request.ts.isoformat() if request.ts else ahora().isoformat()
    }
    dto = json_a_autorizar_dto(data)
    from ...application.acciones.autorizacion import Autorizar
    accion = Autorizar(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post(
    "/orders/{order_id}/reauthorize",
    response_model=OrdenDTO,
    tags=["Ordenes"],
    summary="Reautorizar orden",
    description="Reautoriza una orden con un nuevo monto cuando el costo real excede el 110% del monto autorizado.",
    response_description="Orden reautorizada",
    responses={
        200: {
            "description": "Orden reautorizada exitosamente",
        },
        400: {
            "description": "Error en la reautorización o monto inválido",
        },
        404: {
            "description": "Orden no encontrada",
        }
    }
)
def reautorizar_orden(
    order_id: str = Path(..., description=DESC_ORDER_ID, examples=["ORD-12345678"]),
    request: ReauthorizeRequest = ...,
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {
        "order_id": order_id,
        "new_authorized_amount": str(request.new_authorized_amount),
        "ts": request.ts.isoformat() if request.ts else ahora().isoformat()
    }
    dto = json_a_reautorizar_dto(data)
    from ...application.acciones.autorizacion import Reautorizar
    accion = Reautorizar(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post(
    "/orders/{order_id}/set_real_cost",
    response_model=OrdenDTO,
    tags=["Ordenes"],
    summary="Establecer costo real",
    description="Establece el costo real de un servicio en una orden.",
    response_description="Orden con costo real actualizado",
    responses={
        200: {
            "description": "Costo real establecido exitosamente",
        },
        400: {
            "description": "Error en los datos o servicio no encontrado",
        },
        404: {
            "description": "Orden no encontrada",
        }
    }
)
def establecer_costo_real(
    order_id: str = Path(..., description=DESC_ORDER_ID, examples=["ORD-12345678"]),
    request: SetRealCostRequest = ...,
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {
        "order_id": order_id,
        "service_id": request.service_id,
        "service_index": request.service_index,
        "real_cost": str(request.real_cost),
        "completed": request.completed,
        "components_real": {k: str(v) for k, v in (request.components_real or {}).items()}
    }
    dto = json_a_establecer_costo_real_dto(data)
    from ...application.acciones.servicios import EstablecerCostoReal
    accion = EstablecerCostoReal(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post(
    "/orders/{order_id}/try_complete",
    response_model=OrdenDTO,
    tags=["Ordenes"]
)
def intentar_completar_orden(
    order_id: str = Path(..., description=DESC_ORDER_ID, examples=["ORD-12345678"]),
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {"order_id": order_id}
    dto = json_a_intentar_completar_dto(data)
    from ...application.acciones.autorizacion import IntentarCompletar
    accion = IntentarCompletar(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post(
    "/orders/{order_id}/deliver",
    response_model=OrdenDTO,
    tags=["Ordenes"],
    summary="Entregar orden",
    description="Marca una orden completada como entregada al cliente.",
    response_description="Orden entregada",
    responses={
        200: {
            "description": "Orden entregada exitosamente",
        },
        400: {
            "description": "Error en la transición de estado",
        },
        404: {
            "description": "Orden no encontrada",
        }
    }
)
def entregar_orden(
    order_id: str = Path(..., description=DESC_ORDER_ID, examples=["ORD-12345678"]),
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {"order_id": order_id}
    dto = json_a_entregar_dto(data)
    from ...application.acciones.orden import EntregarOrden
    accion = EntregarOrden(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post(
    "/orders/{order_id}/cancel",
    response_model=OrdenDTO,
    tags=["Ordenes"],
    summary="Cancelar orden",
    description="Cancela una orden con el motivo especificado.",
    response_description="Orden cancelada",
    responses={
        200: {
            "description": "Orden cancelada exitosamente",
        },
        400: {
            "description": "Error en la cancelación",
        },
        404: {
            "description": "Orden no encontrada",
        }
    }
)
def cancelar_orden(
    order_id: str = Path(..., description=DESC_ORDER_ID, examples=["ORD-12345678"]),
    request: CancelRequest = ...,
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {
        "order_id": order_id,
        "reason": request.reason
    }
    dto = json_a_cancelar_dto(data)
    from ...application.acciones.orden import CancelarOrden
    accion = CancelarOrden(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.get(
    "/customers",
    response_model=ListClientesResponse,
    tags=["Clientes"],
    summary="Listar clientes",
    description="Obtiene la lista de todos los clientes registrados.",
    response_description="Lista de clientes",
    responses={
        200: {
            "description": "Lista de clientes obtenida exitosamente",
        }
    }
)
def listar_clientes(
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    clientes = repo_cliente.listar()
    return ListClientesResponse(clientes=[cliente_a_dto(c) for c in clientes])


@router.get(
    "/customers/{customer_id}",
    response_model=ClienteResponse,
    tags=["Clientes"],
    summary="Obtener cliente por ID",
    description="Obtiene los datos de un cliente específico.",
    response_description="Datos del cliente",
    responses={
        200: {
            "description": "Cliente encontrado",
        },
        404: {
            "description": "Cliente no encontrado",
        }
    }
)
def obtener_cliente(
    customer_id: str = Path(..., description=DESC_CUSTOMER_ID),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    cliente = repo_cliente.obtener(customer_id)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente {customer_id} no encontrado")
    return cliente_a_dto(cliente)


@router.post(
    "/customers",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Clientes"],
    summary="Crear cliente",
    description="Crea un nuevo cliente.",
    response_description="Cliente creado",
    responses={
        201: {
            "description": "Cliente creado exitosamente",
        },
        400: {
            "description": "Error en los datos proporcionados",
        }
    }
)
def crear_cliente(
    request: CreateClienteRequest,
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    cliente = Cliente(nombre=request.nombre)
    repo_cliente.guardar(cliente)
    return cliente_a_dto(cliente)


@router.patch(
    "/customers/{customer_id}",
    response_model=ClienteResponse,
    tags=["Clientes"],
    summary="Actualizar cliente",
    description="Actualiza la información de un cliente existente.",
    response_description="Cliente actualizado",
    responses={
        200: {
            "description": "Cliente actualizado exitosamente",
        },
        404: {
            "description": "Cliente no encontrado",
        }
    }
)
def actualizar_cliente(
    customer_id: str = Path(..., description=DESC_CUSTOMER_ID),
    request: UpdateClienteRequest = ...,
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    cliente = repo_cliente.obtener(customer_id)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente {customer_id} no encontrado")
    
    cliente.nombre = request.nombre
    repo_cliente.guardar(cliente)
    return cliente_a_dto(cliente)


@router.get(
    "/customers/{customer_id}/vehicles",
    response_model=ListVehiculosResponse,
    tags=["Clientes"],
    summary="Obtener vehículos de un cliente",
    description="Obtiene la lista de vehículos asociados a un cliente.",
    response_description="Lista de vehículos del cliente",
    responses={
        200: {
            "description": "Lista de vehículos obtenida exitosamente",
        },
        404: {
            "description": "Cliente no encontrado",
        }
    }
)
def obtener_vehiculos_cliente(
    customer_id: str = Path(..., description=DESC_CUSTOMER_ID),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente),
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo)
):
    cliente = repo_cliente.obtener(customer_id)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente {customer_id} no encontrado")
    
    vehiculos = repo_vehiculo.listar_por_cliente(customer_id)
    return ListVehiculosResponse(vehiculos=[vehiculo_a_dto(v, cliente.nombre) for v in vehiculos])


@router.get(
    "/vehicles",
    response_model=ListVehiculosResponse,
    tags=["Vehiculos"],
    summary="Listar vehículos",
    description="Obtiene la lista de todos los vehículos registrados.",
    response_description="Lista de vehículos",
    responses={
        200: {
            "description": "Lista de vehículos obtenida exitosamente",
        }
    }
)
def listar_vehiculos(
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    vehiculos = repo_vehiculo.listar()
    vehiculos_dto = []
    for v in vehiculos:
        cliente = repo_cliente.obtener(v.id_cliente)
        cliente_nombre = cliente.nombre if cliente else None
        vehiculos_dto.append(vehiculo_a_dto(v, cliente_nombre))
    return ListVehiculosResponse(vehiculos=vehiculos_dto)


@router.get(
    "/vehicles/{vehicle_id}",
    response_model=VehiculoResponse,
    tags=["Vehiculos"],
    summary="Obtener vehículo por ID",
    description="Obtiene los datos de un vehículo específico.",
    response_description="Datos del vehículo",
    responses={
        200: {
            "description": "Vehículo encontrado",
        },
        404: {
            "description": "Vehículo no encontrado",
        }
    }
)
def obtener_vehiculo(
    vehicle_id: str = Path(..., description="ID del vehículo"),
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    vehiculo = repo_vehiculo.obtener(vehicle_id)
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vehículo {vehicle_id} no encontrado")
    
    cliente = repo_cliente.obtener(vehiculo.id_cliente)
    cliente_nombre = cliente.nombre if cliente else None
    return vehiculo_a_dto(vehiculo, cliente_nombre)


@router.post(
    "/vehicles",
    response_model=VehiculoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Vehiculos"],
    summary="Crear vehículo",
    description="Crea un nuevo vehículo asociado a un cliente.",
    response_description="Vehículo creado",
    responses={
        201: {
            "description": "Vehículo creado exitosamente",
        },
        400: {
            "description": "Error en los datos proporcionados",
        },
        404: {
            "description": "Cliente no encontrado",
        }
    }
)
def crear_vehiculo(
    request: CreateVehiculoRequest,
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    cliente = repo_cliente.obtener(request.id_cliente)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente {request.id_cliente} no encontrado")
    
    vehiculo = Vehiculo(
        descripcion=request.descripcion,
        id_cliente=request.id_cliente,
        marca=request.marca,
        modelo=request.modelo,
        anio=request.anio
    )
    repo_vehiculo.guardar(vehiculo)
    return vehiculo_a_dto(vehiculo, cliente.nombre)


@router.patch(
    "/vehicles/{vehicle_id}",
    response_model=VehiculoResponse,
    tags=["Vehiculos"],
    summary="Actualizar vehículo",
    description="Actualiza la información de un vehículo existente.",
    response_description="Vehículo actualizado",
    responses={
        200: {
            "description": "Vehículo actualizado exitosamente",
        },
        404: {
            "description": "Vehículo o cliente no encontrado",
        }
    }
)
def actualizar_vehiculo(
    vehicle_id: str = Path(..., description="ID del vehículo"),
    request: UpdateVehiculoRequest = ...,
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    vehiculo = repo_vehiculo.obtener(vehicle_id)
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vehículo {vehicle_id} no encontrado")
    
    if request.descripcion is not None:
        vehiculo.descripcion = request.descripcion
    if request.marca is not None:
        vehiculo.marca = request.marca
    if request.modelo is not None:
        vehiculo.modelo = request.modelo
    if request.anio is not None:
        vehiculo.anio = request.anio
    if request.id_cliente is not None:
        cliente_nuevo = repo_cliente.obtener(request.id_cliente)
        if not cliente_nuevo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente {request.id_cliente} no encontrado")
        vehiculo.id_cliente = request.id_cliente
    
    repo_vehiculo.guardar(vehiculo)
    
    cliente = repo_cliente.obtener(vehiculo.id_cliente)
    cliente_nombre = cliente.nombre if cliente else None
    return vehiculo_a_dto(vehiculo, cliente_nombre)
