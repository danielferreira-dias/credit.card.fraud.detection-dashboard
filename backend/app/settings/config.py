import os

class Settings:
    PROJECT_NAME: str = "Credit Card Fraud Detection API"
    ENV: str = os.getenv("ENV", "dev")  # dev | prod
    LOG_LEVEL: str = "DEBUG" if ENV == "dev" else "INFO"

settings = Settings()