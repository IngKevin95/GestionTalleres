from decimal import Decimal
from datetime import datetime
from fastapi.testclient import TestClient
from app.drivers.api.main import app

client = TestClient(app)


def test_flujo_completo_hasta_delivered():
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2024-01-01T10:00:00Z",
                "data": {
                    "customer": "Juan Pérez",
                    "vehicle": "Toyota Corolla 2020"
                }
            }
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["orders"]) > 0
    order_id = data["orders"][0]["order_id"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "ADD_SERVICE",
                "ts": "2024-01-01T10:05:00Z",
                "data": {
                    "order_id": order_id,
                    "description": "Cambio de aceite",
                    "labor_estimated_cost": 500.00,
                    "components": [
                        {
                            "description": "Aceite 5W-30",
                            "estimated_cost": 300.00
                        }
                    ]
                }
            },
            {
                "op": "SET_STATE_DIAGNOSED",
                "ts": "2024-01-01T10:10:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "AUTHORIZE",
                "ts": "2024-01-01T10:15:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "SET_STATE_IN_PROGRESS",
                "ts": "2024-01-01T10:20:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    servicio_id = data["orders"][-1]["services"][0]["id_servicio"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "SET_REAL_COST",
                "ts": "2024-01-01T11:00:00Z",
                "data": {
                    "order_id": order_id,
                    "service_id": servicio_id,
                    "real_cost": 800.00,
                    "components_real": {},
                    "completed": true
                }
            },
            {
                "op": "TRY_COMPLETE",
                "ts": "2024-01-01T12:00:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "DELIVER",
                "ts": "2024-01-01T13:00:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["orders"]) > 0
    assert data["orders"][-1]["status"] == "DELIVERED"


def test_excede_110_requiere_reautorizacion():
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2024-01-01T10:00:00Z",
                "data": {"customer": "Test", "vehicle": "Auto"}
            }
        ]
    })
    
    assert response.status_code == 200
    order_id = response.json()["orders"][0]["order_id"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "ADD_SERVICE",
                "ts": "2024-01-01T10:05:00Z",
                "data": {
                    "order_id": order_id,
                    "description": "Servicio",
                    "labor_estimated_cost": 10000.00,
                    "components": []
                }
            },
            {
                "op": "SET_STATE_DIAGNOSED",
                "ts": "2024-01-01T10:10:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "AUTHORIZE",
                "ts": "2024-01-01T10:15:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "SET_STATE_IN_PROGRESS",
                "ts": "2024-01-01T10:20:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    servicio_id = response.json()["orders"][-1]["services"][0]["id_servicio"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "SET_REAL_COST",
                "ts": "2024-01-01T11:00:00Z",
                "data": {
                    "order_id": order_id,
                    "service_id": servicio_id,
                    "real_cost": 12000.00,
                    "components_real": {},
                    "completed": true
                }
            },
            {
                "op": "TRY_COMPLETE",
                "ts": "2024-01-01T12:00:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["errors"]) > 0
    assert data["errors"][-1]["code"] == "REQUIRES_REAUTH"
    
    orden_response = client.get(f"/orders/{order_id}")
    assert orden_response.json()["status"] == "WAITING_FOR_APPROVAL"


def test_exacto_110_permita_completar():
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2024-01-01T10:00:00Z",
                "data": {"customer": "Test", "vehicle": "Auto"}
            }
        ]
    })
    
    order_id = response.json()["orders"][0]["order_id"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "ADD_SERVICE",
                "ts": "2024-01-01T10:05:00Z",
                "data": {
                    "order_id": order_id,
                    "description": "Servicio",
                    "labor_estimated_cost": 10000.00,
                    "components": []
                }
            },
            {
                "op": "SET_STATE_DIAGNOSED",
                "ts": "2024-01-01T10:10:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "AUTHORIZE",
                "ts": "2024-01-01T10:15:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "SET_STATE_IN_PROGRESS",
                "ts": "2024-01-01T10:20:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    servicio_id = response.json()["orders"][-1]["services"][0]["id_servicio"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "SET_REAL_COST",
                "ts": "2024-01-01T11:00:00Z",
                "data": {
                    "order_id": order_id,
                    "service_id": servicio_id,
                    "real_cost": 11000.00,
                    "components_real": {},
                    "completed": true
                }
            },
            {
                "op": "TRY_COMPLETE",
                "ts": "2024-01-01T12:00:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    orden = next((o for o in data["orders"] if o["order_id"] == order_id), None)
    if orden:
        assert orden["status"] == "COMPLETED"


def test_reautorizacion_exitosa():
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2024-01-01T10:00:00Z",
                "data": {"customer": "Test", "vehicle": "Auto"}
            }
        ]
    })
    
    order_id = response.json()["orders"][0]["order_id"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "ADD_SERVICE",
                "ts": "2024-01-01T10:05:00Z",
                "data": {
                    "order_id": order_id,
                    "description": "Servicio",
                    "labor_estimated_cost": 10000.00,
                    "components": []
                }
            },
            {
                "op": "SET_STATE_DIAGNOSED",
                "ts": "2024-01-01T10:10:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "AUTHORIZE",
                "ts": "2024-01-01T10:15:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "SET_STATE_IN_PROGRESS",
                "ts": "2024-01-01T10:20:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    servicio_id = response.json()["orders"][-1]["services"][0]["id_servicio"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "SET_REAL_COST",
                "ts": "2024-01-01T11:00:00Z",
                "data": {
                    "order_id": order_id,
                    "service_id": servicio_id,
                    "real_cost": 12000.00,
                    "components_real": {},
                    "completed": true
                }
            },
            {
                "op": "TRY_COMPLETE",
                "ts": "2024-01-01T12:00:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "REAUTHORIZE",
                "ts": "2024-01-01T13:00:00Z",
                "data": {
                    "order_id": order_id,
                    "new_authorized_amount": 15000.00
                }
            }
        ]
    })
    
    assert response.status_code == 200
    orden = client.get(f"/orders/{order_id}").json()
    assert orden["status"] == "AUTHORIZED"
    assert orden["authorization_version"] == 2


def test_error_secuencia_in_progress_sin_autorizar():
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2024-01-01T10:00:00Z",
                "data": {"customer": "Test", "vehicle": "Auto"}
            }
        ]
    })
    
    order_id = response.json()["orders"][0]["order_id"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "SET_STATE_IN_PROGRESS",
                "ts": "2024-01-01T10:20:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["errors"]) > 0
    assert data["errors"][0]["code"] == "SEQUENCE_ERROR"


def test_modificar_post_autorizacion():
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2024-01-01T10:00:00Z",
                "data": {"customer": "Test", "vehicle": "Auto"}
            }
        ]
    })
    
    order_id = response.json()["orders"][0]["order_id"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "ADD_SERVICE",
                "ts": "2024-01-01T10:05:00Z",
                "data": {
                    "order_id": order_id,
                    "description": "Servicio 1",
                    "labor_estimated_cost": 1000.00,
                    "components": []
                }
            },
            {
                "op": "SET_STATE_DIAGNOSED",
                "ts": "2024-01-01T10:10:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "AUTHORIZE",
                "ts": "2024-01-01T10:15:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "ADD_SERVICE",
                "ts": "2024-01-01T10:20:00Z",
                "data": {
                    "order_id": order_id,
                    "description": "Servicio 2",
                    "labor_estimated_cost": 500.00,
                    "components": []
                }
            }
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["errors"]) > 0
    assert data["errors"][-1]["code"] == "NOT_ALLOWED_AFTER_AUTHORIZATION"


def test_cancelar_orden():
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2024-01-01T10:00:00Z",
                "data": {"customer": "Test", "vehicle": "Auto"}
            }
        ]
    })
    
    order_id = response.json()["orders"][0]["order_id"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "CANCEL",
                "ts": "2024-01-01T10:05:00Z",
                "data": {
                    "order_id": order_id,
                    "reason": "Cliente canceló"
                }
            }
        ]
    })
    
    assert response.status_code == 200
    orden = client.get(f"/orders/{order_id}").json()
    assert orden["status"] == "CANCELLED"


def test_autorizar_sin_servicios():
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2024-01-01T10:00:00Z",
                "data": {"customer": "Test", "vehicle": "Auto"}
            }
        ]
    })
    
    order_id = response.json()["orders"][0]["order_id"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "SET_STATE_DIAGNOSED",
                "ts": "2024-01-01T10:10:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "AUTHORIZE",
                "ts": "2024-01-01T10:15:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["errors"]) > 0
    assert data["errors"][-1]["code"] == "NO_SERVICES"


def test_redondeo_half_even_casos_limite():
    from app.domain.dinero import redondear_mitad_par
    from decimal import Decimal
    
    assert redondear_mitad_par(Decimal("2.005"), 2) == Decimal("2.00")
    assert redondear_mitad_par(Decimal("2.015"), 2) == Decimal("2.02")
    assert redondear_mitad_par(Decimal("2.025"), 2) == Decimal("2.02")
    assert redondear_mitad_par(Decimal("2.035"), 2) == Decimal("2.04")


def test_intentar_completar_sin_servicios_completados():
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2024-01-01T10:00:00Z",
                "data": {"customer": "Test", "vehicle": "Auto"}
            }
        ]
    })
    
    order_id = response.json()["orders"][0]["order_id"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "ADD_SERVICE",
                "ts": "2024-01-01T10:05:00Z",
                "data": {
                    "order_id": order_id,
                    "description": "Servicio 1",
                    "labor_estimated_cost": 1000.00,
                    "components": []
                }
            },
            {
                "op": "ADD_SERVICE",
                "ts": "2024-01-01T10:06:00Z",
                "data": {
                    "order_id": order_id,
                    "description": "Servicio 2",
                    "labor_estimated_cost": 2000.00,
                    "components": []
                }
            },
            {
                "op": "SET_STATE_DIAGNOSED",
                "ts": "2024-01-01T10:10:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "AUTHORIZE",
                "ts": "2024-01-01T10:15:00Z",
                "data": {"order_id": order_id}
            },
            {
                "op": "SET_STATE_IN_PROGRESS",
                "ts": "2024-01-01T10:20:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    servicios = response.json()["orders"][-1]["services"]
    servicio_id_1 = servicios[0]["id_servicio"]
    servicio_id_2 = servicios[1]["id_servicio"]
    
    response = client.post("/commands", json={
        "commands": [
            {
                "op": "SET_REAL_COST",
                "ts": "2024-01-01T11:00:00Z",
                "data": {
                    "order_id": order_id,
                    "service_id": servicio_id_1,
                    "real_cost": 1000.00,
                    "components_real": {},
                    "completed": True
                }
            },
            {
                "op": "SET_REAL_COST",
                "ts": "2024-01-01T11:01:00Z",
                "data": {
                    "order_id": order_id,
                    "service_id": servicio_id_2,
                    "real_cost": 2000.00,
                    "components_real": {},
                    "completed": False
                }
            },
            {
                "op": "TRY_COMPLETE",
                "ts": "2024-01-01T12:00:00Z",
                "data": {"order_id": order_id}
            }
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["errors"]) > 0
    assert data["errors"][-1]["code"] == "INVALID_OPERATION"
    assert "completados" in data["errors"][-1]["message"].lower()
    
    orden_response = client.get(f"/orders/{order_id}")
    assert orden_response.json()["status"] == "IN_PROGRESS"

