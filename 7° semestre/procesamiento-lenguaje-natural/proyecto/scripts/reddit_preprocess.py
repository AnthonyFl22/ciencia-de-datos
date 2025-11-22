# proyecto/scripts/reddit_preprocess.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from text_preprocess import preprocess_text, tokenize_words


@dataclass
class RedditPreprocessConfig:
    """
    Configuración para el preprocesamiento de comentarios de Reddit.
    """
    path: Path                     # ruta al archivo bruto (csv / parquet / json)
    text_col: str = "body"         # columna de texto original
    created_col: str = "created_utc"  # columna con la fecha/hora
    id_col: Optional[str] = "id"   # id del comentario (opcional)
    min_text_len: int = 3          # longitud mínima de texto (en caracteres)


def load_raw_reddit(cfg: RedditPreprocessConfig) -> pd.DataFrame:
    """
    Carga el archivo bruto de Reddit según la configuración.
    Soporta .csv, .parquet y .json (lines).
    """
    path = cfg.path
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    suffix = path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix == ".parquet":
        df = pd.read_parquet(path)
    elif suffix == ".json":
        # asumiendo formato jsonl
        df = pd.read_json(path, lines=True)
    else:
        raise ValueError(f"Extensión no soportada: {suffix}")

    return df


def basic_clean(df: pd.DataFrame, cfg: RedditPreprocessConfig) -> pd.DataFrame:
    """
    Limpieza básica:
      - Mantener solo columnas relevantes.
      - Eliminar NaN, [removed], [deleted] y textos demasiado cortos.
      - Quitar duplicados.
      - Construir columnas de fecha: created_dt, date, year, month, year_month.
    """
    df = df.copy()

    # Seleccionar solo columnas que nos interesan
    cols_keep: List[str] = []
    for col in [cfg.id_col, cfg.text_col, cfg.created_col, "score"]:
        if col is not None and col in df.columns:
            cols_keep.append(col)

    df = df[cols_keep]

    # Quitar NaN en texto
    df = df.dropna(subset=[cfg.text_col])

    # Quitar [removed], [deleted], vacíos
    invalid_texts = {"[removed]", "[deleted]", ""}
    df = df[~df[cfg.text_col].astype(str).str.strip().isin(invalid_texts)]

    # Quitar textos muy cortos
    df = df[df[cfg.text_col].astype(str).str.len() >= cfg.min_text_len]

    # Quitar duplicados por texto (y por id si existe)
    subset_dup = [cfg.text_col]
    if cfg.id_col is not None and cfg.id_col in df.columns:
        subset_dup.append(cfg.id_col)

    df = df.drop_duplicates(subset=subset_dup)

    # Manejar fechas
    if cfg.created_col in df.columns:
        # Si es numérico, asumimos timestamp en segundos
        if pd.api.types.is_numeric_dtype(df[cfg.created_col]):
            df["created_dt"] = pd.to_datetime(
                df[cfg.created_col],
                unit="s",
                errors="coerce",
            )
        else:
            df["created_dt"] = pd.to_datetime(
                df[cfg.created_col],
                errors="coerce",
            )
    else:
        df["created_dt"] = pd.NaT

    df = df.dropna(subset=["created_dt"])

    df["date"] = df["created_dt"].dt.date
    df["year"] = df["created_dt"].dt.year
    df["month"] = df["created_dt"].dt.month
    df["year_month"] = df["created_dt"].dt.to_period("M").astype(str)

    return df


EXTRA_STOPWORDS = {
    # Residuos de contracciones en inglés: it's, don't, I'm, I've, etc.
    "s", "t", "m", "ve", "don",

    # Ruido típico de URLs
    "https", "http", "com",
}

# Conjunto final de stopwords: sklearn + extras
CUSTOM_STOPWORDS = ENGLISH_STOP_WORDS.union(EXTRA_STOPWORDS)


def _remove_stopwords(tokens: List[str]) -> List[str]:
    """
    Elimina stopwords en inglés usando ENGLISH_STOP_WORDS de scikit-learn
    + una lista de extras. Además:
      - Elimina letras sueltas alfabéticas (e.g. 's', 't', 'a', 'b').
      - Elimina tokens que sean solo dígitos (e.g. '1', '2', '2020').

    Se asume que los tokens ya vienen en minúsculas gracias a preprocess_text.
    """
    cleaned: List[str] = []

    for t in tokens:
        t = str(t).lower()

        # 1) Stopwords (sklearn + extras)
        if t in CUSTOM_STOPWORDS:
            continue

        # 2) Letras sueltas alfabéticas (ruido)
        if len(t) == 1 and t.isalpha():
            continue

        # 3) Tokens numéricos puros (opcional, para este proyecto no aportan mucho)
        if t.isdigit():
            continue

        cleaned.append(t)

    return cleaned


def add_text_features(df: pd.DataFrame, cfg: RedditPreprocessConfig) -> pd.DataFrame:
    """
    Aplica limpieza de texto y tokenización usando las funciones existentes:
      - preprocess_text(s) -> str limpio
      - tokenize_words(s)  -> List[str] tokens
    Luego:
      - Genera tokens_no_stop eliminando stopwords en inglés.
      - Calcula longitudes (n_tokens, n_tokens_no_stop, n_chars).
    """
    df = df.copy()

    # Texto limpio
    df["text_clean"] = df[cfg.text_col].astype(str).apply(preprocess_text)

    # Tokens
    df["tokens"] = df["text_clean"].apply(tokenize_words)

    # Tokens sin stopwords (en minúsculas por preprocess_text)
    df["tokens_no_stop"] = df["tokens"].apply(_remove_stopwords)

    # Longitudes
    df["n_tokens"] = df["tokens"].apply(len)
    df["n_tokens_no_stop"] = df["tokens_no_stop"].apply(len)
    df["n_chars"] = df[cfg.text_col].astype(str).str.len()

    return df


def build_reddit_clean_df(cfg: RedditPreprocessConfig) -> pd.DataFrame:
    """
    Pipeline completo de Bloque 1:
      1) Carga datos brutos.
      2) Limpieza básica.
      3) Features de texto (text_clean, tokens, tokens_no_stop, longitudes).
    Devuelve df_clean listo para guardar en data_processed.
    """
    df_raw = load_raw_reddit(cfg)
    df_clean = basic_clean(df_raw, cfg)
    df_clean = add_text_features(df_clean, cfg)
    return df_clean
