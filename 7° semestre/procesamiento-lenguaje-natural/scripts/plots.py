import matplotlib.pyplot as plt
from collections import Counter

def plot_histogram_from_counter(counter: Counter, title: str, max_items: int = None, rotation: int = 0):
    """Crea y devuelve un histograma (gráfico de barras) a partir de un objeto Counter.

    La función visualiza las frecuencias de los elementos contenidos en el Counter,
    mostrando opcionalmente solo los más comunes.

    Args:
        counter (Counter): El objeto Counter con los datos a graficar.
        title (str): El título que se mostrará en el gráfico.
        max_items (int, optional): El número máximo de elementos a mostrar,
                                   ordenados por frecuencia. Si es None, se
                                   muestran todos. Por defecto es None.
        rotation (int, optional): El ángulo de rotación (en grados) para las
                                  etiquetas del eje X. Útil si son largas.
                                  Por defecto es 0.

    Returns:
        matplotlib.figure.Figure: El objeto de la figura de Matplotlib que
                                  contiene el gráfico, para poder guardarlo
                                  o modificarlo después.
    """
    # Obtiene los elementos más comunes, limitados por max_items si se especifica.
    if max_items:
        items = counter.most_common(max_items)
    else:
        items = counter.most_common()

    # Separa las etiquetas (claves) y los valores (frecuencias).
    labels = [k for k, _ in items]
    values = [v for _, v in items]

    # Crea la figura y el gráfico de barras.
    plt.figure(figsize=(10, 4))
    plt.bar(range(len(values)), values)

    # Configura las etiquetas del eje X y el título.
    plt.xticks(range(len(values)), labels, rotation=rotation)
    plt.title(title)

    # Ajusta el diseño para que todo sea visible.
    plt.tight_layout()

    # Devuelve la figura actual para manipulación externa.
    return plt.gcf()