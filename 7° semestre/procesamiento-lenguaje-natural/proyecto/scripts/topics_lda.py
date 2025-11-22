# proyecto/scripts/topics_lda.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


@dataclass
class LDAToxicConfig:
    n_topics: int = 8
    max_features: int = 5000
    min_df: int = 20      # término debe aparecer en al menos 20 documentos
    max_df: float = 0.7   # ignorar términos que aparecen en >70% de doks
    random_state: int = 42


def build_vectorizer(cfg: LDAToxicConfig) -> CountVectorizer:
    """
    Construye un CountVectorizer que trabaja con listas de tokens ya preprocesados.
    """
    vectorizer = CountVectorizer(
        tokenizer=lambda x: x,      # ya vienen tokenizados
        preprocessor=lambda x: x,   # no tocar texto
        token_pattern=None,         # necesario si usamos tokenizer personalizado
        max_features=cfg.max_features,
        min_df=cfg.min_df,
        max_df=cfg.max_df,
    )
    return vectorizer


def fit_lda_on_tokens(
    docs_tokens: List[List[str]],
    cfg: LDAToxicConfig,
) -> Tuple[LatentDirichletAllocation, CountVectorizer, any]:
    """
    Ajusta un modelo LDA sobre una lista de documentos tokenizados.
    Devuelve: (modelo_lda, vectorizer, matrix_doc_term)
    """
    vectorizer = build_vectorizer(cfg)
    dt_matrix = vectorizer.fit_transform(docs_tokens)

    lda = LatentDirichletAllocation(
        n_components=cfg.n_topics,
        random_state=cfg.random_state,
        learning_method="batch",
    )
    lda.fit(dt_matrix)

    return lda, vectorizer, dt_matrix


def topics_as_dataframe(
    lda: LatentDirichletAllocation,
    vectorizer: CountVectorizer,
    top_n: int = 15,
) -> pd.DataFrame:
    """
    Devuelve un DataFrame con los tópicos:
      - topic_id
      - rank
      - term
      - weight
    """
    terms = vectorizer.get_feature_names_out()
    rows = []

    for topic_idx, topic in enumerate(lda.components_):
        # components_ es (n_topics, vocab_size)
        top_indices = topic.argsort()[::-1][:top_n]
        for rank, term_idx in enumerate(top_indices, start=1):
            term = terms[term_idx]
            weight = topic[term_idx]
            rows.append(
                {
                    "topic_id": topic_idx,
                    "rank": rank,
                    "term": term,
                    "weight": float(weight),
                }
            )

    return pd.DataFrame(rows)


def dominant_topic_per_doc(
    lda: LatentDirichletAllocation,
    dt_matrix,
) -> List[int]:
    """
    Asigna a cada documento el tópico dominante (mayor probabilidad).
    """
    doc_topic_dist = lda.transform(dt_matrix)  # shape: (n_docs, n_topics)
    dominant = doc_topic_dist.argmax(axis=1)
    return dominant.tolist()
