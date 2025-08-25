# services/transaction_service.py
from typing import List
from fastapi import HTTPException
from app.models.transaction_model import Transaction
from sqlalchemy.orm import Session
from app.settings.algorithm_models import load_model, load_scaler
from app.schemas.transaction_schema import TransactionPredictionResponse, TransactionRequest, TransactionResponse
from app.repositories.transaction_repo import TransactionRepository

model = load_model()
scaler = load_scaler()

class TransactionService:

    def __init__(self, db: Session):
        self.repo = TransactionRepository(db)

    def list_transactions_service(self) -> List[TransactionResponse]:
        transaction_list = self.repo.get_all_transactions()
        if transaction_list is None:
            raise HTTPException(status_code=404, detail="Transactions not found")
        return [self._to_response(ts) for ts in transaction_list]
    
    def get_transaction_by_id(self, transaction_id: int) -> TransactionResponse:
        transaction = self.repo.get_transaction_by_id(transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return self._to_response(transaction)

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
            distant_from_home=transaction.distance_from_home,
            currency=transaction.currency,
            card_present=transaction.card_present
        )

        transaction_data = self.extract_features(transaction_request)
        transaction_data_scaled = scaler.transform([transaction_data])

        prediction = model.predict(transaction_data_scaled)
        probability = model.predict_proba(transaction_data_scaled)[0][1]

        return TransactionPredictionResponse(
            is_fraud=prediction[0],
            probability=probability
        )
    
    @staticmethod
    def mask_card(card: str) -> str:
        if len(card) <= 4:
            return card
        return f"{'*'*(len(card)-4)}{card[-4:]}"

    @classmethod
    def _to_response(cls, ts: Transaction) -> TransactionResponse:
        return TransactionResponse(
            costumer_id=ts.customer_id,
            card_number=cls.mask_card(ts.card_number),
            timestamp=ts.timestamp,
            merchant=ts.merchant,
            merchant_category=ts.merchant_category,
            merchant_type=ts.merchant_type,
            amount=ts.amount,
            currency=ts.currency,
            country=ts.country,
            city=ts.city,
            city_size=ts.city_size,
            card_type=ts.card_type,
            card_present=int(ts.card_present),
            device=ts.device,
            channel=ts.channel,
            device_fingerprint=ts.device_fingerprint,
            ip_address=ts.ip_address,
            distance_from_home=ts.distance_from_home,
            high_risk_merchant=ts.high_risk_merchant,
            transaction_hour=ts.transaction_hour,
            weekend_transaction=ts.weekend_transaction,
            velocity_last_hour=ts.velocity_last_hour,
        )
    
    @staticmethod
    def extract_features(transaction_request: TransactionRequest) -> dict:
        """Builds feature dictionary for the model.

        The Transactionrequest object contains:
        channel: str
        device: str
        country: str
        transaction_hour: int
        amount: float
        max_single_amount: float
        distant_from_home: int
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
        device_type = ["Android App", "Safari", "Firefox", "Chrome", "iOS App", "Edge", "NFC Payment", "Magnetic Stripe", "Chip Reader"]
        countries = ["USA", "Australia", "Germany", "UK", "Canada", "Japan", "France", "Singapore", "Nigeria", "Brazil", "Russia", "Mexico"]

        conversion_rates = {
            'EUR': 1.06,
            'CAD': 0.72,
            'RUB': 0.01,
            'NGN': 0.0006,
            'SGD': 0.75,
            'MXN': 0.049,
            'BRL': 0.17,
            'AUD': 0.65,
            'JPY': 0.0065
        }

        features = {
            "channel_large": 1 if transaction_request.channel == "large" else 0,
            "channel_medium": 1 if transaction_request.channel == "medium" else 0,
            "channel_mobile": 1 if transaction_request.channel == "mobile" else 0,
            "channel_web": 1 if transaction_request.channel == "web" else 0,
            "channel_pos": 1 if transaction_request.channel == "pos" else 0,
            "device_Android App": 1 if transaction_request.device == "Android App" else 0,
            "device_Safari": 1 if transaction_request.device == "Safari" else 0,
            "device_Firefox": 1 if transaction_request.device == "Firefox" else 0,
            "device_Chrome": 1 if transaction_request.device == "Chrome" else 0,
            "device_iOS App": 1 if transaction_request.device == "iOS App" else 0,
            "device_Edge": 1 if transaction_request.device == "Edge" else 0,
            "device_NFC Payment": 1 if transaction_request.device == "NFC Payment" else 0,
            "device_Magnetic Stripe": 1 if transaction_request.device == "Magnetic Stripe" else 0,
            "device_Chip Reader": 1 if transaction_request.device == "Chip Reader" else 0,
            "city_Unknown_City": 1 if transaction_request.city == "Unknown City" else 0,
            "country_USA": 1 if transaction_request.country == "USA" else 0,
            "country_Australia": 1 if transaction_request.country == "Australia" else 0,
            "country_Germany": 1 if transaction_request.country == "Germany" else 0,
            "country_UK": 1 if transaction_request.country == "UK" else 0,
            "country_Canada": 1 if transaction_request.country == "Canada" else 0,
            "country_Japan": 1 if transaction_request.country == "Japan" else 0,
            "country_France": 1 if transaction_request.country == "France" else 0,
            "country_Singapore": 1 if transaction_request.country == "Singapore" else 0,
            "country_Nigeria": 1 if transaction_request.country == "Nigeria" else 0,
            "country_Brazil": 1 if transaction_request.country == "Brazil" else 0,
            "country_Russia": 1 if transaction_request.country == "Russia" else 0,
            "country_Mexico": 1 if transaction_request.country == "Mexico" else 0,
            "USD_converted_amount": 0.0,
            "UDS_converted_total_amount": 0.0,
            "is_off_hours": 1 if transaction_request.transaction_hour > 9 or transaction_request.transaction_hour < 17 else 0,
            "is_high_amount": 0,
            "is_low_amount": 0,
            "transaction_hour": transaction_request.transaction_hour,
            "hour": transaction_request.transaction_hour,
            "high_risk_transaction": 1 if transaction_request.country in ['Brazil', 'Mexico', 'Nigeria', 'Russia'] and transaction_request.device in ['Magnetic Stripe', 'NFC Payment', 'Chip Reader'] else 0,
            "card_present": transaction_request.card_present,
            "distance_from_home": transaction_request.distant_from_home,
        }

        features['USD_converted_amount'] = transaction_request.amount * conversion_rates.get(transaction_request.currency, 1.28)

        features['USD_converted_total_amount'] = transaction_request.total_amount * conversion_rates.get(transaction_request.currency, 1.28)

        features['max_single_amount'] = transaction_request.max_single_amount * conversion_rates.get(transaction_request.currency, 1.28)

        features['is_high_amount'] = 1 if features['USD_converted_amount'] > 1000 else 0
        features['is_low_amount'] = 1 if features['USD_converted_amount'] < 100 else 0

        return features
    






    

