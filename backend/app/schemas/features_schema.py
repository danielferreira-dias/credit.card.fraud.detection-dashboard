import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

FEATURE_COLUMNS = [
    "channel_medium","device_Android App","device_Safari","device_Firefox",
    "USD_converted_total_amount","device_Chrome","device_iOS App","city_Unknown City",
    "country_USA","country_Australia","country_Germany","country_UK","country_Canada",
    "country_Japan","country_France","device_Edge","country_Singapore","channel_mobile",
    "country_Nigeria","country_Brazil","country_Russia","country_Mexico","is_off_hours",
    "max_single_amount","USD_converted_amount","channel_web","is_high_amount","is_low_amount",
    "transaction_hour","hour","device_NFC Payment","device_Magnetic Stripe","device_Chip Reader",
    "high_risk_transaction","channel_pos","card_present","suspicious_device","distance_from_home"
]

conversion_rates = {
    'EUR': 1.06,
    'CAD': 0.72,
    'RUB': 0.01,
    'NGN': 0.0006,
    'SGD': 0.75,
    'MXN': 0.049,
    'BRL': 0.17,
    'AUD': 0.65,
    'JPY': 0.0065,
    'USD': 1.0
}

KEYMAP = {
    "device_android_app": "device_Android App",
    "device_ios_app": "device_iOS App",
    "device_safari": "device_Safari",
    "device_firefox": "device_Firefox",
    "device_chrome": "device_Chrome",
    "device_edge": "device_Edge",
    "device_nfc_payment": "device_NFC Payment",
    "device_magnetic_stripe": "device_Magnetic Stripe",
    "device_chip_reader": "device_Chip Reader",
    "usd_converted_total_amount": "USD_converted_total_amount",
    "usd_converted_amount": "USD_converted_amount",
    "city_unknown_city": "city_Unknown City",
    "country_usa": "country_USA",
    "country_australia": "country_Australia",
    "country_germany": "country_Germany",
    "country_uk": "country_UK",
    "country_canada": "country_Canada",
    "country_japan": "country_Japan",
    "country_france": "country_France",
    "country_singapore": "country_Singapore",
}

class TransactionFeatures(BaseModel):
    """Schema representing the features used for transaction fraud prediction."""
    
    model_config = dict(populate_by_name=True)
    channel_medium: int = Field(alias="channel_medium")
    device_android_app: int = Field(alias="device_Android App")
    device_safari: int = Field(alias="device_Safari")
    device_firefox: int = Field(alias="device_Firefox")
    usd_converted_total_amount: float = Field(alias="USD_converted_total_amount")
    device_chrome: int = Field(alias="device_Chrome")
    device_ios_app: int = Field(alias="device_iOS App")
    city_unknown_city: int = Field(alias="city_Unknown City")
    country_usa: int = Field(alias="country_USA")
    country_australia: int = Field(alias="country_Australia")
    country_germany: int = Field(alias="country_Germany")
    country_uk: int = Field(alias="country_UK")
    country_canada: int = Field(alias="country_Canada")
    country_japan: int = Field(alias="country_Japan")
    country_france: int = Field(alias="country_France")
    device_edge: int = Field(alias="device_Edge")
    country_singapore: int = Field(alias="country_Singapore")
    channel_mobile: int = Field(alias="channel_mobile")
    country_nigeria: int = Field(alias="country_Nigeria")
    country_brazil: int = Field(alias="country_Brazil")
    country_russia: int = Field(alias="country_Russia")
    country_mexico: int = Field(alias="country_Mexico")
    is_off_hours: int = Field(alias="is_off_hours")
    max_single_amount: float = Field(alias="max_single_amount")
    usd_converted_amount: float = Field(alias="USD_converted_amount")
    channel_web: int = Field(alias="channel_web")
    is_high_amount: int = Field(alias="is_high_amount")
    is_low_amount: int = Field(alias="is_low_amount")
    transaction_hour: int = Field(alias="transaction_hour")
    hour: int = Field(alias="hour")
    device_nfc_payment: int = Field(alias="device_NFC Payment")
    device_magnetic_stripe: int = Field(alias="device_Magnetic Stripe")
    device_chip_reader: int = Field(alias="device_Chip Reader")
    high_risk_transaction: int = Field(alias="high_risk_transaction")
    channel_pos: int = Field(alias="channel_pos")
    suspicious_device: int = Field(alias="suspicious_device")
    card_present: int = Field(alias="card_present")
    distance_from_home: int = Field(alias="distance_from_home")

    def to_numpy(self) -> np.ndarray:
        """Converte para NumPy array 2D (1, N) na ordem de FEATURE_COLUMNS."""
        data = self.model_dump(by_alias=True)
        ordered = [data[col] for col in FEATURE_COLUMNS]
        return np.array([ordered], dtype=float)

    def to_dataframe(self) -> pd.DataFrame:
        """Converte para DataFrame com colunas ordenadas."""
        data = self.model_dump(by_alias=True)
        return pd.DataFrame([data], columns=FEATURE_COLUMNS)