from app.domain.entidades import Cliente, Vehiculo


def test_cliente_crear():
    cliente = Cliente("Juan Pérez")
    assert cliente.nombre == "Juan Pérez"
    assert cliente.id_cliente is not None


def test_cliente_con_id():
    cliente = Cliente("Juan Pérez")
    cliente.id_cliente = "CLI-001"
    assert cliente.id_cliente == "CLI-001"


def test_vehiculo_crear():
    vehiculo = Vehiculo("ABC-123", "CLI-001")
    assert vehiculo.descripcion == "ABC-123"
    assert vehiculo.id_cliente == "CLI-001"
    assert vehiculo.id_vehiculo is not None


def test_vehiculo_con_todos_los_campos():
    vehiculo = Vehiculo(
        "ABC-123",
        "CLI-001",
        marca="Toyota",
        modelo="Corolla",
        anio=2020,
        id_vehiculo="VEH-001"
    )
    assert vehiculo.descripcion == "ABC-123"
    assert vehiculo.marca == "Toyota"
    assert vehiculo.modelo == "Corolla"
    assert vehiculo.anio == 2020
    assert vehiculo.id_vehiculo == "VEH-001"


def test_vehiculo_sin_campos_opcionales():
    vehiculo = Vehiculo("XYZ-789", "CLI-002")
    assert vehiculo.marca is None
    assert vehiculo.modelo is None
    assert vehiculo.anio is None

