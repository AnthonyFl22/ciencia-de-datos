from collections import Counter
from typing import List, Tuple

def ngrams(tokens: List[str], n: int) -> Counter:
    """Genera y cuenta n-gramas a partir de una lista de tokens.

    Un n-grama es una secuencia contigua de 'n' elementos. Por ejemplo,
    los bigramas (n=2) de la frase "el perro corre" son "el perro" y
    "perro corre".

    Args:
        tokens (List[str]): La lista de palabras o tokens a procesar.
        n (int): El tamaño de los n-gramas a generar (ej. 2 para bigramas).
                 Debe ser un entero mayor o igual a 1.

    Returns:
        Counter: Un objeto Counter donde cada clave es un n-grama (string)
                 y el valor es su frecuencia en la lista de tokens.

    Raises:
        ValueError: Si el valor de 'n' es menor a 1.
    """
    if n <= 0:
        raise ValueError("n must be >= 1")
    
    # Crea una tupla de n-gramas.
    # Ej: para n=2 y ['a', 'b', 'c'], genera [('a', 'b'), ('b', 'c')]
    grams = zip(*[tokens[i:] for i in range(n)])
    
    # Une cada tupla en un string y cuenta sus frecuencias.
    return Counter([" ".join(g) for g in grams])