# services/transaction_service.py
from typing import List
import numpy as np
import pandas as pd
import logging
from sklearn.exceptions import NotFittedError
from sqlalchemy.orm import Session
from app.models.transaction_model import FEATURE_COLUMNS, Transaction
from app.schemas.transaction_schema import TransactionCreate, TransactionPredictionResponse, TransactionRequest, TransactionResponse
from app.repositories.transaction_repo import TransactionRepository
from app.infra.model_loader import ModelLoader
from app.exception.transaction_exceptions import TransactionInvalidDataError, TransactionNotFoundError, ModelNotLoadedError
from app.schemas.features_schema import TransactionFeatures, conversion_rates
from app.schemas.filter_schema import TransactionFilter

logger = logging.getLogger(__name__)

class TransactionService:

    def __init__(self, db: Session):
        self.repo = TransactionRepository(db)
        self.artifacts = ModelLoader.load()
        try:
            self.artifacts = ModelLoader.load()
            self.scaler = self.artifacts.scaler
            self.model = self.artifacts.model
        except Exception as e:
            logger.critical("Erro ao carregar artefactos de ML", exc_info=True)
            raise ModelNotLoadedError("Erro ao carregar artefactos de ML") from e

    def get_transactions(self, filters: TransactionFilter, limit: int, skip: int) -> List[TransactionResponse]:
        transaction_list = self.repo.get_all_transactions(filters, limit, skip)
        if transaction_list is None or len(transaction_list) == 0:
            logger.error("No transactions found in the database.")
            raise TransactionNotFoundError(name="Transactions Not Found", message="Transactions do not exist.") 
        return [self._to_response(ts) for ts in transaction_list]
    
    def get_transaction_id(self, transaction_id: str) -> TransactionResponse:
        if transaction_id is None:
            logger.error(f"{transaction_id} cannot be None for prediction.")
            raise TransactionInvalidDataError("transaction_id cannot be None")

        transaction = self.repo.get_transaction_id(transaction_id)
        if transaction is None:
            logger.error(f"Transaction with ID {transaction_id} not found.")
            raise TransactionNotFoundError(name="Transaction Not Found", message=f"Transaction with ID {transaction_id} does not exist.")    
        
        return self._to_response(transaction)

    def predict_transaction(self, transaction_id: str) -> dict:

        if transaction_id is None:
            logger.error(f"{transaction_id} cannot be None for prediction.")
            raise TransactionInvalidDataError("transaction_id cannot be None")

        transaction = self.repo.get_transaction_id(transaction_id)
        logger.info(f"Fetched transaction for prediction: {transaction}")

        if transaction is None:
            logger.warning(f"Transaction with ID {transaction_id} not found for prediction.")
            raise TransactionNotFoundError(name="Transaction Not Found", message=f"Transaction with ID {transaction_id} does not exist.")
        
        transaction_request = TransactionRequest(
            channel=transaction.channel,
            device=transaction.device,
            country=transaction.country,
            city=transaction.city,
            transaction_hour=transaction.transaction_hour,
            amount=transaction.amount,
            max_single_amount = transaction.velocity_last_hour.get("max_single_amount", 0.0),
            total_amount = transaction.velocity_last_hour.get("total_amount", 0.0),
            distance_from_home=transaction.distance_from_home,
            currency=transaction.currency,
            card_present=transaction.card_present
        )

        transaction_data = self.extract_features(transaction_request, conversion_rates)
        if transaction_data is None:
            raise TransactionInvalidDataError("Transaction data for prediction is none.")
        logger.info(f"Current transaction data for prediction is -> {transaction_data}")

        try:
            transaction_data_numpy = np.array([[transaction_data.model_dump(by_alias=True)[c] for c in FEATURE_COLUMNS]], dtype=float)
            ##logger.info(f"Data was transformed into numpy {transaction_data_numpy}")

            transaction_data_dataframe = pd.DataFrame([transaction_data.model_dump(by_alias=True)], columns=FEATURE_COLUMNS)

            logger.info("Feature columns received: %s", list(transaction_data_dataframe.columns))
            assert list(transaction_data_dataframe.columns) == FEATURE_COLUMNS, "Ordem das colunas incorreta!"
            # Se tens scaler + modelo separados:
            X_scaled = self.scaler.transform(transaction_data_numpy)
            y_pred = int(self.model.predict(X_scaled)[0])

            probas = getattr(self.model, "predict_proba", None)
            if probas is not None:
                p = self.model.predict_proba(X_scaled)
                p_pos = float(np.asarray(p)[..., -1].ravel()[0])   # robusto (pega a última coluna)
            else:
                # fallback caso não exista predict_proba
                p_pos = None

        except NotFittedError as e:
            logger.error("Model pipeline not fitted", exc_info=True)
            raise ModelNotLoadedError("Model not fitted; load a trained artifact.") from e

        logger.info(f"Prediction for transaction ID {transaction_id}: {y_pred} with probability of being fraudulent {p_pos}") 

        return TransactionPredictionResponse(
            is_fraud=True if y_pred == 1 else False,
            probability=p_pos
        )
    
    def create_transaction(self, new_transaction: TransactionCreate) -> TransactionResponse:
        return self._to_response(self.repo.create_transaction(new_transaction))
    
    def delete_transaction(self, transaction_id: str) -> str:
        transaction = self.repo.get_transaction_id(transaction_id)
        if transaction is None:
            logger.error(f"Transaction with ID {transaction_id} not found for deletion.")
            raise TransactionNotFoundError(name="Transaction Not Found", message=f"Transaction with ID {transaction_id} does not exist.")    
        
        self.repo.delete_transaction(transaction_id)
        return f"Transaction with ID {transaction_id} deleted successfully."

    def update_transaction(self, transaction_id: str, updated_transaction: TransactionCreate) -> TransactionResponse:
        existing_transaction = self.repo.get_transaction_id(transaction_id)
        
        if existing_transaction is None:
            logger.error(f"Transaction with ID {transaction_id} not found for update.")
            raise TransactionNotFoundError(name="Transaction Not Found", message=f"Transaction with ID {transaction_id} does not exist.")    

        for key, value in updated_transaction.__dict__.items():
                if key != "transaction_id" and value is not None:
                    setattr(existing_transaction, key, value)

        return self._to_response(self.repo.update_transaction(existing_transaction))
    
    @staticmethod
    def mask_card(card: str) -> str:
        if len(card) <= 4:
            return card
        return f"{'*'*(len(card)-4)}{card[-4:]}"

    @classmethod
    def _to_response(cls, ts: Transaction) -> TransactionResponse:
        """
        Converts a Transaction model instance to a TransactionResponse schema.
        Args:
            ts (Transaction): The transaction model instance.
        Returns:
            TransactionResponse: The transaction response schema.
        """
        if ts is None:
            raise ValueError("Transaction instance cannot be None")

        return TransactionResponse(
            customer_id=ts.customer_id,
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
    def extract_features(transaction_request: TransactionRequest, conversion_rates: dict) -> TransactionFeatures:
        return TransactionFeatures(
            channel_medium=1 if transaction_request.channel == "medium" else 0,
            **{"device_Android App": 1 if transaction_request.device == "Android App" else 0},
            device_Safari=1 if transaction_request.device == "Safari" else 0,
            device_Firefox=1 if transaction_request.device == "Firefox" else 0,
            USD_converted_total_amount=transaction_request.total_amount * conversion_rates.get(transaction_request.currency, 1.28),
            device_Chrome=1 if transaction_request.device == "Chrome" else 0,
            **{"device_iOS App": 1 if transaction_request.device == "iOS App" else 0},
            **{"city_Unknown City": 1 if transaction_request.city == "Unknown City" else 0},
            country_USA=1 if transaction_request.country == "USA" else 0,
            country_Australia=1 if transaction_request.country == "Australia" else 0,
            country_Germany=1 if transaction_request.country == "Germany" else 0,
            country_UK=1 if transaction_request.country == "UK" else 0,
            country_Canada=1 if transaction_request.country == "Canada" else 0,
            country_Japan=1 if transaction_request.country == "Japan" else 0,
            country_France=1 if transaction_request.country == "France" else 0,
            device_Edge=1 if transaction_request.device == "Edge" else 0,
            country_Singapore=1 if transaction_request.country == "Singapore" else 0,
            channel_mobile=1 if transaction_request.channel == "mobile" else 0,
            country_Nigeria=1 if transaction_request.country == "Nigeria" else 0,
            country_Brazil=1 if transaction_request.country == "Brazil" else 0,
            country_Russia=1 if transaction_request.country == "Russia" else 0,
            country_Mexico=1 if transaction_request.country == "Mexico" else 0,
            is_off_hours=1 if transaction_request.transaction_hour < 9 or transaction_request.transaction_hour > 17 else 0,
            max_single_amount=transaction_request.max_single_amount * conversion_rates.get(transaction_request.currency, 1.28),
            USD_converted_amount=transaction_request.amount * conversion_rates.get(transaction_request.currency, 1.28),
            channel_web=1 if transaction_request.channel == "web" else 0,
            is_high_amount=1 if (transaction_request.amount * conversion_rates.get(transaction_request.currency, 1.28)) > 1000 else 0,
            is_low_amount=1 if (transaction_request.amount * conversion_rates.get(transaction_request.currency, 1.28)) < 100 else 0,
            transaction_hour=transaction_request.transaction_hour,
            hour=transaction_request.transaction_hour,
            **{"device_NFC Payment": 1 if transaction_request.device == "NFC Payment" else 0},
            **{"device_Magnetic Stripe": 1 if transaction_request.device == "Magnetic Stripe" else 0},
            **{"device_Chip Reader": 1 if transaction_request.device == "Chip Reader" else 0},
            high_risk_transaction=1 if transaction_request.country in ['Brazil', 'Mexico', 'Nigeria', 'Russia']and transaction_request.device in ['Magnetic Stripe', 'NFC Payment', 'Chip Reader'] else 0,
            channel_pos=1 if transaction_request.channel == "pos" else 0,
            suspicious_device= 1 if transaction_request.device in ["NFC Payment", "Magnetic Stripe", "Chip Reader"] else 0,
            card_present=1 if transaction_request.card_present else 0,
            distance_from_home=transaction_request.distance_from_home,
        )






    

