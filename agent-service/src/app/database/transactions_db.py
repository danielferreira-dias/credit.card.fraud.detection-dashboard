import sqlite3
import os
from typing import Optional

class TransactionsDB:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'transactions.db')
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with transactions table mimicking PostgreSQL structure"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create transactions table matching PostgreSQL Transaction model
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    card_number TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    merchant_category TEXT,
                    merchant_type TEXT,
                    merchant TEXT,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    country TEXT,
                    city TEXT,
                    city_size TEXT,
                    card_type TEXT,
                    card_present INTEGER DEFAULT 0,
                    device TEXT,
                    channel TEXT,
                    device_fingerprint TEXT,
                    ip_address TEXT,
                    distance_from_home INTEGER,
                    high_risk_merchant INTEGER DEFAULT 0,
                    transaction_hour INTEGER,
                    weekend_transaction INTEGER DEFAULT 0,
                    velocity_last_hour TEXT,
                    is_fraud INTEGER DEFAULT 0
                )
            """)

            # Create index on transaction_id for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transaction_id
                ON transactions(transaction_id)
            """)

            # Create index on customer_id for customer-based queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_customer_id
                ON transactions(customer_id)
            """)

            # Create index on timestamp for time-based queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON transactions(timestamp)
            """)

            conn.commit()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

# Initialize database instance
db = TransactionsDB()