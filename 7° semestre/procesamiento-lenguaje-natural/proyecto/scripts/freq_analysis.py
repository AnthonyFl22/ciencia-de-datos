from collections import Counter
from typing import List, Tuple

def char_frequencies(s: str) -> Counter:
    """Calcula la frecuencia de cada carácter en una cadena de texto.

    Args:
        s (str): La cadena de texto a analizar.

    Returns:
        Counter: Un objeto Counter con cada carácter como clave y su
                 frecuencia como valor.
    """
    return Counter(s)

def word_frequencies(tokens: List[str]) -> Counter:
    """Calcula la frecuencia de cada palabra (token) en una lista.

    Args:
        tokens (List[str]): Una lista de strings donde cada elemento es
                            una palabra o token.

    Returns:
        Counter: Un objeto Counter con cada palabra como clave y su
                 frecuencia como valor.
    """
    return Counter(tokens)

def top_items(counter: Counter, n: int) -> List[Tuple[str, int]]:
    """Obtiene los 'n' elementos más comunes de un objeto Counter.

    Args:
        counter (Counter): El objeto Counter del cual extraer los elementos.
        n (int): El número de elementos más comunes a devolver.

    Returns:
        List[Tuple[str, int]]: Una lista de tuplas (elemento, conteo),
                                ordenada de mayor a menor frecuencia.
    """
    return counter.most_common(n)