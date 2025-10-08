
from pydantic import EmailStr
from app.schemas.user_schema import UserCreate, UserRegisterSchema, UserResponse
from app.models.user_model import Analysis, Report, User
from app.repositories.user_repo import AnalysisRepository, ReportRepository, UserRepository
from app.exception.user_exceptions import UserCredentialInvalid, UserDuplicateException, UserNotFoundException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.security.password_utils import hash_password

class UserService:

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user_service(self, user_data: UserRegisterSchema) -> UserResponse:
        if user_data.password != user_data.confirm_password:
            raise UserCredentialInvalid('Password is not matching the confirm password')
        new_user = await self.repo.get_user_by_email(user_data.email)
        if new_user:
            raise UserDuplicateException(
                message="User with this email already exists"
            )
        hashed_password = hash_password(user_data.password)
        user_data_with_hash = UserCreate(
            email=user_data.email,
            name=user_data.name,
            password=hashed_password,
            confirmed=True  # Users are confirmed upon creation
        )
        user = await self.repo.create_user(user_data_with_hash)
        return self._to_response_model(user)

    async def get_user_service(self, user_id: int) -> UserResponse:
        user = await self.repo.get_user(user_id)
        if user is None:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return self._to_response_model(user)
    
    async def get_user_service_email(self, email: EmailStr) -> UserResponse:
        user = await self.repo.get_user_by_email(email)
        if user is None:
            raise UserNotFoundException(f"User with email {email} not found")
        return self._to_response_model(user)

    async def get_users_service(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        users = await self.repo.get_users(skip=skip, limit=limit)
        return [self._to_response_model(user) for user in users]

    async def update_user_service(self, user_id: int, user_data: dict) -> UserResponse:
        if 'password' in user_data:
            user_data['password'] = hash_password(user_data['password'])
        user = await self.repo.update_user(user_id, user_data)
        if user is None:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return self._to_response_model(user)

    async def delete_user_service(self, user_id: int) -> str:
        user: User = await self.repo.get_user(user_id)
        return await self.repo.delete_user(user.id)
    
    @staticmethod
    def _to_response_model(user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
        )
class ReportService:
    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo
    
        """Create report from structured response"""
    async def create_report(self, user_id: int, report_content: dict) -> Report:
        return await self.report_repo.create(
            user_id=user_id,
            report_content=report_content
        )
    
    async def get_user_reports(self, user_id: int) -> List[Report]:
        """Get all reports for a user"""
        return await self.report_repo.get_by_user_id(user_id)

    async def get_lastest_report(self, user_id) -> Report:
        return await self.report_repo.get_latest_user_report(user_id=user_id)

    async def delete_report(self, report_id: int) -> str:
        """Delete a report by ID"""
        return await self.report_repo.delete(report_id)

    def _format_stats_to_text(self, stats_data: dict) -> str:
        """Convert JSON stats to human-readable text for the agent"""
        overview = stats_data.get("overview", {})
        geral = stats_data.get("geral", {})
        
        # Build the text report
        text_parts = []
        
        # General statistics
        text_parts.append("=== GENERAL STATISTICS ===")
        text_parts.append(f"Total Transactions: {geral.get('total_transactions', 0):,}")
        text_parts.append(f"Fraudulent Transactions: {geral.get('fraudulent_transactions', 0):,}")
        text_parts.append(f"Fraud Rate: {geral.get('fraud_rate', 0)}%")
        text_parts.append(f"Transaction Amount Range: ${geral.get('min_amount', 0):.2f} - ${geral.get('max_amount', 0):,.2f}")
        text_parts.append(f"Average Transaction Amount: ${geral.get('avg_amount', 0):,.2f}")
        text_parts.append("")
        
        # Country statistics
        text_parts.append("=== COUNTRY BREAKDOWN ===")
        countries = overview.get("countries", {})
        for country, stats in countries.items():
            fraud_rate = (stats['fraud_transactions'] / stats['total_transactions'] * 100) if stats['total_transactions'] > 0 else 0
            text_parts.append(
                f"{country}: {stats['total_transactions']:,} transactions, "
                f"{stats['fraud_transactions']:,} fraudulent ({fraud_rate:.2f}%)"
            )
        text_parts.append("")
        
        # Merchant category statistics
        text_parts.append("=== MERCHANT CATEGORY ANALYSIS ===")
        merchant_categories = overview.get("merchant_category", {})
        for category, stats in merchant_categories.items():
            fraud_rate = (stats['fraud_transactions'] / stats['total_transactions'] * 100) if stats['total_transactions'] > 0 else 0
            text_parts.append(
                f"{category}: {stats['total_transactions']:,} transactions, "
                f"{stats['fraud_transactions']:,} fraudulent ({fraud_rate:.2f}%)"
            )
        text_parts.append("")
        
        # Device statistics
        text_parts.append("=== DEVICE TYPE ANALYSIS ===")
        devices = overview.get("device", {})
        for device, stats in devices.items():
            fraud_rate = (stats['fraud_transactions'] / stats['total_transactions'] * 100) if stats['total_transactions'] > 0 else 0
            text_parts.append(
                f"{device}: {stats['total_transactions']:,} transactions, "
                f"{stats['fraud_transactions']:,} fraudulent ({fraud_rate:.2f}%)"
            )
        text_parts.append("")
        
        # Channel statistics
        text_parts.append("=== CHANNEL DISTRIBUTION ===")
        channels = overview.get("channel", {})
        for channel, stats in channels.items():
            fraud_rate = (stats['fraud_transactions'] / stats['total_transactions'] * 100) if stats['total_transactions'] > 0 else 0
            text_parts.append(
                f"{channel.upper()}: {stats['total_transactions']:,} transactions, "
                f"{stats['fraud_transactions']:,} fraudulent ({fraud_rate:.2f}%)"
            )
        text_parts.append("")
        
        # High risk merchant analysis
        text_parts.append("=== HIGH RISK MERCHANT ANALYSIS ===")
        high_risk = overview.get("high_risk_merchant", {})
        for risk_level, stats in high_risk.items():
            risk_label = "High Risk" if risk_level == "true" else "Low Risk"
            fraud_rate = (stats['fraud_transactions'] / stats['total_transactions'] * 100) if stats['total_transactions'] > 0 else 0
            text_parts.append(
                f"{risk_label}: {stats['total_transactions']:,} transactions, "
                f"{stats['fraud_transactions']:,} fraudulent ({fraud_rate:.2f}%)"
            )
        text_parts.append("")
        
        # Distance from home analysis
        text_parts.append("=== DISTANCE FROM HOME ANALYSIS ===")
        distance = overview.get("distance_from_home", {})
        for dist_key, stats in distance.items():
            location = "Home" if dist_key == "0" else "Away from Home"
            fraud_rate = (stats['fraud_transactions'] / stats['total_transactions'] * 100) if stats['total_transactions'] > 0 else 0
            text_parts.append(
                f"{location}: {stats['total_transactions']:,} transactions, "
                f"{stats['fraud_transactions']:,} fraudulent ({fraud_rate:.2f}%)"
            )
        text_parts.append("")
        
        # Weekend vs weekday
        text_parts.append("=== WEEKEND VS WEEKDAY ANALYSIS ===")
        weekend = overview.get("weekend_transaction", {})
        for is_weekend, stats in weekend.items():
            day_type = "Weekend" if is_weekend == "true" else "Weekday"
            fraud_rate = (stats['fraud_transactions'] / stats['total_transactions'] * 100) if stats['total_transactions'] > 0 else 0
            text_parts.append(
                f"{day_type}: {stats['total_transactions']:,} transactions, "
                f"{stats['fraud_transactions']:,} fraudulent ({fraud_rate:.2f}%)"
            )
        text_parts.append("")
        
        # Hourly statistics
        text_parts.append("=== HOURLY TRANSACTION PATTERNS ===")
        hourly_stats = overview.get("hourly_stats", [])
        for hour_data in hourly_stats:
            hour = hour_data['hour']
            fraud_rate = (hour_data['fraud_transactions'] / hour_data['total_transactions'] * 100) if hour_data['total_transactions'] > 0 else 0
            text_parts.append(
                f"Hour {hour:02d}:00: {hour_data['total_transactions']:,} transactions, "
                f"{hour_data['fraud_transactions']:,} fraudulent ({fraud_rate:.2f}%)"
            )
        
        return "\n".join(text_parts)
class AnalysisService:
    def __init__(self, repo: AnalysisRepository):
        self.repo = repo
    
    async def create_analysis(self, user_id: int, transaction_id: str, analysis_content: dict) -> Analysis:
        return await self.repo.create(user_id=user_id, transaction_id=transaction_id, analysis_content=analysis_content)
    
    async def get_analysis(self, transaction_id: str) -> Analysis:
        return await self.repo.get_transaction_id(transaction_id)

    def _format_stats_to_text(self, analysis: dict) -> str:
        """Convert transaction data to human-readable text for the agent"""
        transaction = analysis.get("transaction")

        if not transaction:
            return "No transaction data available for analysis."

        text_parts = []

        text_parts.append("=== TRANSACTION ANALYSIS REQUEST ===")
        text_parts.append(f"Transaction ID: {getattr(transaction, 'transaction_id', 'N/A')}")
        text_parts.append(f"Customer ID: {getattr(transaction, 'customer_id', 'N/A')}")
        text_parts.append(f"Card Number: {getattr(transaction, 'card_number', 'N/A')}")
        text_parts.append(f"Timestamp: {getattr(transaction, 'timestamp', 'N/A')}")
        text_parts.append("")

        text_parts.append("=== TRANSACTION DETAILS ===")
        text_parts.append(f"Merchant: {getattr(transaction, 'merchant', 'N/A')}")
        text_parts.append(f"Merchant Category: {getattr(transaction, 'merchant_category', 'N/A')}")
        text_parts.append(f"Merchant Type: {getattr(transaction, 'merchant_type', 'N/A')}")
        amount = getattr(transaction, 'amount', 0)
        currency = getattr(transaction, 'currency', 'USD')
        text_parts.append(f"Amount: {currency} {amount:,.2f}")
        text_parts.append(f"Country: {getattr(transaction, 'country', 'N/A')}")
        text_parts.append(f"City: {getattr(transaction, 'city', 'N/A')}")
        text_parts.append(f"City Size: {getattr(transaction, 'city_size', 'N/A')}")
        text_parts.append("")

        text_parts.append("=== PAYMENT METHOD ===")
        text_parts.append(f"Card Type: {getattr(transaction, 'card_type', 'N/A')}")
        card_present = getattr(transaction, 'card_present', 0)
        text_parts.append(f"Card Present: {'Yes' if card_present == 1 else 'No'}")
        text_parts.append(f"Device: {getattr(transaction, 'device', 'N/A')}")
        text_parts.append(f"Channel: {getattr(transaction, 'channel', 'N/A')}")
        text_parts.append(f"Device Fingerprint: {getattr(transaction, 'device_fingerprint', 'N/A')}")
        text_parts.append(f"IP Address: {getattr(transaction, 'ip_address', 'N/A')}")
        text_parts.append("")

        text_parts.append("=== RISK FACTORS ===")
        distance_from_home = getattr(transaction, 'distance_from_home', 0)
        text_parts.append(f"Distance from Home: {distance_from_home} units")
        high_risk_merchant = getattr(transaction, 'high_risk_merchant', False)
        text_parts.append(f"High Risk Merchant: {'Yes' if high_risk_merchant else 'No'}")
        transaction_hour = getattr(transaction, 'transaction_hour', 0)
        text_parts.append(f"Transaction Hour: {transaction_hour:02d}:00")
        weekend_transaction = getattr(transaction, 'weekend_transaction', False)
        text_parts.append(f"Weekend Transaction: {'Yes' if weekend_transaction else 'No'}")
        text_parts.append("")

        velocity = getattr(transaction, 'velocity_last_hour', None)
        if velocity:
            text_parts.append("=== VELOCITY ANALYSIS (LAST HOUR) ===")
            text_parts.append(f"Number of Transactions: {getattr(velocity, 'num_transactions', 0):,}")
            text_parts.append(f"Total Amount: {currency} {getattr(velocity, 'total_amount', 0):,.2f}")
            text_parts.append(f"Unique Merchants: {getattr(velocity, 'unique_merchants', 0)}")
            text_parts.append(f"Unique Countries: {getattr(velocity, 'unique_countries', 0)}")
            text_parts.append(f"Maximum Single Amount: {currency} {getattr(velocity, 'max_single_amount', 0):,.2f}")
            text_parts.append("")

        text_parts.append("=== FRAUD ASSESSMENT ===")
        is_fraud = getattr(transaction, 'is_fraud', False)
        text_parts.append(f"Is Fraud: {'Yes' if is_fraud else 'No'}")
        fraud_probability = getattr(transaction, 'fraud_probability', 0)
        text_parts.append(f"Fraud Probability: {fraud_probability:.2%}")
        text_parts.append("")

        text_parts.append("Please analyze this transaction for potential fraud indicators and provide insights about the risk factors present.")

        return "\n".join(text_parts)
