from __future__ import annotations
from pathlib import Path
import pandas as pd
from typing import Dict, Iterable, Tuple, Any, List
import json


# -------------------------------------------------------------
# Tipo de dato para el léxico VAD
# -------------------------------------------------------------
VADLexicon = Dict[str, Tuple[float, float, float]]  # word -> (valence, arousal, dominance)


# -------------------------------------------------------------
# 1. Cargar léxico NRC-VAD
# -------------------------------------------------------------
def load_nrc_vad_lexicon(path: Path) -> VADLexicon:
    df = pd.read_csv(path, sep="\t", comment="#")
    df.columns = [c.lower() for c in df.columns]

    # Asegurar columna "word"
    if "word" not in df.columns:
        # detecta cualquier columna que comience con "word"
        word_cols = [c for c in df.columns if "word" in c]
        if not word_cols:
            raise ValueError(f"No se encontró columna 'word'. Columnas: {df.columns.tolist()}")
        df = df.rename(columns={word_cols[0]: "word"})

    df["word"] = df["word"].astype(str).str.lower()

    # Asegurar columnas VAD
    required = ["valence", "arousal", "dominance"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Falta columna {col} en el léxico NRC-VAD")

    lexicon = {
        row["word"]: (float(row["valence"]), float(row["arousal"]), float(row["dominance"]))
        for _, row in df.iterrows()
    }
    return lexicon


# -------------------------------------------------------------
# 2. Adaptar léxico al dominio LoL (neutralizar palabras)
# -------------------------------------------------------------
def adapt_vad_lexicon_for_lol(
    vad_lexicon: VADLexicon,
    game_words_path: Path,
) -> VADLexicon:

    with open(game_words_path, "r", encoding="utf-8") as f:
        game_words = set(json.load(f))

    new_lex = dict(vad_lexicon)

    for w in game_words:
        if w in new_lex:
            # mantener arousal & dominance, neutralizar valence
            _, a, d = new_lex[w]
            new_lex[w] = (0.0, a, d)

    return new_lex


# -------------------------------------------------------------
# 3. Calcular VAD por comentario
# -------------------------------------------------------------
def vad_scores_for_tokens(tokens: Iterable[str], lexicon: VADLexicon) -> Dict[str, float]:
    vals, aros, doms = [], [], []

    for w in tokens:
        w = str(w).lower()
        if w in lexicon:
            v, a, d = lexicon[w]
            vals.append(v)
            aros.append(a)
            doms.append(d)

    if not vals:
        return {
            "vad_valence_mean": 0.0,
            "vad_arousal_mean": 0.0,
            "vad_dominance_mean": 0.0,
        }

    return {
        "vad_valence_mean": sum(vals) / len(vals),
        "vad_arousal_mean": sum(aros) / len(aros),
        "vad_dominance_mean": sum(doms) / len(doms),
    }


def apply_vad_to_dataframe(
    df: pd.DataFrame,
    tokens_col: str,
    lexicon: VADLexicon,
) -> pd.DataFrame:

    def row_vad(toks: Any) -> Dict[str, float]:
        if not isinstance(toks, (list, tuple)):
            return {
                "vad_valence_mean": 0.0,
                "vad_arousal_mean": 0.0,
                "vad_dominance_mean": 0.0,
            }
        return vad_scores_for_tokens(toks, lexicon)

    vad_series = df[tokens_col].apply(row_vad)
    vad_df = pd.json_normalize(vad_series)

    return pd.concat([df, vad_df], axis=1)
