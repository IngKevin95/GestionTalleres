from typing import Optional
from sqlalchemy.orm import Session

from ...domain.entidades import Orden
from ...domain.enums import EstadoOrden
from ...domain.dinero import a_decimal
from ...application.ports import RepositorioOrden as IRepositorioOrden
from ..models.orden_model import OrdenModel
from .repositorio_servicio import RepositorioServicioSQL
from .repositorio_evento import RepositorioEventoSQL
from .repositorio_cliente import RepositorioClienteSQL
from .repositorio_vehiculo import RepositorioVehiculoSQL
from ..logging_config import obtener_logger


logger = obtener_logger("app.infrastructure.repositories.repositorio_orden")


class RepositorioOrden(IRepositorioOrden):
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.repo_servicio = RepositorioServicioSQL(sesion)
        self.repo_evento = RepositorioEventoSQL(sesion)
        self.repo_cliente = RepositorioClienteSQL(sesion)
        self.repo_vehiculo = RepositorioVehiculoSQL(sesion)
    
    def obtener(self, id_orden: str) -> Optional[Orden]:
        m = self.sesion.query(OrdenModel).filter(OrdenModel.id_orden == id_orden).first()
        if m is None:
            return None
        
        self.sesion.expire_all()
        return self._deserializar(m)
    
    def guardar(self, orden: Orden) -> None:
        cliente = self.repo_cliente.buscar_o_crear_por_nombre(orden.cliente)
        vehiculo = self.repo_vehiculo.buscar_o_crear_por_descripcion(orden.vehiculo, cliente.id_cliente)
        
        modelo = self.sesion.query(OrdenModel).filter(OrdenModel.id_orden == orden.id_orden).first()
        
        if modelo:
            self._actualizar_modelo(modelo, orden, cliente.id_cliente, vehiculo.id_vehiculo)
        else:
            modelo = self._serializar(orden, cliente.id_cliente, vehiculo.id_vehiculo)
            self.sesion.add(modelo)
        
        self.sesion.flush()
        self.repo_servicio.guardar_servicios(modelo.id_orden, orden.servicios, modelo.servicios)
        self.repo_evento.guardar_eventos(modelo.id_orden, orden.eventos, modelo.eventos)
        self.sesion.commit()
        
    
    def _serializar(self, orden: Orden, id_cliente: str, id_vehiculo: str) -> OrdenModel:
        monto_str = str(orden.monto_autorizado) if orden.monto_autorizado else None
        return OrdenModel(
            id_orden=orden.id_orden,
            id_cliente=id_cliente,
            id_vehiculo=id_vehiculo,
            estado=orden.estado.value,
            monto_autorizado=monto_str,
            version_autorizacion=orden.version_autorizacion,
            total_real=str(orden.total_real),
            fecha_creacion=orden.fecha_creacion,
            fecha_cancelacion=orden.fecha_cancelacion
        )
    
    def _actualizar_modelo(self, m: OrdenModel, orden: Orden, id_cliente: str, id_vehiculo: str) -> None:
        m.id_cliente = id_cliente
        m.id_vehiculo = id_vehiculo
        m.estado = orden.estado.value
        m.monto_autorizado = str(orden.monto_autorizado) if orden.monto_autorizado else None
        m.version_autorizacion = orden.version_autorizacion
        m.total_real = str(orden.total_real)
        m.fecha_cancelacion = orden.fecha_cancelacion
    
    def _deserializar(self, m: OrdenModel) -> Orden:
        servicios = self.repo_servicio.deserializar_servicios(m.servicios)
        eventos = self.repo_evento.deserializar_eventos(m.eventos)
        
        cliente_nombre = m.cliente.nombre if m.cliente else ""
        vehiculo_desc = m.vehiculo.descripcion if m.vehiculo else ""
        
        orden = Orden(
            id_orden=m.id_orden,
            cliente=cliente_nombre,
            vehiculo=vehiculo_desc,
            fecha_creacion=m.fecha_creacion
        )
        orden.estado = EstadoOrden(m.estado)
        orden.servicios = servicios
        orden.eventos = eventos
        orden.monto_autorizado = a_decimal(m.monto_autorizado) if m.monto_autorizado else None
        orden.version_autorizacion = m.version_autorizacion
        orden.total_real = a_decimal(m.total_real)
        orden.fecha_cancelacion = m.fecha_cancelacion
        
        return orden
