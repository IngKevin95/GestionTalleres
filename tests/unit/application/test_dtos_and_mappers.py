from app.application.mappers import crear_orden_dto


def test_crear_orden_dto_basico():
    data = {
        "order_id": "ORD-001",
        "customer": "Juan",
        "vehicle": "Toyota"
    }
    resultado = crear_orden_dto(data)
    assert resultado is not None
    assert resultado.order_id == "ORD-001"
