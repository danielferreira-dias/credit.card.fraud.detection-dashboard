import pytest
# tests/factories.py
from datetime import datetime
from app.models.transaction_model import Transaction
from app.infra.logger import setup_logger

logger = setup_logger("test")

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
        distance_from_home=1,
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

@pytest.fixture
def non_fraud_transaction(**overrides) -> Transaction:
    base = dict(
    transaction_id="TX_a0ad2a2a",
    customer_id="CUST_72886",
    card_number="6646734767813109",
    timestamp="2024-09-30T00:00:01.034820",   # normalizado para formato ISO
    merchant="Taco Bell",
    merchant_category="Restaurant",
    merchant_type="fast_food",
    amount=294.87,
    currency="GBP",
    country="UK",
    city="Unknown City",
    city_size="medium",
    card_type="Platinum Credit",
    card_present=False,
    device="iOS App",
    channel="mobile",
    device_fingerprint="e8e6160445c935fd0001501e4cbac8bc",
    ip_address="197.153.60.199",
    distance_from_home=0,          # cuidado: no CSV estava como string "0"
    high_risk_merchant=False,
    transaction_hour=0,
    weekend_transaction=False,
    velocity_last_hour={
        "total_amount": 33498556.080464985,
        "num_transactions": 1197,
        "unique_countries": 12,
        "unique_merchants": 105,
        "max_single_amount": 1925480.6324148502,
    },
    is_fraud=False,
)
    base.update(overrides)
    return Transaction(**base)

@pytest.fixture
def fraud_transaction(**overrides) -> Transaction:
    base = dict(
    transaction_id="TX_3599c101",
    customer_id="CUST_70474",
    card_number="376800864692727",
    timestamp="2024-09-30T00:00:01.764464",
    merchant_category="Entertainment",
    merchant_type="gaming",
    merchant="Steam",
    amount=3368.97,
    currency="BRL",
    country="Mexico",
    city="Unknown City",
    city_size="medium",
    card_type="Platinum Credit",
    card_present=False,
    device="NFC Payment",
    channel="mobile",
    device_fingerprint="a73043a57091e775af37f252b3a32af9",
    ip_address="208.123.221.203",
    distance_from_home=1,
    high_risk_merchant=True,
    transaction_hour=0,
    weekend_transaction=False,
    velocity_last_hour={
        "total_amount": 33498556.080464985,
        "num_transactions": 1197,
        "unique_countries": 12,
        "unique_merchants": 105,
        "max_single_amount": 1925480.6324148502,
    },
    is_fraud=True,  # ground truth desta linha
)
    base.update(overrides)
    return Transaction(**base)

def test_create_transaction(client):
    payload = {
        "transaction_id": "tx_create_test",
        "customer_id": "CUST_70474",
        "card_number": "1454535342727",
        "timestamp": "2024-09-30T00:00:01.764464",
        "merchant": "Steam",
        "merchant_category": "Entertainment",
        "merchant_type": "gaming",
        "amount": 3368.97,
        "currency": "BRL",
        "country": "Brazil",
        "city": "Unknown City",
        "city_size": "medium",
        "card_type": "Platinum Credit",
        "card_present": 0,
        "device": "Edge",
        "channel": "web",
        "device_fingerprint": "a73043a57091e775af37f252b3a32af9",
        "ip_address": "208.123.221.203",
        "distance_from_home": 1,
        "high_risk_merchant": True,
        "transaction_hour": 0,
        "weekend_transaction": False,
        "velocity_last_hour": {
            "num_transactions": 509,
            "total_amount": 20114759.055250417,
            "unique_merchants": 100,
            "unique_countries": 12,
            "max_single_amount": 5149117.011434267
        }
    }
    r = client.post("/transactions/create_transaction", json=payload)
    logger.info("Response for create transaction: %s", r.json())
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "Transição criada com successo"
    assert data["data"].get("customer_id") == "CUST_70474"

def test_create_transaction_duplicate_id(client, pg_sessionmaker):
    db = pg_sessionmaker()
    tx1 = build_transaction(transaction_id="tx_duplicate")
    db.add(tx1)
    db.commit()

    payload = {
        "transaction_id": "tx_duplicate",
        "customer_id": "CUST_70474",
        "card_number": "1454535342727",
        "timestamp": "2024-09-30T00:00:01.764464",
        "merchant": "Steam",
        "merchant_category": "Entertainment",
        "merchant_type": "gaming",
        "amount": 3368.97,
        "currency": "BRL",
        "country": "Brazil",
        "city": "Unknown City",
        "city_size": "medium",
        "card_type": "Platinum Credit",
        "card_present": 0,
        "device": "Edge",
        "channel": "web",
        "device_fingerprint": "a73043a57091e775af37f252b3a32af9",
        "ip_address": "208.123.221.203",
        "distance_from_home": 1,
        "high_risk_merchant": True,
        "transaction_hour": 0,
        "weekend_transaction": False,
        "velocity_last_hour": {
            "num_transactions": 509,
            "total_amount": 20114759.055250417,
            "unique_merchants": 100,
            "unique_countries": 12,
            "max_single_amount": 5149117.011434267
        }
    }
    
    r = client.post("/transactions/create_transaction", json=payload)
    logger.info("Response for duplicate ID: %s", r.json())
    data = r.json()
    assert data.get('message') == "Transição já existe na base de dados;"
    assert r.status_code == 409 

def test_create_transaction_missing_field(client):
    payload = {
        "transaction_id": "tx_duplicate",
        "customer_id": "CUST_70474",
        "card_number": "1454535342727",
        "timestamp": "2024-09-30T00:00:01.764464",
        "merchant": "Steam",
        "merchant_category": "Entertainment",
        "merchant_type": "gaming",
        "amount": 3368.97,
        "currency": "BRL",
        "country": "Brazil",
        "city": "Unknown City",
        "city_size": "medium",
        "card_type": "Platinum Credit",
        "card_present": 0,
        "device": "Edge",
        "channel": "web",
        "device_fingerprint": "a73043a57091e775af37f252b3a32af9",
        "ip_address": "208.123.221.203",
        "distance_from_home": 1,
        "high_risk_merchant": None,  # campo obrigatório
        "transaction_hour": 0,
        "weekend_transaction": False,
        "velocity_last_hour": {
            "num_transactions": 509,
            "total_amount": 20114759.055250417,
            "unique_merchants": 100,
            "unique_countries": 12,
            "max_single_amount": 5149117.011434267
        }
    }
    
    r = client.post("/transactions/create_transaction", json=payload)
    assert r.status_code == 422  # Unprocessable Entity devido a validação do Pydantic
    
def test_get_transaction_not_found(client):
    r = client.get("/transactions/UNKNOWN_ID")
    assert r.status_code == 404

def test_get_transaction_found(client, pg_sessionmaker):
    db = pg_sessionmaker()
    tx = build_transaction(transaction_id="tx_teste")
    db.add(tx)
    db.commit()
    r = client.get("/transactions/tx_teste")
    assert r.status_code == 200
    data = r.json()
    assert data["amount"] == 100.0

def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "OK"}

def test_predict_transaction_endpoint(client, pg_sessionmaker):
    db = pg_sessionmaker()
    tx = build_transaction(transaction_id="TX_a0ad2a2a", amount=999.9)
    db.add(tx)
    db.commit()

    logger.info("Inserted test transaction into DB")
    logger.info("Transaction: %s", tx)

    r = client.get("/transactions/TX_a0ad2a2a/predict")
    assert r.status_code == 200
    data = r.json()
    assert "is_fraud" in data

def test_predict_transaction_is_false(client, non_fraud_transaction):
    transaction_id = non_fraud_transaction.transaction_id
    r = client.get(f"/transactions/{transaction_id}/predict")

    assert r.status_code == 200
    data = r.json()
    assert data.get('is_fraud') == False

def test_predict_transaction_is_true(client, pg_sessionmaker, fraud_transaction):
    db = pg_sessionmaker()
    db.add(fraud_transaction)
    db.commit()
    db.refresh(fraud_transaction)
    transaction_id = fraud_transaction.transaction_id
    r = client.get(f"/transactions/{transaction_id}/predict")

    assert r.status_code == 200
    data = r.json()
    assert data.get('is_fraud') == True
    