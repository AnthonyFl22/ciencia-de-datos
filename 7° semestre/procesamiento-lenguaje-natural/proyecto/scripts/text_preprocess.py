import re
import unicodedata
from typing import List

# Constante con los caracteres de puntuación a eliminar.
_TO_REMOVE = r""";:,\.\-\\\"'/\(\)\[\]¿\?¡!\{\}~<>|\«\»\—’\t\n\r"""

def strip_accents(s: str) -> str:
    """Elimina los acentos y otros diacríticos de una cadena de texto.

    Utiliza la normalización NFKD de Unicode para separar los caracteres
    base de sus modificadores (como acentos) y luego los descarta.
    Ejemplo: 'canción' -> 'cancion'.

    Args:
        s (str): La cadena de texto original.

    Returns:
        str: La cadena de texto sin acentos.
    """
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

def preprocess_text(s: str) -> str:
    """Realiza una limpieza completa de una cadena de texto para su análisis.

    El proceso incluye:
    1. Conversión a minúsculas.
    2. Eliminación de acentos.
    3. Reemplazo de signos de puntuación por espacios.
    4. Normalización de espacios múltiples a uno solo.

    Args:
        s (str): La cadena de texto original a preprocesar.

    Returns:
        str: La cadena de texto limpia y normalizada.
    """
    # 1. Convertir a minúsculas
    s = s.lower()
    # 2. Eliminar acentos
    s = strip_accents(s)
    # 3. Eliminar puntuación y otros símbolos definidos en _TO_REMOVE
    s = re.sub(f"[{_TO_REMOVE}]+", " ", s)
    # 4. Normalizar espacios en blanco (múltiples espacios a uno solo)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def tokenize_words(s: str) -> List[str]:
    """Divide una cadena de texto preprocesada en una lista de palabras (tokens).

    Asume que la cadena ya ha sido limpiada y las palabras están
    separadas por un único espacio.

    Args:
        s (str): La cadena de texto limpia.

    Returns:
        List[str]: Una lista de palabras. Devuelve una lista vacía si la
                   cadena de entrada está vacía.
    """
    if not s:
        return []
    return s.split()

def characters_no_spaces(s: str) -> str:
    """Elimina todos los caracteres de espacio en blanco de una cadena.

    Esto incluye espacios, tabulaciones y saltos de línea.

    Args:
        s (str): La cadena de texto de entrada.

    Returns:
        str: La cadena de texto resultante sin ningún espacio en blanco.
    """

    return re.sub(r"\s+", "", s)