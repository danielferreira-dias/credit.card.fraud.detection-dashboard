from app.database.transactions_db import TransactionsDB
from typing import List, Dict, Any, Optional
import sqlite3

class ProviderService:
    def __init__(self, db: TransactionsDB):
        """
            This service will estabilish a direct connection with the mocking database,
            In this case, a temporary SQLite Database.
            This connection will provide the Agent with knowledge about the database data;
        """
        self.db = db

    def get_connection(self):
        """Get database connection through the TransactionsDB instance"""
        return self.db.get_connection()

    async def get_all_transactions(self, limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
        """Get all transactions from the database"""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM transactions LIMIT {limit} OFFSET {skip}")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_transaction_by_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific transaction by ID"""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    async def get_transactions_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all transactions for a specific customer"""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE customer_id = ? ORDER BY timestamp DESC", (customer_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_fraud_transactions(self) -> List[Dict[str, Any]]:
        """Get all fraudulent transactions"""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE is_fraud = 1 ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_transaction_stats(self) -> Dict[str, Any]:
        """Get basic statistics about transactions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total transactions
            cursor.execute("SELECT COUNT(*) FROM transactions")
            total_count = cursor.fetchone()[0]

            # Fraud transactions
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE is_fraud = 1")
            fraud_count = cursor.fetchone()[0]

            # Average amount
            cursor.execute("SELECT AVG(amount) FROM transactions")
            avg_amount = cursor.fetchone()[0]

            # Total amount
            cursor.execute("SELECT SUM(amount) FROM transactions")
            total_amount = cursor.fetchone()[0]

            return {
                "total_transactions": total_count,
                "fraud_transactions": fraud_count,
                "fraud_rate": (fraud_count / total_count * 100) if total_count > 0 else 0,
                "average_amount": avg_amount,
                "total_amount": total_amount
            }