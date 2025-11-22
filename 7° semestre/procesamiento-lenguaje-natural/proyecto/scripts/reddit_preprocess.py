# proyecto/scripts/reddit_preprocess.py

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import pandas as pd

from text_preprocess import preprocess_text, tokenize_words


@dataclass
class RedditPreprocessConfig:
    path: Path
    text_col: str = "body"           # columna de texto bruto
    created_col: str = "created_utc" # timestamp o fecha
    id_col: Optional[str] = "id"     # opcional
    min_text_len: int = 3            # mínimo de caracteres para conservar


def load_raw_reddit(cfg: RedditPreprocessConfig) -> pd.DataFrame:
    """Carga el archivo bruto de Reddit según la config."""
    path = cfg.path
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    if path.suffix.lower() in {".csv"}:
        df = pd.read_csv(path)
    elif path.suffix.lower() in {".parquet"}:
        df = pd.read_parquet(path)
    elif path.suffix.lower() in {".json"}:
        df = pd.read_json(path, lines=True)
    else:
        raise ValueError(f"Extensión no soportada: {path.suffix}")

    return df


def basic_clean(df: pd.DataFrame, cfg: RedditPreprocessConfig) -> pd.DataFrame:
    """Limpieza básica: quitar vacíos, [removed], duplicados y construir fechas."""
    df = df.copy()

    # Mantener solo columnas que nos interesan (si existen)
    cols_keep: List[str] = []
    for col in [cfg.id_col, cfg.text_col, cfg.created_col, "score"]:
        if col is not None and col in df.columns:
            cols_keep.append(col)
    df = df[cols_keep]

    # Quitar NaN en texto
    df = df.dropna(subset=[cfg.text_col])

    # Quitar [removed], [deleted], etc.
    df = df[~df[cfg.text_col].astype(str).str.strip().isin(["[removed]", "[deleted]", ""])]

    # Quitar textos muy cortos
    df = df[df[cfg.text_col].astype(str).str.len() >= cfg.min_text_len]

    # Quitar duplicados por texto (y id si existe)
    subset_dup = [cfg.text_col]
    if cfg.id_col is not None and cfg.id_col in df.columns:
        subset_dup.append(cfg.id_col)
    df = df.drop_duplicates(subset=subset_dup)

    # Manejar fechas
    if cfg.created_col in df.columns:
        df["created_dt"] = pd.to_datetime(df[cfg.created_col], unit="s", errors="coerce") \
                           if pd.api.types.is_numeric_dtype(df[cfg.created_col]) \
                           else pd.to_datetime(df[cfg.created_col], errors="coerce")
    else:
        df["created_dt"] = pd.NaT

    df = df.dropna(subset=["created_dt"])

    df["date"] = df["created_dt"].dt.date
    df["year"] = df["created_dt"].dt.year
    df["month"] = df["created_dt"].dt.month
    df["year_month"] = df["created_dt"].dt.to_period("M").astype(str)

    return df


def add_text_features(df: pd.DataFrame, cfg: RedditPreprocessConfig) -> pd.DataFrame:
    """Aplica preprocess_text y tokenize_words, y agrega columnas útiles."""
    df = df.copy()

    # Texto limpio
    df["text_clean"] = df[cfg.text_col].astype(str).apply(preprocess_text)

    # Tokens (ajusta si tu tokenize_words tiene otra firma)
    df["tokens"] = df["text_clean"].apply(tokenize_words)

    # Longitud
    df["n_tokens"] = df["tokens"].apply(len)
    df["n_chars"] = df[cfg.text_col].astype(str).str.len()

    # Por ahora usamos tokens como tokens_no_stop; si luego haces stopwords,
    # aquí agregamos df["tokens_no_stop"]
    df["tokens_no_stop"] = df["tokens"]

    return df


def build_reddit_clean_df(cfg: RedditPreprocessConfig) -> pd.DataFrame:
    """Pipeline completo: carga, limpieza básica y features de texto."""
    df_raw = load_raw_reddit(cfg)
    df_clean = basic_clean(df_raw, cfg)
    df_clean = add_text_features(df_clean, cfg)
    return df_clean
