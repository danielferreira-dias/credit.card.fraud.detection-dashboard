import os
import joblib

BASE_DIR = "/app"  # Diretório base dentro do container

MODEL_PATH = os.path.join(BASE_DIR, "models", "fraud_detection_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "fraud_detection_scaler.pkl")

def load_model():
    return joblib.load(MODEL_PATH)

def load_scaler():
    return joblib.load(SCALER_PATH)