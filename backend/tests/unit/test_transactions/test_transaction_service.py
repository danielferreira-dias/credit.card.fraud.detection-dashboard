import pytest
from app.service.transaction_service import TransactionService
from app.schemas.transaction_schema import TransactionRequest

import pytest

@pytest.fixture(autouse=True)
def mock_model(monkeypatch):
    class DummyModel:
        def predict(self, X): return [0] * len(X)
    monkeypatch.setattr("app.settings.algorithm_models.joblib.load", lambda _: DummyModel())

@pytest.fixture
def transaction_request_mock() -> TransactionRequest:
    return TransactionRequest(
        channel="large",
        device="Android App",
        country="USA",
        transaction_hour=14,
        amount=150.0,
        max_single_amount=200.0,
        distance_from_home=1,
        currency="USD",
        card_present=0
    )

@pytest.mark.parametrize(
    "card,expected",[
        ("1234567890123456", "************3456"), 
        ("0000", "0000"),  
        ("", "")                        
    ]
)
def test_mask_card_basic(card, expected):
    assert TransactionService.mask_card(card) == expected

def test_extract_features_missing():
    with pytest.raises(TypeError):
        TransactionService.extract_features(None)

def test_extract_features_none_channel(transaction_request_mock):
    transaction_request_mock.channel = None
    with pytest.raises(ValueError):
        TransactionService.extract_features(transaction_request_mock)

def test_extract_features_valid_values_channel(transaction_request_mock):
    features = TransactionService.extract_features(transaction_request_mock)
    assert features['channel_large'] == 1
    assert features['channel_medium'] == 0
    assert features['channel_mobile'] == 0
    assert features['channel_web'] == 0
    assert features['channel_pos'] == 0

def test_extract_features_valid_values_device(transaction_request_mock):
    features = TransactionService.extract_features(transaction_request_mock)
    assert features['device_Android App'] == 1
    assert features['device_Safari'] == 0
    assert features['device_Firefox'] == 0
    assert features['device_Chrome'] == 0
    assert features['device_iOS App'] == 1
    assert features['device_Edge'] == 0
    assert features['device_NFC Payment'] == 0
    assert features['device_Magnetic Stripe'] == 0
    assert features['device_Chip Reader'] == 0

def test_extract_features_valid_values_country(transaction_request_mock):
    features = TransactionService.extract_features(transaction_request_mock)
    assert features['country_USA'] == 1
    assert features['country_Australia'] == 0
    assert features['country_Germany'] == 0
    assert features['country_UK'] == 0
    assert features['country_Canada'] == 0
    assert features['country_Japan'] == 0
    assert features['country_France'] == 0
    assert features['country_Singapore'] == 0
    assert features['country_Nigeria'] == 0
    assert features['country_Brazil'] == 0
    assert features['country_Russia'] == 0
    assert features['country_Mexico'] == 0

def test_extract_features_amount_conversion(transaction_request_mock):
    features = TransactionService.extract_features(transaction_request_mock)
    assert features['USD_converted_amount'] == 150
    assert features['USD_converted_total_amount'] == 150.0
    assert features['max_single_amount'] == 200.0

def test_extract_features_high_low_amount(transaction_request_mock):
    features = TransactionService.extract_features(transaction_request_mock)
    assert features['is_high_amount'] == 0
    assert features['is_low_amount'] == 0

def test_extract_features_off_hours(transaction_request_mock):
    transaction_request_mock.transaction_hour = 20
    features = TransactionService.extract_features(transaction_request_mock)
    assert features['is_off_hours'] == 1
    transaction_request_mock.transaction_hour = 10
    features = TransactionService.extract_features(transaction_request_mock)
    assert features['is_off_hours'] == 0

def test_extract_features_card_present(transaction_request_mock):
    features = TransactionService.extract_features(transaction_request_mock)
    assert features['card_present'] == 0

def test_extract_features_distance_home_frome(transaction_request_mock):
    features = TransactionService.extract_features(transaction_request_mock)
    assert features['distance_from_home'] == 1


