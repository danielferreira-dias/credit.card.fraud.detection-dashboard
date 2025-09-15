import pandas as pd
import json
import ast

def remover_duplicados_csv(clean_csv: str, save: bool = False) -> pd.DataFrame:
    """
    Reads .csv excel file and removes the duplicated rows

    Args:
        clean_csv (str): Path.
        save (bool): If true, save in the same path as '_clean'.

    Returns:-
        pd.DataFrame: DataFrame sem duplicados.
    """
    df = pd.read_csv(clean_csv)

    # Remove duplicates
    df_non_duplicates = df.drop_duplicates(subset="transaction_id", keep="first")

    # Convert velocity_last_hour from Python dict string to JSON
    if 'velocity_last_hour' in df_non_duplicates.columns:
        def convert_to_json(value):
            if pd.isna(value) or value == '':
                return None
            try:
                # Convert Python dict string to actual dict, then to JSON
                dict_obj = ast.literal_eval(str(value))
                return json.dumps(dict_obj)
            except (ValueError, SyntaxError):
                return None

        df_non_duplicates['velocity_last_hour'] = df_non_duplicates['velocity_last_hour'].apply(convert_to_json)

    # Save
    if save:
        clean_path = clean_csv.replace(".csv", "_clean.csv")
        df_non_duplicates.to_csv(clean_path, index=False)
        print(f"File saved: {clean_path}")

    return df_non_duplicates

if __name__ == "__main__":
    remover_duplicados_csv("./synthetic_fraud_data.csv", True)