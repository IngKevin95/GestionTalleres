import pytest
from app.application.acciones.orden import CrearOrden
from app.application.acciones.estados import EstablecerEstadoDiagnosticado
from app.application.acciones.autorizacion import Autorizar
from app.application.acciones.servicios import AgregarServicio


def test_crear_orden_action_existe():
    assert CrearOrden is not None


def test_estado_diagnosticado_existe():
    assert EstablecerEstadoDiagnosticado is not None


def test_autorizar_existe():
    assert Autorizar is not None


def test_agregar_servicio_existe():
    assert AgregarServicio is not None
