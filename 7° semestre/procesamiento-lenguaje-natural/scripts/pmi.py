from __future__ import annotations
from collections import Counter
from math import log2
import pandas as pd

def unigram_counts(tokens: list[str]) -> Counter[str]:
    """Calcula la frecuencia de cada token (unigrama) en una lista.

    Args:
        tokens (list[str]): Una lista de strings, donde cada string es un token.

    Returns:
        Counter[str]: Un objeto Counter que mapea cada token a su frecuencia.
    """
    return Counter(tokens)

def bigram_counter_from_str_keys(counter_str: Counter[str]) -> Counter[tuple[str, str]]:
    """Convierte un Counter con claves 'w1 w2' a uno con claves (w1, w2).

    Esta función de utilidad es útil para procesar contadores de n-gramas
    cuyas claves son strings, transformándolas a tuplas que son más
    fáciles de manejar programáticamente.

    Args:
        counter_str (Counter[str]): Un Counter donde las claves son strings
            de bigramas separados por un espacio (ej: "palabra1 palabra2").

    Returns:
        Counter[tuple[str, str]]: Un nuevo Counter donde las claves son tuplas
            de dos strings (ej: ("palabra1", "palabra2")).
    """
    out: Counter[tuple[str, str]] = Counter()
    for key, f in counter_str.items():
        parts = key.split(" ")
        if len(parts) == 2:
            out[(parts[0], parts[1])] = f
    return out

def probabilities(tokens: list[str], bigram_c: Counter[tuple[str, str]]):
    """Calcula las probabilidades de unigramas y bigramas.

    Args:
        tokens (list[str]): La lista completa de tokens del corpus.
        bigram_c (Counter[tuple[str, str]]): Un contador con la frecuencia
            de cada bigrama.

    Returns:
        tuple[dict, dict]: Una tupla con dos diccionarios:
        - El primero mapea cada unigrama a su probabilidad P(w).
        - El segundo mapea cada bigrama a su probabilidad P(w1, w2).
    """
    N = len(tokens)
    if N == 0:
        return {}, {}

    uni_c = unigram_counts(tokens)
    p_uni = {w: uni_c[w] / N for w in uni_c}

    # El número de posibles bigramas es N-1
    denom = max(1, N - 1)
    p_bi = {bg: bigram_c[bg] / denom for bg in bigram_c}

    return p_uni, p_bi

def pmi_df(
    tokens: list[str],
    bigram_c: Counter[tuple[str, str]],
    min_freq: int = 1
) -> pd.DataFrame:
    """Calcula la Información Mutua Puntual (PMI) para una lista de bigramas.

    La PMI mide la asociación entre dos eventos. Un valor alto de PMI
    indica que las dos palabras del bigrama tienden a co-ocurrir más
    frecuentemente de lo que se esperaría por azar. La fórmula es:
    PMI(w1, w2) = log2( P(w1, w2) / (P(w1) * P(w2)) )

    Args:
        tokens (list[str]): La lista completa de tokens del corpus.
        bigram_c (Counter[tuple[str, str]]): Un contador con la frecuencia
            de cada bigrama.
        min_freq (int, optional): Frecuencia mínima que debe tener un bigrama
            para ser incluido en el cálculo. Por defecto es 1.

    Returns:
        pd.DataFrame: Un DataFrame de pandas con las columnas "w1", "w2",
            "freq" y "pmi", ordenado descendentemente por PMI y frecuencia.
    """
    p_uni, p_bi = probabilities(tokens, bigram_c)
    rows = []

    for (w1, w2), f in bigram_c.items():
        if f < min_freq:
            continue

        px, py = p_uni.get(w1, 0.0), p_uni.get(w2, 0.0)
        pxy = p_bi.get((w1, w2), 0.0)

        # Asegurarse de que las probabilidades no son cero para evitar errores
        if px > 0 and py > 0 and pxy > 0:
            pmi_val = log2(pxy / (px * py))
            rows.append((w1, w2, f, pmi_val))

    df = pd.DataFrame(
        rows, columns=["w1", "w2", "freq", "pmi"]
    ).sort_values(["pmi", "freq"], ascending=[False, False])

    return df.reset_index(drop=True)