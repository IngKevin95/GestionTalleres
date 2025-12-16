from datetime import datetime
from typing import Optional

from ...domain.entidades import Orden, Evento
from ...domain.exceptions import ErrorDominio
from ...domain.enums import CodigoError
from ...domain.zona_horaria import ahora
from .base import AccionBase
from ..dtos import CrearOrdenDTO, CancelarDTO, EntregarDTO, OrdenDTO
from ..mappers import orden_a_dto


class CrearOrden(AccionBase):
    def __init__(self, repo, auditoria, repo_cliente=None, repo_vehiculo=None):
        super().__init__(repo, auditoria)
        self.repo_cliente = repo_cliente
        self.repo_vehiculo = repo_vehiculo
    
    def ejecutar(self, dto: CrearOrdenDTO) -> OrdenDTO:
        if not dto.order_id:
            raise ErrorDominio(CodigoError.INVALID_OPERATION, "order_id es requerido")
        
        ord_exist = self.repo.obtener(dto.order_id)
        if ord_exist:
            return orden_a_dto(ord_exist)
        
        cliente_nombre = None
        vehiculo_placa = None
        
        if self.repo_cliente and self.repo_vehiculo:
            customer = dto.customer
            vehicle = dto.vehicle
            
            cliente = self.repo_cliente.buscar_o_crear_por_criterio(
                id_cliente=customer.id_cliente,
                identificacion=customer.identificacion,
                nombre=customer.nombre,
                correo=dto.customer_extra.get("correo") if dto.customer_extra else None,
                direccion=dto.customer_extra.get("direccion") if dto.customer_extra else None,
                celular=dto.customer_extra.get("celular") if dto.customer_extra else None
            )
            cliente_nombre = cliente.nombre
            
            if vehicle.placa:
                vehiculo = self.repo_vehiculo.buscar_o_crear_por_placa(
                    placa=vehicle.placa,
                    id_cliente=cliente.id_cliente,
                    marca=dto.vehicle_extra.get("marca") if dto.vehicle_extra else None,
                    modelo=dto.vehicle_extra.get("modelo") if dto.vehicle_extra else None,
                    anio=dto.vehicle_extra.get("anio") if dto.vehicle_extra else None,
                    kilometraje=dto.vehicle_extra.get("kilometraje") if dto.vehicle_extra else None
                )
                vehiculo_placa = vehiculo.placa
            elif vehicle.id_vehiculo:
                vehiculo = self.repo_vehiculo.buscar_por_criterio(id_vehiculo=vehicle.id_vehiculo)
                if vehiculo is None:
                    raise ErrorDominio(CodigoError.INVALID_OPERATION, f"Vehículo con id {vehicle.id_vehiculo} no encontrado")
                vehiculo_placa = vehiculo.placa
            else:
                raise ErrorDominio(CodigoError.INVALID_OPERATION, "vehicle debe tener id_vehiculo o placa")
        else:
            if dto.customer.nombre:
                cliente_nombre = dto.customer.nombre
            elif dto.customer.identificacion:
                cliente_nombre = dto.customer.identificacion
            elif dto.customer.id_cliente:
                cliente_nombre = str(dto.customer.id_cliente)
            else:
                raise ErrorDominio(CodigoError.INVALID_OPERATION, "customer debe tener id_cliente, identificacion o nombre")
            
            if dto.vehicle.placa:
                vehiculo_placa = dto.vehicle.placa
            elif dto.vehicle.id_vehiculo:
                vehiculo_placa = str(dto.vehicle.id_vehiculo)
            else:
                raise ErrorDominio(CodigoError.INVALID_OPERATION, "vehicle debe tener id_vehiculo o placa")
        
        orden = Orden(dto.order_id, cliente_nombre, vehiculo_placa, dto.timestamp)
        orden.eventos.append(Evento("CREATED", ahora(), {}))
        
        idx_ant = self._obtener_indice_eventos_anterior(orden)
        self.repo.guardar(orden)
        self._registrar_eventos_nuevos(orden, idx_ant)
        return orden_a_dto(orden)


class CancelarOrden(AccionBase):
    def ejecutar(self, dto: CancelarDTO) -> OrdenDTO:
        o = self.repo.obtener(dto.order_id)
        if o is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"No existe orden {dto.order_id}")
        
        idx_prev = self._obtener_indice_eventos_anterior(o)
        o.cancelar(dto.motivo)
        
        self.repo.guardar(o)
        self._registrar_eventos_nuevos(o, idx_prev)
        return orden_a_dto(o)


class EntregarOrden(AccionBase):
    def ejecutar(self, dto: EntregarDTO) -> OrdenDTO:
        orden = self.repo.obtener(dto.order_id)
        if orden is None:
            raise ErrorDominio(CodigoError.ORDER_NOT_FOUND, f"Orden {dto.order_id} no existe")
        
        idx_ant = self._obtener_indice_eventos_anterior(orden)
        orden.entregar()
        
        self.repo.guardar(orden)
        self._registrar_eventos_nuevos(orden, idx_ant)
        return orden_a_dto(orden)

