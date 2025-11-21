from pathlib import Path
import pandas as pd

def read_titles_csv(path: str | Path, title_col: str = "title") -> list[str]:
    """Lee una columna específica de un archivo CSV y la devuelve como una lista.

    Esta función abre un archivo CSV, verifica la existencia de una columna
    y extrae sus valores, eliminando cualquier fila nula y asegurando
    que todos los datos sean de tipo string.

    Args:
        path (str | Path): La ruta al archivo CSV que se va a leer.
        title_col (str, optional): El nombre de la columna que contiene los títulos.
            Por defecto es "title".

    Returns:
        list[str]: Una lista con los títulos extraídos del archivo.

    Raises:
        ValueError: Si la columna especificada en `title_col` no se encuentra
            en el archivo CSV.
    """
    df = pd.read_csv(path)
    if title_col not in df.columns:
        raise ValueError(
            f"Columna '{title_col}' no encontrada en {path}. "
            f"Columnas disponibles: {list(df.columns)}"
        )
    return df[title_col].dropna().astype(str).tolist()

def join_titles(titles: list[str]) -> str:
    """Concatena una lista de títulos en un único string separado por espacios.

    Args:
        titles (list[str]): La lista de títulos (strings) que se van a unir.

    Returns:
        str: Un único string que resulta de unir todos los títulos.
    """
    return " ".join(titles)