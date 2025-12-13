from unittest.mock import Mock
from sqlalchemy.orm import Session
from app.infrastructure.repositories.repositorio_vehiculo import RepositorioVehiculoSQL
from app.domain.entidades import Vehiculo


def test_repositorio_vehiculo_obtener_no_existe():
    sesion = Mock(spec=Session)
    query_mock = Mock()
    query_mock.filter.return_value.first.return_value = None
    sesion.query.return_value = query_mock
    
    repo = RepositorioVehiculoSQL(sesion)
    vehiculo = repo.obtener("VEH-999")
    
    assert vehiculo is None

