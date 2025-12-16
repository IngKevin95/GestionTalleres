from fastapi import APIRouter, HTTPException, Depends, status, Path, Body, Query
from typing import List, Dict, Any, Optional

from ...application.action_service import ActionService
from ...application.dtos import OrdenDTO, EventoDTO, ErrorDTO, CrearOrdenDTO, AgregarServicioDTO, AutorizarDTO, ReautorizarDTO, EstablecerCostoRealDTO, IntentarCompletarDTO, EntregarDTO, CancelarDTO
from ...application.mappers import orden_a_dto, cliente_a_dto, vehiculo_a_dto, crear_orden_dto, agregar_servicio_dto, autorizar_dto, reautorizar_dto, costo_real_dto, intentar_completar_dto, entregar_dto, cancelar_dto
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
    UpdateVehiculoRequest, ListVehiculosResponse, CustomerIdentifier, VehicleIdentifier
)
from ...infrastructure.logging_config import obtener_logger


logger = obtener_logger("app.drivers.api.routes")

router = APIRouter()


def obtener_cliente_por_criterio(customer: CustomerIdentifier, repo: RepositorioClienteSQL) -> Cliente:
    criterios = sum([1 for v in [customer.id_cliente, customer.identificacion, customer.nombre] if v is not None])
    if criterios != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar exactamente uno de: id_cliente, identificacion o nombre"
        )
    
    cliente = repo.buscar_por_criterio(
        id_cliente=customer.id_cliente,
        identificacion=customer.identificacion,
        nombre=customer.nombre
    )
    
    if not cliente:
        criterio_usado = customer.id_cliente or customer.identificacion or customer.nombre
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente no encontrado con criterio: {criterio_usado}"
        )
    
    return cliente


def obtener_vehiculo_por_criterio(vehicle: VehicleIdentifier, repo: RepositorioVehiculoSQL) -> Vehiculo:
    criterios = sum([1 for v in [vehicle.id_vehiculo, vehicle.placa] if v is not None])
    if criterios != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar exactamente uno de: id_vehiculo o placa"
        )
    
    vehiculo = repo.buscar_por_criterio(
        id_vehiculo=vehicle.id_vehiculo,
        placa=vehicle.placa
    )
    
    if not vehiculo:
        criterio_usado = vehicle.id_vehiculo or vehicle.placa
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo no encontrado con criterio: {criterio_usado}"
        )
    
    return vehiculo

@router.get("/", tags=["Sistema"])
def root():
    return {"message": "GestionTalleres API", "version": "1.0.0"}

@router.get("/health", response_model=HealthResponse, tags=["Sistema"])
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
        
        if orden_dto and orden_dto.order_id:
            orders_dict[orden_dto.order_id] = {
                "order_id": orden_dto.order_id,
                "status": orden_dto.status,
                "customer": orden_dto.customer,
                "vehicle": orden_dto.vehicle,
                "subtotal_estimated": orden_dto.subtotal_estimated,
                "authorized_amount": orden_dto.authorized_amount or "0.00",
                "real_total": orden_dto.real_total
            }
        
        if error_dto:
            errors.append(error_dto.model_dump())
            logger.warning(f"Comando {idx} ({op}): {error_dto.message}")
        
        events.extend([e.model_dump() for e in eventos_dto])
        
    except Exception:
        logger.error(f"Error procesando comando {idx}: {op}", exc_info=True)
        raise


@router.post("/commands", response_model=CommandsResponse, tags=["Comandos"])
def procesar_comandos(
    request_body: CommandsRequest,
    action_service: ActionService = Depends(obtener_action_service)
):
    if not request_body.commands:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'commands' es requerido y no puede estar vacío"
        )
    
    if len(request_body.commands) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 100 comandos por request"
        )
    
    orders_dict = {}
    events = []
    errors = []
    
    sesion = action_service.repo.sesion
    
    for idx, comando_raw in enumerate(request_body.commands, 1):
        comando = _normalizar_comando(comando_raw, idx)
        try:
            _procesar_comando_individual(
                comando, idx, action_service,
                orders_dict, events, errors
            )
            sesion.expire_all()
        except HTTPException:
            sesion.rollback()
            raise
        except Exception as e:
            sesion.rollback()
            logger.error(f"Error inesperado en comando {idx}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error procesando comando {idx}: {str(e)}"
            )
    
    return CommandsResponse(
        orders=list(orders_dict.values()),
        events=events,
        errors=errors
    )


@router.post("/orders", response_model=OrdenDTO, status_code=status.HTTP_201_CREATED, tags=["Órdenes"])
def crear_orden(
    request: CreateOrderRequest,
    action_service: ActionService = Depends(obtener_action_service),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente),
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo)
):
    try:
        data = {
            "customer": request.customer,
            "vehicle": request.vehicle,
            "order_id": request.order_id,
            "ts": request.ts
        }
        dto = crear_orden_dto(data)
        from ...application.acciones.orden import CrearOrden
        accion = CrearOrden(action_service.repo, action_service.auditoria, repo_cliente, repo_vehiculo)
        return accion.ejecutar(dto)
    except (ValueError, ErrorDominio) as e:
        msg = e.mensaje if isinstance(e, ErrorDominio) else str(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


@router.get("/orders/{order_id}", response_model=OrdenDTO, tags=["Órdenes"])
def obtener_orden(
    order_id: str = Path(...),
    repo: RepositorioOrden = Depends(obtener_repositorio)
):
    o = repo.obtener(order_id)
    if o is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Orden {order_id} no encontrada")
    
    return orden_a_dto(o)


@router.patch("/orders/{order_id}", response_model=OrdenDTO, tags=["Órdenes"])
def actualizar_orden(
    order_id: str = Path(...),
    customer: Optional[str] = Body(None),
    vehicle: Optional[str] = Body(None),
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


@router.post("/orders/{order_id}/set_state", response_model=OrdenDTO, tags=["Órdenes"])
def establecer_estado(
    order_id: str = Path(...),
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




@router.post("/orders/{order_id}/services", response_model=OrdenDTO, tags=["Órdenes"])
def agregar_servicio(
    order_id: str = Path(...),
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
    dto = agregar_servicio_dto(data)
    from ...application.acciones.servicios import AgregarServicio
    accion = AgregarServicio(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post("/orders/{order_id}/authorize", response_model=OrdenDTO, tags=["Órdenes"])
def autorizar_orden(
    order_id: str = Path(...),
    request: AuthorizeRequest = ...,
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {
        "order_id": order_id,
        "ts": request.ts.isoformat() if request.ts else ahora().isoformat()
    }
    dto = autorizar_dto(data)
    from ...application.acciones.autorizacion import Autorizar
    accion = Autorizar(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post("/orders/{order_id}/reauthorize", response_model=OrdenDTO, tags=["Órdenes"])
def reautorizar_orden(
    order_id: str = Path(...),
    request: ReauthorizeRequest = ...,
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {
        "order_id": order_id,
        "new_authorized_amount": str(request.new_authorized_amount),
        "ts": request.ts.isoformat() if request.ts else ahora().isoformat()
    }
    dto = reautorizar_dto(data)
    from ...application.acciones.autorizacion import Reautorizar
    accion = Reautorizar(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post("/orders/{order_id}/set_real_cost", response_model=OrdenDTO, tags=["Órdenes"])
def establecer_costo_real(
    order_id: str = Path(...),
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
    dto = costo_real_dto(data)
    from ...application.acciones.servicios import EstablecerCostoReal
    accion = EstablecerCostoReal(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post("/orders/{order_id}/try_complete", response_model=OrdenDTO, tags=["Órdenes"])
def intentar_completar_orden(
    order_id: str = Path(...),
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {"order_id": order_id}
    dto = intentar_completar_dto(data)
    from ...application.acciones.autorizacion import IntentarCompletar
    accion = IntentarCompletar(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post("/orders/{order_id}/deliver", response_model=OrdenDTO, tags=["Órdenes"])
def entregar_orden(
    order_id: str = Path(...),
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {"order_id": order_id}
    dto = entregar_dto(data)
    from ...application.acciones.orden import EntregarOrden
    accion = EntregarOrden(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.post("/orders/{order_id}/cancel", response_model=OrdenDTO, tags=["Órdenes"])
def cancelar_orden(
    order_id: str = Path(...),
    request: CancelRequest = ...,
    action_service: ActionService = Depends(obtener_action_service)
):
    data = {
        "order_id": order_id,
        "reason": request.reason
    }
    dto = cancelar_dto(data)
    from ...application.acciones.orden import CancelarOrden
    accion = CancelarOrden(action_service.repo, action_service.auditoria)
    try:
        return accion.ejecutar(dto)
    except ErrorDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)


@router.get("/customers", tags=["Clientes"])
def obtener_cliente_o_listar(
    id_cliente: Optional[int] = Query(None),
    identificacion: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    # Si no se proporciona ningún criterio, listar todos
    if id_cliente is None and identificacion is None and nombre is None:
        clientes = repo_cliente.listar()
        clientes_response = [
            ClienteResponse(
                id_cliente=c.id_cliente,
                nombre=c.nombre,
                identificacion=c.identificacion,
                correo=c.correo,
                direccion=c.direccion,
                celular=c.celular
            )
            for c in clientes
        ]
        return ListClientesResponse(clientes=clientes_response)
    
    # Si se proporciona al menos un criterio, buscar uno específico
    customer = CustomerIdentifier(id_cliente=id_cliente, identificacion=identificacion, nombre=nombre)
    cliente = obtener_cliente_por_criterio(customer, repo_cliente)
    return ClienteResponse(
        id_cliente=cliente.id_cliente,
        nombre=cliente.nombre,
        identificacion=cliente.identificacion,
        correo=cliente.correo,
        direccion=cliente.direccion,
        celular=cliente.celular
    )


@router.post("/customers", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED, tags=["Clientes"])
def crear_cliente(
    request: CreateClienteRequest,
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    cliente_existente = None
    
    if request.identificacion:
        cliente_existente = repo_cliente.buscar_por_identificacion(request.identificacion)
        if cliente_existente:
            return ClienteResponse(
                id_cliente=cliente_existente.id_cliente,
                nombre=cliente_existente.nombre,
                identificacion=cliente_existente.identificacion,
                correo=cliente_existente.correo,
                direccion=cliente_existente.direccion,
                celular=cliente_existente.celular
            )
    
    if request.nombre:
        cliente_existente = repo_cliente.buscar_por_nombre(request.nombre)
        if cliente_existente:
            return ClienteResponse(
                id_cliente=cliente_existente.id_cliente,
                nombre=cliente_existente.nombre,
                identificacion=cliente_existente.identificacion,
                correo=cliente_existente.correo,
                direccion=cliente_existente.direccion,
                celular=cliente_existente.celular
            )
    
    cliente = Cliente(nombre=request.nombre)
    if request.identificacion:
        cliente.identificacion = request.identificacion
    if request.correo:
        cliente.correo = request.correo
    if request.direccion:
        cliente.direccion = request.direccion
    if request.celular:
        cliente.celular = request.celular
    repo_cliente.guardar(cliente)
    return ClienteResponse(
        id_cliente=cliente.id_cliente,
        nombre=cliente.nombre,
        identificacion=cliente.identificacion,
        correo=cliente.correo,
        direccion=cliente.direccion,
        celular=cliente.celular
    )


@router.patch("/customers", response_model=ClienteResponse, tags=["Clientes"])
def actualizar_cliente(
    id_cliente: Optional[int] = Query(None),
    identificacion: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    request: UpdateClienteRequest = ...,
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    customer = CustomerIdentifier(id_cliente=id_cliente, identificacion=identificacion, nombre=nombre)
    cliente = obtener_cliente_por_criterio(customer, repo_cliente)
    
    if request.nombre is not None:
        cliente.nombre = request.nombre
    if request.identificacion is not None:
        cliente.identificacion = request.identificacion
    if request.correo is not None:
        cliente.correo = request.correo
    if request.direccion is not None:
        cliente.direccion = request.direccion
    if request.celular is not None:
        cliente.celular = request.celular
    repo_cliente.guardar(cliente)
    return ClienteResponse(
        id_cliente=cliente.id_cliente,
        nombre=cliente.nombre,
        identificacion=cliente.identificacion,
        correo=cliente.correo,
        direccion=cliente.direccion,
        celular=cliente.celular
    )


@router.get("/customers/vehicles", response_model=ListVehiculosResponse, tags=["Clientes"])
def obtener_vehiculos_cliente(
    id_cliente: Optional[int] = Query(None),
    identificacion: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente),
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo)
):
    customer = CustomerIdentifier(id_cliente=id_cliente, identificacion=identificacion, nombre=nombre)
    cliente = obtener_cliente_por_criterio(customer, repo_cliente)
    
    vehiculos = repo_vehiculo.listar_por_cliente(cliente.id_cliente)
    vehiculos_response = [
        VehiculoResponse(
            id_vehiculo=v.id_vehiculo,
            placa=v.placa,
            marca=v.marca,
            modelo=v.modelo,
            anio=v.anio,
            kilometraje=v.kilometraje,
            id_cliente=v.id_cliente,
            cliente_nombre=cliente.nombre
        )
        for v in vehiculos
    ]
    return ListVehiculosResponse(vehiculos=vehiculos_response)


@router.get("/vehicles", tags=["Vehículos"])
def obtener_vehiculo_o_listar(
    id_vehiculo: Optional[int] = Query(None),
    placa: Optional[str] = Query(None),
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    # Si no se proporciona ningún criterio, listar todos
    if id_vehiculo is None and placa is None:
        vehiculos = repo_vehiculo.listar()
        vehiculos_response = []
        for v in vehiculos:
            cliente = repo_cliente.obtener(v.id_cliente)
            cliente_nombre = cliente.nombre if cliente else None
            vehiculos_response.append(
                VehiculoResponse(
                    id_vehiculo=v.id_vehiculo,
                    placa=v.placa,
                    marca=v.marca,
                    modelo=v.modelo,
                    anio=v.anio,
                    kilometraje=v.kilometraje,
                    id_cliente=v.id_cliente,
                    cliente_nombre=cliente_nombre
                )
            )
        return ListVehiculosResponse(vehiculos=vehiculos_response)
    
    # Si se proporciona al menos un criterio, buscar uno específico
    vehicle = VehicleIdentifier(id_vehiculo=id_vehiculo, placa=placa)
    vehiculo = obtener_vehiculo_por_criterio(vehicle, repo_vehiculo)
    
    cliente = repo_cliente.obtener(vehiculo.id_cliente)
    cliente_nombre = cliente.nombre if cliente else None
    return VehiculoResponse(
        id_vehiculo=vehiculo.id_vehiculo,
        placa=vehiculo.placa,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        anio=vehiculo.anio,
        kilometraje=vehiculo.kilometraje,
        id_cliente=vehiculo.id_cliente,
        cliente_nombre=cliente_nombre
    )


@router.post("/vehicles", response_model=VehiculoResponse, status_code=status.HTTP_201_CREATED, tags=["Vehículos"])
def crear_vehiculo(
    request: CreateVehiculoRequest,
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    cliente = obtener_cliente_por_criterio(request.customer, repo_cliente)
    
    vehiculo_existente = repo_vehiculo.buscar_por_placa(request.placa)
    if vehiculo_existente:
        cliente_vehiculo = repo_cliente.obtener(vehiculo_existente.id_cliente)
        cliente_nombre = cliente_vehiculo.nombre if cliente_vehiculo else None
        return VehiculoResponse(
            id_vehiculo=vehiculo_existente.id_vehiculo,
            placa=vehiculo_existente.placa,
            marca=vehiculo_existente.marca,
            modelo=vehiculo_existente.modelo,
            anio=vehiculo_existente.anio,
            kilometraje=vehiculo_existente.kilometraje,
            id_cliente=vehiculo_existente.id_cliente,
            cliente_nombre=cliente_nombre
        )
    
    vehiculo = Vehiculo(
        placa=request.placa,
        id_cliente=cliente.id_cliente,
        marca=request.marca,
        modelo=request.modelo,
        anio=request.anio,
        kilometraje=request.kilometraje
    )
    repo_vehiculo.guardar(vehiculo)
    return VehiculoResponse(
        id_vehiculo=vehiculo.id_vehiculo,
        placa=vehiculo.placa,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        anio=vehiculo.anio,
        kilometraje=vehiculo.kilometraje,
        id_cliente=vehiculo.id_cliente,
        cliente_nombre=cliente.nombre
    )


@router.patch("/vehicles", response_model=VehiculoResponse, tags=["Vehículos"])
def actualizar_vehiculo(
    id_vehiculo: Optional[int] = Query(None),
    placa: Optional[str] = Query(None),
    request: UpdateVehiculoRequest = ...,
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    vehicle = VehicleIdentifier(id_vehiculo=id_vehiculo, placa=placa)
    vehiculo = obtener_vehiculo_por_criterio(vehicle, repo_vehiculo)
    
    if request.placa is not None:
        vehiculo.placa = request.placa
    if request.marca is not None:
        vehiculo.marca = request.marca
    if request.modelo is not None:
        vehiculo.modelo = request.modelo
    if request.anio is not None:
        vehiculo.anio = request.anio
    if request.kilometraje is not None:
        vehiculo.kilometraje = request.kilometraje
    if request.customer is not None:
        if isinstance(request.customer, str):
            customer_identifier = CustomerIdentifier(nombre=request.customer)
        else:
            customer_identifier = request.customer
        cliente_nuevo = obtener_cliente_por_criterio(customer_identifier, repo_cliente)
        vehiculo.id_cliente = cliente_nuevo.id_cliente
    
    repo_vehiculo.guardar(vehiculo)
    
    cliente = repo_cliente.obtener(vehiculo.id_cliente)
    cliente_nombre = cliente.nombre if cliente else None
    return VehiculoResponse(
        id_vehiculo=vehiculo.id_vehiculo,
        placa=vehiculo.placa,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        anio=vehiculo.anio,
        kilometraje=vehiculo.kilometraje,
        id_cliente=vehiculo.id_cliente,
        cliente_nombre=cliente_nombre
    )


@router.patch("/vehicles/{vehicle_identifier}", response_model=VehiculoResponse, tags=["Vehículos"])
def actualizar_vehiculo_por_path(
    vehicle_identifier: str = Path(...),
    request: UpdateVehiculoRequest = ...,
    repo_vehiculo: RepositorioVehiculoSQL = Depends(obtener_repositorio_vehiculo),
    repo_cliente: RepositorioClienteSQL = Depends(obtener_repositorio_cliente)
):
    try:
        id_vehiculo = int(vehicle_identifier)
        vehicle = VehicleIdentifier(id_vehiculo=id_vehiculo, placa=None)
    except ValueError:
        vehicle = VehicleIdentifier(id_vehiculo=None, placa=vehicle_identifier)
    
    vehiculo = obtener_vehiculo_por_criterio(vehicle, repo_vehiculo)
    
    if request.placa is not None:
        vehiculo.placa = request.placa
    if request.marca is not None:
        vehiculo.marca = request.marca
    if request.modelo is not None:
        vehiculo.modelo = request.modelo
    if request.anio is not None:
        vehiculo.anio = request.anio
    if request.kilometraje is not None:
        vehiculo.kilometraje = request.kilometraje
    if request.customer is not None:
        if isinstance(request.customer, str):
            customer_identifier = CustomerIdentifier(nombre=request.customer)
        else:
            customer_identifier = request.customer
        cliente_nuevo = obtener_cliente_por_criterio(customer_identifier, repo_cliente)
        vehiculo.id_cliente = cliente_nuevo.id_cliente
    
    repo_vehiculo.guardar(vehiculo)
    
    cliente = repo_cliente.obtener(vehiculo.id_cliente)
    cliente_nombre = cliente.nombre if cliente else None
    return VehiculoResponse(
        id_vehiculo=vehiculo.id_vehiculo,
        placa=vehiculo.placa,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        anio=vehiculo.anio,
        kilometraje=vehiculo.kilometraje,
        id_cliente=vehiculo.id_cliente,
        cliente_nombre=cliente_nombre
    )
