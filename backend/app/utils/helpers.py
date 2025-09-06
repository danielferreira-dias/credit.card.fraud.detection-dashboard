import pandas as pd
from app.models.transaction_model import FEATURE_COLUMNS

def features_to_df(features: dict) -> pd.DataFrame:
    """
    features: dicionário com os nomes EXACTOS acima.
    """
    df = pd.DataFrame([features])
    # força a ordem e garante que todas as colunas existem
    df = df.reindex(columns=FEATURE_COLUMNS)
    return df