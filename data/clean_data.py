import pandas as pd

def remover_duplicados_csv(caminho_csv: str, guardar: bool = False) -> pd.DataFrame:
    """
    Lê um ficheiro .csv, remove duplicados e (opcionalmente) guarda o ficheiro limpo.

    Args:
        caminho_csv (str): Caminho para o ficheiro CSV.
        guardar (bool): Se True, guarda o ficheiro limpo no mesmo local com sufixo '_limpo'.

    Returns:
        pd.DataFrame: DataFrame sem duplicados.
    """
    # Lê o CSV
    df = pd.read_csv(caminho_csv)

    # Remove duplicados
    df_sem_duplicados = df.drop_duplicates()

    # Guarda se for necessário
    if guardar:
        caminho_limpo = caminho_csv.replace(".csv", "_limpo.csv")
        df_sem_duplicados.to_csv(caminho_limpo, index=False)
        print(f"Ficheiro limpo guardado em: {caminho_limpo}")

    return df_sem_duplicados