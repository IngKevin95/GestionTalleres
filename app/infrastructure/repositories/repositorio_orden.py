from typing import Optional
from sqlalchemy.orm import Session

from ...domain.entidades import Orden
from ...domain.enums import EstadoOrden
from ...domain.dinero import a_decimal
from ...application.ports import RepositorioOrden as IRepositorioOrden, UnidadTrabajo
from ..models.orden_model import OrdenModel
from .repositorio_servicio import RepositorioServicioSQL
from .repositorio_evento import RepositorioEventoSQL
from .repositorio_cliente import RepositorioClienteSQL
from .repositorio_vehiculo import RepositorioVehiculoSQL
from .unidad_trabajo import UnidadTrabajoSQL
from ..logging_config import obtener_logger


logger = obtener_logger("app.infrastructure.repositories.repositorio_orden")


class RepositorioOrden(IRepositorioOrden):
    def __init__(self, sesion: Session, unidad_trabajo: Optional[UnidadTrabajo] = None):
        self.sesion = sesion
        if unidad_trabajo is None:
            unidad_trabajo = UnidadTrabajoSQL(sesion)
        self.unidad_trabajo = unidad_trabajo
    
    def _obtener_repo_cliente(self) -> RepositorioClienteSQL:
        return self.unidad_trabajo.obtener_repositorio_cliente()
    
    def _obtener_repo_vehiculo(self) -> RepositorioVehiculoSQL:
        return self.unidad_trabajo.obtener_repositorio_vehiculo()
    
    def _obtener_repo_servicio(self) -> RepositorioServicioSQL:
        return self.unidad_trabajo.obtener_repositorio_servicio()
    
    def _obtener_repo_evento(self) -> RepositorioEventoSQL:
        return self.unidad_trabajo.obtener_repositorio_evento()
    
    def obtener(self, order_id: str) -> Optional[Orden]:
        modelo = self.sesion.query(OrdenModel).filter(OrdenModel.order_id == order_id).first()
        if modelo is None:
            return None
        
        self.sesion.expire_all()
        return self._deserializar(modelo)
    
    def _obtener_o_crear_cliente_vehiculo(self, orden: Orden) -> tuple:
        """Obtiene o crea cliente y vehículo, retorna sus IDs."""
        repo_cliente = self._obtener_repo_cliente()
        repo_vehiculo = self._obtener_repo_vehiculo()
        cliente = repo_cliente.buscar_o_crear_por_nombre(orden.cliente)
        vehiculo = repo_vehiculo.buscar_o_crear_por_placa(orden.vehiculo, cliente.id_cliente)
        return cliente.id_cliente, vehiculo.id_vehiculo
    
    def _validar_ids_orden(self, orden: Orden, modelo: OrdenModel) -> None:
        """Valida que los IDs de la orden sean consistentes."""
        if orden.id is not None and modelo.id != orden.id:
            raise ValueError(f"order_id '{orden.order_id}' ya existe con un id diferente")
    
    def _validar_id_nuevo(self, orden: Orden) -> None:
        """Valida que el ID de una orden nueva no exista ya."""
        if orden.id is not None:
            modelo_existente = self.sesion.query(OrdenModel).filter(OrdenModel.id == orden.id).first()
            if modelo_existente:
                raise ValueError(f"Ya existe una orden con id {orden.id}")
    
    def _guardar_entidades_relacionadas(self, modelo_id: int, orden: Orden, modelo: OrdenModel) -> None:
        """Guarda servicios y eventos relacionados con la orden."""
        repo_servicio = self._obtener_repo_servicio()
        repo_evento = self._obtener_repo_evento()
        repo_servicio.guardar_servicios(modelo_id, orden.servicios, modelo.servicios)
        repo_evento.guardar_eventos(modelo_id, orden.eventos, modelo.eventos)
    
    def guardar(self, orden: Orden) -> None:
        try:
            id_cliente, id_vehiculo = self._obtener_o_crear_cliente_vehiculo(orden)
            
            modelo = self.sesion.query(OrdenModel).filter(OrdenModel.order_id == orden.order_id).first()
            
            if modelo:
                self._validar_ids_orden(orden, modelo)
                try:
                    self.sesion.refresh(modelo)
                except Exception:
                    modelo = self.sesion.query(OrdenModel).filter(OrdenModel.order_id == orden.order_id).first()
                    if not modelo:
                        raise ValueError(f"Orden {orden.order_id} no encontrada después de rollback")
                self._actualizar_modelo(modelo, orden, id_cliente, id_vehiculo)
                orden.id = modelo.id
            else:
                self._validar_id_nuevo(orden)
                modelo = self._serializar(orden, id_cliente, id_vehiculo)
                self.sesion.add(modelo)
                self.sesion.flush()
                orden.id = modelo.id
            
            self._guardar_entidades_relacionadas(modelo.id, orden, modelo)
            self.sesion.commit()
        except Exception:
            self.sesion.rollback()
            raise
        
    
    def _serializar(self, orden: Orden, id_cliente: int, id_vehiculo: int) -> OrdenModel:
        monto_str = str(orden.monto_autorizado) if orden.monto_autorizado else None
        return OrdenModel(
            id=orden.id,
            order_id=orden.order_id,
            id_cliente=id_cliente,
            id_vehiculo=id_vehiculo,
            estado=orden.estado.value,
            monto_autorizado=monto_str,
            version_autorizacion=orden.version_autorizacion,
            total_real=str(orden.total_real),
            fecha_creacion=orden.fecha_creacion,
            fecha_cancelacion=orden.fecha_cancelacion
        )
    
    def _actualizar_modelo(self, modelo: OrdenModel, orden: Orden, id_cliente: int, id_vehiculo: int) -> None:
        modelo.id_cliente = id_cliente
        modelo.id_vehiculo = id_vehiculo
        modelo.estado = orden.estado.value
        modelo.monto_autorizado = str(orden.monto_autorizado) if orden.monto_autorizado else None
        modelo.version_autorizacion = orden.version_autorizacion
        modelo.total_real = str(orden.total_real)
        modelo.fecha_cancelacion = orden.fecha_cancelacion
    
    def _deserializar(self, modelo: OrdenModel) -> Orden:
        repo_servicio = self._obtener_repo_servicio()
        repo_evento = self._obtener_repo_evento()
        servicios = repo_servicio.deserializar_servicios(modelo.servicios)
        eventos = repo_evento.deserializar_eventos(modelo.eventos)
        
        cliente_nombre = modelo.cliente.nombre if modelo.cliente else ""
        vehiculo_placa = modelo.vehiculo.placa if modelo.vehiculo else ""
        
        orden = Orden(
            order_id=modelo.order_id,
            cliente=cliente_nombre,
            vehiculo=vehiculo_placa,
            fecha_creacion=modelo.fecha_creacion,
            id=modelo.id
        )
        orden.estado = EstadoOrden(modelo.estado)
        orden.servicios = servicios
        orden.eventos = eventos
        orden.monto_autorizado = a_decimal(modelo.monto_autorizado) if modelo.monto_autorizado else None
        orden.version_autorizacion = modelo.version_autorizacion
        orden.total_real = a_decimal(modelo.total_real)
        orden.fecha_cancelacion = modelo.fecha_cancelacion
        
        return orden
