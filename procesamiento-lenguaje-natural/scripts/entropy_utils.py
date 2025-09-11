import math
from collections import Counter
from typing import Iterable

def shannon_entropy(items: Iterable) -> float:
    """Calcula la entropía de Shannon para una secuencia de elementos.

    La entropía mide el nivel de incertidumbre o aleatoriedad en los datos.
    Un valor de 0.0 indica predictibilidad total, mientras que valores
    más altos indican una mayor aleatoriedad.

    Args:
        items (Iterable): Una secuencia de elementos, como un string donde cada
                          elemento es un carácter, o una lista de palabras (tokens).

    Returns:
        float: El valor de la entropía calculado en bits.
    """
    # Contar la frecuencia de cada elemento único en la secuencia.
    counter = Counter(items)
    
    # Obtener el número total de elementos.
    total = sum(counter.values())
    
    # Si no hay elementos, la entropía es 0.
    if total == 0:
        return 0.0
    
    ent = 0.0
    # Aplicar la fórmula de Shannon: H(X) = -Σ [p(x) * log2(p(x))]
    for count in counter.values():
        # Calcular la probabilidad (p) de cada elemento.
        p = count / total
        # Sumar el resultado a la entropía total.
        ent -= p * math.log2(p)
        
    return ent