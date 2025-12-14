from typing import List
from sqlalchemy.orm import Session

from ...domain.entidades import Servicio, Componente
from ...domain.dinero import a_decimal
from ..models.servicio_model import ServicioModel
from ..models.componente_model import ComponenteModel


class RepositorioServicioSQL:
    def __init__(self, sesion: Session):
        self.sesion = sesion
    
    def guardar_servicios(self, id_orden: int, servicios: List[Servicio], servicios_existentes: List[ServicioModel]) -> None:
        existentes_dict = {s.id_servicio: s for s in servicios_existentes if s.id_servicio is not None}
        
        for serv in servicios:
            if serv.id_servicio is not None and serv.id_servicio in existentes_dict:
                sm = existentes_dict[serv.id_servicio]
                sm.descripcion = serv.descripcion
                sm.costo_mano_obra_estimado = str(serv.costo_mano_obra_estimado)
                sm.costo_real = str(serv.costo_real) if serv.costo_real else None
                sm.completado = 1 if serv.completado else 0
            else:
                nuevo = ServicioModel(
                    id_orden=id_orden,
                    descripcion=serv.descripcion,
                    costo_mano_obra_estimado=str(serv.costo_mano_obra_estimado),
                    costo_real=str(serv.costo_real) if serv.costo_real else None,
                    completado=1 if serv.completado else 0
                )
                self.sesion.add(nuevo)
                self.sesion.flush()
                serv.id_servicio = nuevo.id_servicio
                servicios_existentes.append(nuevo)
                sm = nuevo
            
            self._guardar_componentes(sm, serv)
        
        ids_servicios = {s.id_servicio for s in servicios if s.id_servicio is not None}
        for sm in list(servicios_existentes):
            if sm.id_servicio not in ids_servicios:
                self.sesion.delete(sm)
                servicios_existentes.remove(sm)
    
    def _guardar_componentes(self, sm: ServicioModel, servicio: Servicio) -> None:
        existentes = {c.id_componente: c for c in sm.componentes if c.id_componente is not None}
        
        for comp in servicio.componentes:
            if comp.id_componente is not None and comp.id_componente in existentes:
                cm = existentes[comp.id_componente]
                cm.descripcion = comp.descripcion
                cm.costo_estimado = str(comp.costo_estimado)
                cm.costo_real = str(comp.costo_real) if comp.costo_real else None
            else:
                nuevo_comp = ComponenteModel(
                    id_servicio=sm.id_servicio,
                    descripcion=comp.descripcion,
                    costo_estimado=str(comp.costo_estimado),
                    costo_real=str(comp.costo_real) if comp.costo_real else None
                )
                self.sesion.add(nuevo_comp)
                self.sesion.flush()
                comp.id_componente = nuevo_comp.id_componente
                sm.componentes.append(nuevo_comp)
        
        ids_comps = {c.id_componente for c in servicio.componentes if c.id_componente is not None}
        for cm in list(sm.componentes):
            if cm.id_componente not in ids_comps:
                self.sesion.delete(cm)
    
    def deserializar_servicios(self, servicios_modelo: List[ServicioModel]) -> List[Servicio]:
        resultado = []
        for sm in servicios_modelo:
            comps = []
            for cm in sm.componentes:
                comp = Componente(
                    descripcion=cm.descripcion,
                    costo_estimado=a_decimal(cm.costo_estimado),
                    costo_real=a_decimal(cm.costo_real) if cm.costo_real else None
                )
                comp.id_componente = cm.id_componente
                comps.append(comp)
            
            serv = Servicio(
                descripcion=sm.descripcion,
                costo_mano_obra_estimado=a_decimal(sm.costo_mano_obra_estimado),
                componentes=comps
            )
            serv.id_servicio = sm.id_servicio
            serv.completado = bool(sm.completado)
            serv.costo_real = a_decimal(sm.costo_real) if sm.costo_real else None
            resultado.append(serv)
        
        return resultado

