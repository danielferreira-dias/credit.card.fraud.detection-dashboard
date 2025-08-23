import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import transaction as transaction_router

@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def expected_prediction_keys() -> set[str]:
    return {"is_fraud", "probability"}


def test_root_health_check(client: TestClient):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello from credit-card-fraud-detection-dashboard!"}

def test_list_transactions_ok(client: TestClient):
    resp = client.get("/transactions/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    first = data[0]


def test_get_transaction_ok(client: TestClient):
    resp = client.get("/transactions/1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 1
    assert body["is_fraud"] is True


def test_predict_transaction_ok(client: TestClient):
    resp = client.get("/transactions/1/predict")
    assert resp.status_code == 200
    body = resp.json()

def test_delete_transaction_ok(client: TestClient):
    resp = client.delete("/transactions/1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 1
