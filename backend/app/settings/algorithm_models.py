import os
import pickle
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'fraud_detection_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'fraud_detection_scaler.pkl')

def load_model():
    return joblib.load(MODEL_PATH)

def load_scaler():
	return joblib.load(SCALER_PATH)