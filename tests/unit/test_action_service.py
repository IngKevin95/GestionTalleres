from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict
from app.application.action_service import ActionService
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


def test_procesar_comando_create_order():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    comando = {
        "op": "CREATE_ORDER",
        "ts": "2025-01-01T10:00:00Z",
        "data": {
            "order_id": "ORD-001",
            "customer": "Juan",
            "vehicle": "Auto"
        }
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert orden_dto.order_id == "ORD-001"
    assert orden_dto.customer == "Juan"
    assert error is None


def test_procesar_comando_add_service():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    repo.guardar(orden)
    
    comando = {
        "op": "ADD_SERVICE",
        "data": {
            "order_id": "ORD-001",
            "service": {
                "description": "Servicio",
                "labor_estimated_cost": "1000.00",
                "components": []
            }
        }
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert len(orden_dto.services) == 1
    assert error is None


def test_procesar_comando_set_state_diagnosed():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    repo.guardar(orden)
    
    comando = {
        "op": "SET_STATE_DIAGNOSED",
        "data": {"order_id": "ORD-001"}
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert orden_dto.status == "DIAGNOSED"
    assert error is None


def test_procesar_comando_authorize():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.DIAGNOSED
    from app.domain.entidades import Servicio
    orden.servicios.append(Servicio("Servicio", Decimal("1000.00")))
    repo.guardar(orden)
    
    comando = {
        "op": "AUTHORIZE",
        "ts": "2025-01-01T10:00:00Z",
        "data": {"order_id": "ORD-001"}
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert orden_dto.status == "AUTHORIZED"
    assert orden_dto.authorized_amount is not None
    assert error is None


def test_procesar_comando_set_state_in_progress():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.AUTHORIZED
    orden.monto_autorizado = Decimal("1160.00")
    repo.guardar(orden)
    
    comando = {
        "op": "SET_STATE_IN_PROGRESS",
        "data": {"order_id": "ORD-001"}
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert orden_dto.status == "IN_PROGRESS"
    assert error is None


def test_procesar_comando_set_real_cost():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    from app.domain.entidades import Servicio
    servicio = Servicio("Servicio", Decimal("1000.00"))
    orden.servicios.append(servicio)
    repo.guardar(orden)
    
    comando = {
        "op": "SET_REAL_COST",
        "data": {
            "order_id": "ORD-001",
            "service_id": servicio.id_servicio,
            "real_cost": "1200.00",
            "completed": True
        }
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert error is None


def test_procesar_comando_try_complete():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.IN_PROGRESS
    orden.monto_autorizado = Decimal("1160.00")
    from app.domain.entidades import Servicio
    servicio = Servicio("Servicio", Decimal("1000.00"))
    servicio.completado = True
    servicio.costo_real = Decimal("1000.00")
    orden.servicios.append(servicio)
    repo.guardar(orden)
    
    comando = {
        "op": "TRY_COMPLETE",
        "data": {"order_id": "ORD-001"}
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert orden_dto.status == "COMPLETED"
    assert error is None


def test_procesar_comando_reauthorize():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.WAITING_FOR_APPROVAL
    orden.monto_autorizado = Decimal("1160.00")
    orden.total_real = Decimal("1300.00")
    repo.guardar(orden)
    
    comando = {
        "op": "REAUTHORIZE",
        "ts": "2025-01-01T10:00:00Z",
        "data": {
            "order_id": "ORD-001",
            "new_authorized_amount": "1500.00"
        }
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert orden_dto.status == "AUTHORIZED"
    assert error is None


def test_procesar_comando_deliver():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.COMPLETED
    repo.guardar(orden)
    
    comando = {
        "op": "DELIVER",
        "data": {"order_id": "ORD-001"}
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert orden_dto.status == "DELIVERED"
    assert error is None


def test_procesar_comando_cancel():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    repo.guardar(orden)
    
    comando = {
        "op": "CANCEL",
        "data": {
            "order_id": "ORD-001",
            "reason": "Cliente canceló"
        }
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert orden_dto.status == "CANCELLED"
    assert error is None


def test_procesar_comando_operacion_desconocida():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    comando = {
        "op": "OPERACION_INVALIDA",
        "data": {"order_id": "ORD-001"}
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is None
    assert error is not None
    assert error.code == "INVALID_OPERATION"


def test_procesar_comando_error_dominio():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    comando = {
        "op": "ADD_SERVICE",
        "data": {
            "order_id": "ORD-999",
            "service": {
                "description": "Servicio",
                "labor_estimated_cost": "1000.00",
                "components": []
            }
        }
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is None
    assert error is not None
    assert error.code == CodigoError.ORDER_NOT_FOUND.value


def test_procesar_comando_error_requires_reauth():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    service = ActionService(repo, audit)
    
    orden = Orden("ORD-001", "Juan", "Auto", datetime.utcnow())
    orden.estado = EstadoOrden.IN_PROGRESS
    orden.monto_autorizado = Decimal("1160.00")
    from app.domain.entidades import Servicio
    servicio = Servicio("Servicio", Decimal("1000.00"))
    servicio.completado = True
    limite = Decimal("1160.00") * Decimal("1.10")
    servicio.costo_real = limite + Decimal("100.00")
    orden.servicios.append(servicio)
    repo.guardar(orden)
    
    comando = {
        "op": "TRY_COMPLETE",
        "data": {"order_id": "ORD-001"}
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is not None
    assert error is not None
    assert error.code == CodigoError.REQUIRES_REAUTH.value
    assert orden_dto.status == "WAITING_FOR_APPROVAL"


def test_procesar_comando_error_inesperado():
    repo = RepositorioOrdenMock()
    audit = AlmacenEventosMock()
    
    class RepoRoto(RepositorioOrden):
        def obtener(self, id_orden: str):
            if id_orden == "ORD-001":
                return None
            raise Exception("Error inesperado")
        def guardar(self, orden: Orden):
            raise Exception("Error al guardar")
    
    service = ActionService(RepoRoto(), audit)
    
    comando = {
        "op": "CREATE_ORDER",
        "data": {"order_id": "ORD-001", "customer": "Juan", "vehicle": "Auto"}
    }
    
    orden_dto, eventos, error = service.procesar_comando(comando)
    assert orden_dto is None
    assert error is not None
    assert error.code == "INTERNAL_ERROR"

