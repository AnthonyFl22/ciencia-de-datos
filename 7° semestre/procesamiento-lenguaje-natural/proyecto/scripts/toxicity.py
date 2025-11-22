# proyecto/scripts/toxicity.py

from __future__ import annotations
from typing import Iterable, Dict, Any, List, Set, Mapping
from pathlib import Path
import json
import pandas as pd

# =====================================================
# 1. LÉXICOS DE TOXICIDAD
# =====================================================

# Léxico básico (TOKEN EXACTO)
BASIC_TOXIC_WORDS: Set[str] = {
    # Flame genérico y descalificaciones
    "noob", "trash", "garbage", "useless", "dogshit",
    "clown", "troll", "trolling", "feeder", "inting",

    # Insultos directos
    "idiot", "stupid", "moron", "retard",

    # Groserías que pueden ser agresión
    "fuck", "fucking", "shit", "bitch", "asshole",

    # Expresiones agresivas
    "kys", "die", "uninstall",
}

# Léxico avanzado (token → severidad)
ADVANCED_TOXIC_LEXICON: Dict[str, float] = {
    # leve
    "noob": 1.2,
    "int": 1.5,
    "troll": 1.5,
    "trash": 2.0,

    # moderado
    "useless": 2.0,
    "garbage": 2.1,
    "dogshit": 2.2,
    "idiot": 2.4,
    "stupid": 2.2,
    "moron": 2.1,

    # fuerte
    "fuck": 2.5,
    "fucking": 2.8,
    "shit": 2.0,
    "asshole": 3.0,
    "bitch": 2.6,

    # extremo
    "retard": 3.4,
    "kys": 4.0,
    "die": 3.0,
    "uninstall": 2.5,
}

# Intensificadores (multiplican severidad)
INTENSIFIERS = {
    "very", "so", "fucking", "really", "extremely",
    "super", "ultra", "literally", "absolutely"
}

# Amortiguadores (reducen severidad)
DOWNTONERS = {
    "kinda", "sorta", "slightly", "somewhat", "a-bit"
}

# Negación
NEGATIONS = {"no", "not", "never", "dont", "don't", "isnt", "isn't"}


# =====================================================
# 2. UTILIDAD: CARGAR palabras de mecánica LoL
# =====================================================

def load_game_words(path: Path) -> Set[str]:
    with open(path, "r", encoding="utf-8") as f:
        words = json.load(f)
    return set(words)


# =====================================================
# 3. VERSIÓN BÁSICA DE TOXICIDAD
# =====================================================

def basic_toxicity_features(tokens: Iterable[str],
                            toxic_lexicon: Set[str]) -> Dict[str, Any]:

    toks = [t.lower() for t in tokens]
    total = len(toks)

    count = sum(1 for t in toks if t in toxic_lexicon)

    return {
        "tox_word_count": count,
        "tox_ratio": count / total if total > 0 else 0.0,
        "tox_has_toxic": count > 0,
    }


def apply_basic_toxicity_to_dataframe(df: pd.DataFrame,
                                      tokens_col: str,
                                      toxic_lexicon: Set[str]) -> pd.DataFrame:

    out = df.copy()

    feats = df[tokens_col].apply(
        lambda toks: basic_toxicity_features(toks, toxic_lexicon)
        if isinstance(toks, (list, tuple)) else
        {"tox_word_count": 0, "tox_ratio": 0.0, "tox_has_toxic": False}
    )

    out = pd.concat([out, pd.json_normalize(feats)], axis=1)
    return out


# =====================================================
# 4. VERSIÓN AVANZADA DE TOXICIDAD
# =====================================================

def advanced_toxicity_features(tokens: Iterable[str],
                               toxic_lexicon: Mapping[str, float]) -> Dict[str, Any]:

    toks = [t.lower() for t in tokens]
    total = len(toks)

    tox_count = 0
    total_score = 0.0
    max_span = 0.0

    for i, w in enumerate(toks):
        base = toxic_lexicon.get(w)
        if base is None:
            continue

        tox_count += 1
        score = base

        # Ver anterior
        prev = toks[i - 1] if i > 0 else ""

        if prev in INTENSIFIERS:
            score *= 1.5
        if prev in DOWNTONERS:
            score *= 0.6
        if prev in NEGATIONS:
            score *= 0.2

        total_score += score
        max_span = max(max_span, score)

    return {
        "tox_adv_token_count": tox_count,
        "tox_adv_score_raw": total_score,
        "tox_adv_score_norm": total_score / total if total > 0 else 0.0,
        "tox_adv_max_span_score": max_span,
        "tox_adv_has_toxic": tox_count > 0,
    }


def apply_advanced_toxicity_to_dataframe(df: pd.DataFrame,
                                         tokens_col: str,
                                         toxic_lexicon: Mapping[str, float]) -> pd.DataFrame:

    out = df.copy()

    feats = df[tokens_col].apply(
        lambda toks: advanced_toxicity_features(toks, toxic_lexicon)
        if isinstance(toks, (list, tuple)) else
        {
            "tox_adv_token_count": 0,
            "tox_adv_score_raw": 0.0,
            "tox_adv_score_norm": 0.0,
            "tox_adv_max_span_score": 0.0,
            "tox_adv_has_toxic": False,
        }
    )

    out = pd.concat([out, pd.json_normalize(feats)], axis=1)
    return out


# =====================================================
# 5. FUNCIÓN PRINCIPAL PARA LO-L
# =====================================================

def prepare_lol_toxicity_lexicons(game_words: Set[str]):
    """
    Devuelve (basic_lex, advanced_lex) con las palabras de gameplay REMOVIDAS para evitar falsos positivos.
    """
    basic = {w for w in BASIC_TOXIC_WORDS if w not in game_words}

    adv = {w: s for w, s in ADVANCED_TOXIC_LEXICON.items() if w not in game_words}

    return basic, adv
