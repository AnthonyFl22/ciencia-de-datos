import pandas as pd

def top_pmi(df: pd.DataFrame, k: int = 10) -> pd.DataFrame:
    """Selecciona los k bigramas con mayor valor de PMI de un DataFrame.

    La función ordena el DataFrame primero por la columna 'pmi' y luego por
    'freq', ambas de forma descendente, para luego devolver las primeras k filas.

    Args:
        df (pd.DataFrame): El DataFrame que contiene los valores de PMI.
            Debe tener las columnas "pmi" y "freq".
        k (int, optional): El número de filas (mejores resultados) a devolver.
            Por defecto es 10.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con los k bigramas de mayor PMI.
    """
    if df.empty:
        return df
    return df.sort_values(
        ["pmi", "freq"], ascending=[False, False]
    ).head(k).reset_index(drop=True)

def save_table(df: pd.DataFrame, path: str) -> None:
    """Guarda un DataFrame de pandas en un archivo CSV.

    Args:
        df (pd.DataFrame): El DataFrame que se va a guardar.
        path (str): La ruta del archivo, incluyendo el nombre y la extensión .csv,
            donde se guardará el DataFrame.

    Returns:
        None
    """
    df.to_csv(path, index=False)