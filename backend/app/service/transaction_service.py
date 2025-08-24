# services/transaction_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.settings.algorithm_models import load_model, load_scaler
from backend.app.schemas.transaction_schema import TransactionRequest
from backend.app.repositories.transaction_repo import TransactionRepository

model = load_model()
scaler = load_scaler()

class TransasactionSercice:

    def __init__(self, db: Session):
        self.repo = TransactionRepository(db)

    def list_transactions_service(self):
        return self.repo.get_all_transactions()

    def predict_transaction_service(self, transaction_id: int) -> dict:
        transaction = self.repo.get_transaction_by_id(transaction_id)

        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found") 
        
        transaction_request = TransactionRequest(
            channel=transaction.channel,
            device=transaction.device,
            country=transaction.country,
            transaction_hour=transaction.transaction_hour,
            amount=transaction.amount,
            max_single_amount = transaction.velocity_last_hour.get("max_single_amount", 0.0),
            distante_from_home=transaction.distance_from_home,
            card_present=transaction.card_present
        )

        transaction_data = extract_features(transaction_request)
        transaction_data_scaled = scaler.transform([transaction_data])

        prediction = model.predict(transaction_data_scaled)
        probability = model.predict_proba(transaction_data_scaled)[0][1]

        return {
            "is_fraud": prediction,
            "probability": probability
        }

def extract_features(transaction_request: TransactionRequest):
    """Builds feature dictionary for the model.

    The Transactionrequest object contains:
    channel: str
    device: str
    country: str
    transaction_hour: int
    amount: float
    max_single_amount: float
    distante_from_home: int
    card_present: int

    The dictionary returned by this function must include exactly the
    following variables/keys (feature order is important downstream):

    channel_large, channel_medium, device_Android App, device_Safari,
    device_Firefox, USD_converted_total_amount, device_Chrome, device_iOS App,
    city_Unknown City, country_USA, country_Australia, country_Germany,
    country_UK, country_Canada, country_Japan, country_France, device_Edge,
    country_Singapore, channel_mobile, country_Nigeria, country_Brazil,
    country_Russia, country_Mexico, is_off_hours, max_single_amount,
    USD_converted_amount, channel_web, is_high_amount, is_low_amount,
    transaction_hour, hour, device_NFC Payment, device_Magnetic Stripe,
    device_Chip Reader, high_risk_transaction, channel_pos, card_present,
    distance_from_home
    """

    channel_type = ["large", "medium", "mobile", "web", "pos"]
    device_type = ["Android_App", "Safari", "Firefox", "Chrome", "iOS_App", "Edge", "NFC_Payment", "Magnetic_Stripe", "Chip_Reader"]
    countries = ["USA", "Australia", "Germany", "UK", "Canada", "Japan", "France", "Singapore", "Nigeria", "Brazil", "Russia", "Mexico"]

    features = {
        "channel_large": 0,
        "channel_medium": 0,
        "channel_mobile": 0,
        "channel_web": 0,
        "channel_pos": 0,
        "device_Android_App": 0,
        "device_Safari": 0,
        "device_Firefox": 0,
        "device_Chrome": 0,
        "device_iOS_App": 0,
        "device_Edge": 0,
        "device_NFC_Payment": 0,
        "device_Magnetic_Stripe": 0,
        "device_Chip_Reader": 0,
        "city_Unknown_City": 0,
        "country_USA": 0,
        "country_Australia": 0,
        "country_Germany": 0,
        "country_UK": 0,
        "country_Canada": 0,
        "country_Japan": 0,
        "country_France": 0,
        "country_Singapore": 0,
        "country_Nigeria": 0,
        "country_Brazil": 0,
        "country_Russia": 0,
        "country_Mexico": 0,
        "USD_converted_total_amount": 0.0,
    }
    

