from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from ..enums import EstadoOrden, CodigoError
from ..exceptions import ErrorDominio
from ..dinero import redondear_mitad_par
from ..zona_horaria import ahora
from .service import Servicio
from .event import Evento


class Orden:
    def __init__(self, order_id: str, cliente: str, vehiculo: str, fecha_creacion: datetime, id: Optional[int] = None):
        self.id = id
        self.order_id = order_id
        self.cliente = cliente
        self.vehiculo = vehiculo
        self.estado = EstadoOrden.CREATED
        self.servicios: List[Servicio] = []
        self.eventos: List[Evento] = []
        self.monto_autorizado: Optional[Decimal] = None
        self.version_autorizacion = 0
        self.total_real = Decimal('0')
        self.fecha_creacion = fecha_creacion
        self.fecha_cancelacion: Optional[datetime] = None

    def _validar_no_cancelada(self):
        if self.estado == EstadoOrden.CANCELLED:
            raise ErrorDominio(CodigoError.ORDER_CANCELLED, "La orden está cancelada")

    def _agregar_evento(self, tipo: str, metadatos: dict = None):
        evento = Evento(tipo, ahora(), metadatos or {})
        self.eventos.append(evento)

    def agregar_servicio(self, servicio: Servicio):
        self._validar_no_cancelada()
        
        if self.estado not in [EstadoOrden.CREATED, EstadoOrden.DIAGNOSED]:
            raise ErrorDominio(
                CodigoError.NOT_ALLOWED_AFTER_AUTHORIZATION,
                "No se pueden agregar servicios después de autorizar"
            )
        
        self.servicios.append(servicio)

    def establecer_estado_diagnosticado(self):
        if self.estado == EstadoOrden.CANCELLED:
            raise ErrorDominio(CodigoError.ORDER_CANCELLED, "La orden está cancelada")
        
        if self.estado != EstadoOrden.CREATED:
            raise ErrorDominio(CodigoError.SEQUENCE_ERROR, "Estado debe ser CREATED")
        
        self.estado = EstadoOrden.DIAGNOSED
        self._agregar_evento("DIAGNOSED")

    def autorizar(self, monto: Decimal):
        if self.estado == EstadoOrden.CANCELLED:
            raise ErrorDominio(CodigoError.ORDER_CANCELLED, "La orden está cancelada")
        
        if self.estado != EstadoOrden.DIAGNOSED:
            raise ErrorDominio(CodigoError.SEQUENCE_ERROR, "Requiere estado DIAGNOSED")
        
        if not self.servicios:
            raise ErrorDominio(CodigoError.NO_SERVICES, "No hay servicios")
        
        self.monto_autorizado = redondear_mitad_par(monto, 2)
        self.version_autorizacion = 1
        self.estado = EstadoOrden.AUTHORIZED
        evt_data = {"monto": str(self.monto_autorizado), "version": self.version_autorizacion}
        self._agregar_evento("AUTHORIZED", evt_data)

    def establecer_estado_en_proceso(self):
        if self.estado == EstadoOrden.CANCELLED:
            raise ErrorDominio(CodigoError.ORDER_CANCELLED, "La orden está cancelada")
        
        if self.estado != EstadoOrden.AUTHORIZED:
            raise ErrorDominio(CodigoError.SEQUENCE_ERROR, "Requiere estado AUTHORIZED")
        
        self.estado = EstadoOrden.IN_PROGRESS
        self._agregar_evento("IN_PROGRESS")

    def establecer_costo_real(self, servicio_id: int, costo_real: Decimal, componentes_reales: dict = None):
        if self.estado == EstadoOrden.CANCELLED:
            raise ErrorDominio(CodigoError.ORDER_CANCELLED, "La orden está cancelada")
        
        # Buscar servicio por ID
        servicio = None
        for s in self.servicios:
            if s.id_servicio == servicio_id:
                servicio = s
                break
        
        if servicio is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, "Servicio no encontrado")
        
        if componentes_reales:
            servicio.costo_real = costo_real
            for comp_id, costo in componentes_reales.items():
                for c in servicio.componentes:
                    if c.id_componente == comp_id:
                        c.costo_real = costo
                        break
        else:
            servicio.costo_real = costo_real
            for c in servicio.componentes:
                c.costo_real = None
        
        self._recalcular_total_real()

    def _recalcular_total_real(self):
        # Recalcular sumando costos reales de todos los servicios
        self.total_real = sum(servicio.calcular_costo_real() for servicio in self.servicios)

    def intentar_completar(self):
        if self.estado == EstadoOrden.CANCELLED:
            raise ErrorDominio(CodigoError.ORDER_CANCELLED, "La orden está cancelada")
        
        if self.estado != EstadoOrden.IN_PROGRESS:
            raise ErrorDominio(CodigoError.SEQUENCE_ERROR, "Debe estar en IN_PROGRESS")
        
        if self.monto_autorizado is None:
            raise ErrorDominio(CodigoError.SEQUENCE_ERROR, "Orden no autorizada")
        
        if not self.servicios:
            raise ErrorDominio(CodigoError.NO_SERVICES, "No hay servicios")
        
        for s in self.servicios:
            if not s.completado:
                raise ErrorDominio(CodigoError.INVALID_OPERATION, "Faltan servicios por completar")
        
        self._recalcular_total_real()
        limite = redondear_mitad_par(self.monto_autorizado * Decimal('1.10'), 2)
        
        if self.total_real > limite:
            self.estado = EstadoOrden.WAITING_FOR_APPROVAL
            self._agregar_evento("WAITING_FOR_APPROVAL", {
                "total_real": str(self.total_real),
                "limite": str(limite)
            })
            raise ErrorDominio(
                CodigoError.REQUIRES_REAUTH,
                f"El costo real ({self.total_real:.2f}) excede el 110% del monto autorizado ({self.monto_autorizado:.2f}). Límite: {limite:.2f}."
            )
        
        self.estado = EstadoOrden.COMPLETED
        self._agregar_evento("COMPLETED")

    def reautorizar(self, nuevo_monto: Decimal):
        if self.estado == EstadoOrden.CANCELLED:
            raise ErrorDominio(CodigoError.ORDER_CANCELLED, "La orden está cancelada")
        
        if self.estado != EstadoOrden.WAITING_FOR_APPROVAL:
            raise ErrorDominio(CodigoError.SEQUENCE_ERROR, "Requiere WAITING_FOR_APPROVAL")
        
        if nuevo_monto < self.total_real:
            raise ErrorDominio(
                CodigoError.INVALID_AMOUNT,
                f"Monto {nuevo_monto} menor que total real {self.total_real}"
            )
        
        self.version_autorizacion += 1
        self.monto_autorizado = redondear_mitad_par(nuevo_monto, 2)
        self.estado = EstadoOrden.AUTHORIZED
        meta = {"monto": str(self.monto_autorizado), "version": self.version_autorizacion}
        self._agregar_evento("REAUTHORIZED", meta)

    def entregar(self):
        if self.estado == EstadoOrden.CANCELLED:
            raise ErrorDominio(CodigoError.ORDER_CANCELLED, "La orden está cancelada")
        
        if self.estado != EstadoOrden.COMPLETED:
            raise ErrorDominio(CodigoError.SEQUENCE_ERROR, "Debe estar COMPLETED")
        
        self.estado = EstadoOrden.DELIVERED
        self._agregar_evento("DELIVERED")

    def cancelar(self, motivo: str):
        if self.estado == EstadoOrden.CANCELLED:
            raise ErrorDominio(CodigoError.ORDER_CANCELLED, "La orden ya está cancelada")
        
        self.estado = EstadoOrden.CANCELLED
        self.fecha_cancelacion = ahora()
        self._agregar_evento("CANCELLED", {"motivo": motivo})

