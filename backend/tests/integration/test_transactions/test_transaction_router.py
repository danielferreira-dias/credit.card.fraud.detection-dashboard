import pytest
# tests/factories.py
from datetime import datetime
from app.models.transaction_model import Transaction

def build_transaction(**overrides) -> Transaction:
    """
    Cria uma instância Transaction para testes, com defaults seguros.
    Campos passados em overrides substituem os defaults.
    """
    base = dict(
        transaction_id="TX_DEFAULT",
        customer_id="CUST_1",
        card_number="1234567890123456",
        timestamp="2024-09-30T00:00:01.034820",
        merchant="Loja XPTO",
        merchant_category="GROCERY",
        merchant_type="Retail",
        amount=100.0,
        currency="EUR",
        country="PT",
        city="Lisboa",
        city_size="LARGE",
        card_type="VISA",
        card_present=True,
        device="iOS App",
        channel="mobile",
        device_fingerprint="dfp123",
        ip_address="127.0.0.1",
        distance_from_home=5.5,
        high_risk_merchant=False,
        transaction_hour=12,
        weekend_transaction=False,
        velocity_last_hour={
            "num_transactions": 1,
            "total_amount": 100.0,
            "unique_merchants": 1,
            "unique_countries": 1,
            "max_single_amount": 100.0,
        },
        is_fraud=False,
    )
    base.update(overrides)  # sobrescreve defaults com o que passares
    return Transaction(**base)

def test_get_transaction_not_found(client):
    r = client.get("/transactions/UNKNOWN_ID")
    assert r.status_code == 404

def test_get_transaction_found(client, pg_sessionmaker):
    db = pg_sessionmaker()
    tx = build_transaction(transaction_id="TX_12345")
    db.add(tx)
    db.commit()

    r = client.get("/transactions/TX_12345")
    assert r.status_code == 200
    data = r.json()
    assert data["amount"] == 100.0

def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_predict_transaction_endpoint(client, pg_sessionmaker):
    print(pg_sessionmaker().bind.url)
    db = pg_sessionmaker()
    tx = build_transaction(transaction_id="TX_TEST", amount=999.9)
    db.add(tx)
    db.commit()

    r = client.get("/transactions/TX_TEST/predict")
    assert r.status_code == 200
    data = r.json()
    assert "is_fraud" in data