import pandas as pd
import ast
import json

# Lê o CSV com a string errada
df = pd.read_csv("./synthetic_fraud_data.csv")

df = df.drop_duplicates(subset=["transaction_id"])

# Corrige a coluna 'velocity_last_hour'
df["velocity_last_hour"] = df["velocity_last_hour"].apply(ast.literal_eval)  # ← transforma string em dict
df["velocity_last_hour"] = df["velocity_last_hour"].apply(json.dumps)        # ← transforma dict em JSON válido

# Salva novo ficheiro CSV
df.to_csv("cleaned_synthetic_fraud_data.csv", index=False)