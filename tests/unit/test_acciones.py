from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict
from app.application.acciones import (
    CrearOrden, AgregarServicio, EstablecerEstadoDiagnosticado,
    Autorizar, EstablecerEstadoEnProceso, IntentarCompletar,
    Reautorizar, EntregarOrden, CancelarOrden
)
from app.application.dtos import (
    CrearOrdenDTO, AgregarServicioDTO, EstablecerEstadoDiagnosticadoDTO,
    AutorizarDTO, EstablecerEstadoEnProcesoTDTO, IntentarCompletarDTO,
    ReautorizarDTO, EntregarDTO, CancelarDTO
)
from app.application.ports import RepositorioOrden, AlmacenEventos
from app.domain.entidades import Orden, Evento
from app.domain.exceptions import ErrorDominio
from app.domain.enums import CodigoError, EstadoOrden


class RepositorioOrdenMock(RepositorioOrden):
    def __init__(self):
        self._ordenes: Dict[str, Orden] = {}
    
    def obtener(self, id_orden: str) -> Optional[Orden]:
        return self._ordenes.get(id_orden)
    
    def guardar(self, orden: Orden) -> None:
        self._ordenes[orden.id_orden] = orden


class AlmacenEventosMock(AlmacenEventos):
    def __init__(self):
        self.eventos_registrados = []
    
    def registrar(self, evento: Evento) -> None:
        self.eventos_registrados.append(evento)


def crear_fixtures():
    repo = RepositorioOrdenMock()
    auditoria = AlmacenEventosMock()
    return repo, auditoria


def test_crear_orden():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    accion = CrearOrden(repo, audit)
    
    dto = CrearOrdenDTO(
        cliente="Juan Pérez",
        vehiculo="Toyota Corolla",
        timestamp=datetime.utcnow()
    )
    
    resultado = accion.ejecutar(dto)
    assert resultado.status == "CREATED"
    assert resultado.customer == "Juan Pérez"
    
    orden = repo.obtener(resultado.order_id)
    assert orden is not None


def test_agregar_servicio():
    repo, auditoria = crear_fixtures()
    
    crear = CrearOrden(repo, auditoria)
    orden_dto = crear.ejecutar(CrearOrdenDTO(
        cliente="Juan", vehiculo="Auto", timestamp=datetime.utcnow()
    ))
    
    agregar = AgregarServicio(repo, auditoria)
    servicio_dto = AgregarServicioDTO(
        order_id=orden_dto.order_id,
        descripcion="Cambio de aceite",
        costo_mano_obra=Decimal("500.00"),
        componentes=[{"description": "Aceite", "estimated_cost": "300.00"}]
    )
    
    resultado = agregar.ejecutar(servicio_dto)
    assert len(resultado.services) == 1


def test_autorizar():
    r = RepositorioOrdenMock()
    a = AlmacenEventosMock()
    
    crear = CrearOrden(r, a)
    orden_dto = crear.ejecutar(CrearOrdenDTO(
        cliente="Juan", vehiculo="Auto", timestamp=datetime.utcnow()
    ))
    
    agregar = AgregarServicio(r, a)
    agregar.ejecutar(AgregarServicioDTO(
        order_id=orden_dto.order_id,
        descripcion="Servicio",
        costo_mano_obra=Decimal("1000.00"),
        componentes=[]
    ))
    
    diagnosticar = EstablecerEstadoDiagnosticado(r, a)
    diagnosticar.ejecutar(EstablecerEstadoDiagnosticadoDTO(order_id=orden_dto.order_id))
    
    autorizar = Autorizar(r, a)
    resultado = autorizar.ejecutar(AutorizarDTO(
        order_id=orden_dto.order_id,
        timestamp=datetime.utcnow()
    ))
    
    assert resultado.status == "AUTHORIZED"
    assert resultado.authorized_amount is not None


def test_intentar_completar_excede_110():
    repo, auditoria = crear_fixtures()
    
    crear = CrearOrden(repo, auditoria)
    orden_dto = crear.ejecutar(CrearOrdenDTO(
        cliente="Juan", vehiculo="Auto", timestamp=datetime.utcnow()
    ))
    
    agregar = AgregarServicio(repo, auditoria)
    agregar.ejecutar(AgregarServicioDTO(
        order_id=orden_dto.order_id,
        descripcion="Servicio",
        costo_mano_obra=Decimal("10000.00"),
        componentes=[]
    ))
    
    diagnosticar = EstablecerEstadoDiagnosticado(repo, auditoria)
    diagnosticar.ejecutar(EstablecerEstadoDiagnosticadoDTO(order_id=orden_dto.order_id))
    
    autorizar = Autorizar(repo, auditoria)
    autorizar.ejecutar(AutorizarDTO(order_id=orden_dto.order_id, timestamp=datetime.utcnow()))
    
    en_proceso = EstablecerEstadoEnProceso(repo, auditoria)
    en_proceso.ejecutar(EstablecerEstadoEnProcesoTDTO(order_id=orden_dto.order_id))
    
    orden = repo.obtener(orden_dto.order_id)
    monto_autorizado = orden.monto_autorizado
    limite_110 = monto_autorizado * Decimal("1.10")
    costo_que_excede = limite_110 + Decimal("100.00")
    
    orden.servicios[0].costo_real = costo_que_excede
    orden.servicios[0].completado = True
    repo.guardar(orden)
    
    completar = IntentarCompletar(repo, auditoria)
    try:
        completar.ejecutar(IntentarCompletarDTO(order_id=orden_dto.order_id))
        assert False, "Debe lanzar error"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.REQUIRES_REAUTH
        
        orden = repo.obtener(orden_dto.order_id)
        assert orden.estado == EstadoOrden.WAITING_FOR_APPROVAL


def test_intentar_completar_sin_servicios_completados():
    repo, auditoria = crear_fixtures()
    
    crear = CrearOrden(repo, auditoria)
    orden_dto = crear.ejecutar(CrearOrdenDTO(
        cliente="Juan", vehiculo="Auto", timestamp=datetime.utcnow()
    ))
    
    agregar = AgregarServicio(repo, auditoria)
    agregar.ejecutar(AgregarServicioDTO(
        order_id=orden_dto.order_id,
        descripcion="Servicio 1",
        costo_mano_obra=Decimal("1000.00"),
        componentes=[]
    ))
    
    agregar.ejecutar(AgregarServicioDTO(
        order_id=orden_dto.order_id,
        descripcion="Servicio 2",
        costo_mano_obra=Decimal("2000.00"),
        componentes=[]
    ))
    
    diagnosticar = EstablecerEstadoDiagnosticado(repo, auditoria)
    diagnosticar.ejecutar(EstablecerEstadoDiagnosticadoDTO(order_id=orden_dto.order_id))
    
    autorizar = Autorizar(repo, auditoria)
    autorizar.ejecutar(AutorizarDTO(order_id=orden_dto.order_id, timestamp=datetime.utcnow()))
    
    en_proceso = EstablecerEstadoEnProceso(repo, auditoria)
    en_proceso.ejecutar(EstablecerEstadoEnProcesoTDTO(order_id=orden_dto.order_id))
    
    orden = repo.obtener(orden_dto.order_id)
    orden.servicios[0].completado = True
    orden.servicios[1].completado = False
    orden.servicios[0].costo_real = Decimal("1000.00")
    orden.servicios[1].costo_real = Decimal("2000.00")
    repo.guardar(orden)
    
    completar = IntentarCompletar(repo, auditoria)
    try:
        completar.ejecutar(IntentarCompletarDTO(order_id=orden_dto.order_id))
        assert False, "Debe lanzar error por servicios no completados"
    except ErrorDominio as e:
        assert e.codigo == CodigoError.INVALID_OPERATION
        assert "completar" in e.mensaje.lower()
        
        orden = repo.obtener(orden_dto.order_id)
        assert orden.estado == EstadoOrden.IN_PROGRESS

