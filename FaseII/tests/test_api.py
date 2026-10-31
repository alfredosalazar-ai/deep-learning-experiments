"""Pruebas de integración HTTP para la API CIMA."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture()
def client():
    # Usar el contexto activa el lifespan de FastAPI y carga el modelo.
    with TestClient(app) as test_client:
        yield test_client


def test_home_returns_interface(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "CHATBOT CIMA" in response.text


def test_health_model_is_loaded(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["model_loaded"] is True
    assert body["status"] == "ok"


def test_predict_returns_safe_contract(client):
    response = client.post(
        "/predict",
        json={"texto": "Solicito confirmar el pago asociado al folio 12345."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["clase_predicha"] in {
        "INDIVIDUAL", "PAQUETE", "AMBIGUA", "FUERA_ALCANCE"
    }
    assert body["decision_operativa"] in {
        "APTO_PARA_FLUJO_INDIVIDUAL", "REVISION_HUMANA"
    }
    assert body["requiere_revision_humana"] == (
        body["decision_operativa"] == "REVISION_HUMANA"
    )
    assert "no autoriza pagos" in body["advertencia"].lower()


def test_predict_rejects_blank_text(client):
    response = client.post("/predict", json={"texto": "   "})
    assert response.status_code == 422


def test_predict_rejects_missing_text(client):
    response = client.post("/predict", json={})
    assert response.status_code == 422


def test_predict_rejects_text_over_limit(client):
    response = client.post("/predict", json={"texto": "a" * 5001})
    assert response.status_code == 422


def test_openapi_schema_available(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/predict" in response.json()["paths"]
