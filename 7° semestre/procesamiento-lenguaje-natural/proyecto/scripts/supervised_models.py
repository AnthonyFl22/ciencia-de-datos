# proyecto/scripts/supervised_models.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
)

import joblib


@dataclass
class SupervisedConfig:
    test_size: float = 0.2
    random_state: int = 42
    max_features: int = 20000
    min_df: int = 5
    max_df: float = 0.9
    ngram_range: Tuple[int, int] = (1, 2)  # unigrams + bigrams
    model_type: str = "logreg"  # "logreg", "svm", "nb"


# ============================================================
# 1. Construcción de features
# ============================================================

def build_text_vectorizer(cfg: SupervisedConfig) -> TfidfVectorizer:
    """
    Vectorizador TF-IDF estándar para inglés, asumiendo texto ya preprocesado.
    """
    vect = TfidfVectorizer(
        max_features=cfg.max_features,
        min_df=cfg.min_df,
        max_df=cfg.max_df,
        ngram_range=cfg.ngram_range,
    )
    return vect


def fit_transform_text(
    train_texts: List[str],
    test_texts: List[str],
    cfg: SupervisedConfig,
) -> Tuple[csr_matrix, csr_matrix, TfidfVectorizer]:
    """
    Ajusta el TF-IDF en train y transforma train/test.
    """
    vect = build_text_vectorizer(cfg)
    X_train_text = vect.fit_transform(train_texts)
    X_test_text = vect.transform(test_texts)
    return X_train_text, X_test_text, vect


def build_numeric_features(
    df: pd.DataFrame,
    numeric_cols: List[str],
) -> csr_matrix:
    """
    Construye una matriz CSR con features numéricos a partir de columnas del DataFrame.
    """
    if not numeric_cols:
        # matriz vacía con filas = len(df)
        return csr_matrix((len(df), 0))

    mat = df[numeric_cols].astype(float).values
    return csr_matrix(mat)


def combine_features(
    X_text: csr_matrix,
    X_numeric: csr_matrix,
) -> csr_matrix:
    """
    Combina features textuales (sparse) y numéricos (sparse) con hstack.
    """
    if X_numeric.shape[1] == 0:
        return X_text
    return hstack([X_text, X_numeric])


# ============================================================
# 2. Creación de modelos
# ============================================================

def build_model(cfg: SupervisedConfig):
    """
    Construye un modelo supervisado según cfg.model_type.
    """
    if cfg.model_type == "logreg":
        model = LogisticRegression(
            max_iter=1000,
            random_state=cfg.random_state,
        )
    elif cfg.model_type == "svm":
        model = LinearSVC(
            random_state=cfg.random_state,
        )
    elif cfg.model_type == "nb":
        model = MultinomialNB()
    else:
        raise ValueError(f"Modelo no soportado: {cfg.model_type}")

    return model


# ============================================================
# 3. Entrenamiento y evaluación
# ============================================================

def train_test_split_df(
    df: pd.DataFrame,
    label_col: str,
    test_size: float,
    random_state: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Hace un split estratificado por la columna label_col.
    """
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df[label_col],
    )
    return train_df, test_df


def evaluate_binary_classifier(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Dict[str, Any]:
    """
    Devuelve métricas para clasificación binaria.
    """
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1
    )
    report = classification_report(y_true, y_pred, digits=3)

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "report": report,
    }


# ============================================================
# 4. Guardar / cargar modelo y vectorizador
# ============================================================

def save_model_and_vectorizer(
    model,
    vectorizer: TfidfVectorizer,
    numeric_cols: List[str],
    path: str,
):
    """
    Guarda modelo, vectorizador y metainfo (numeric_cols) con joblib.
    """
    obj = {
        "model": model,
        "vectorizer": vectorizer,
        "numeric_cols": numeric_cols,
    }
    joblib.dump(obj, path)


def load_model_and_vectorizer(path: str):
    """
    Carga modelo y vectorizador.
    """
    obj = joblib.load(path)
    return obj["model"], obj["vectorizer"], obj.get("numeric_cols", [])
