from pathlib import Path

def read_text(path: str) -> str:
    """Lee el contenido completo de un archivo de texto.

    Utiliza codificación UTF-8 e ignora cualquier error de decodificación
    que pueda ocurrir para evitar que el programa se detenga.

    Args:
        path (str): La ruta al archivo que se va a leer.

    Returns:
        str: El contenido del archivo como una única cadena de texto.
    """
    p = Path(path)
    # Abre el archivo en modo lectura ("r") con codificación utf-8.
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def write_text(path: str, content: str) -> None:
    """Escribe una cadena de texto en un archivo.

    Si los directorios en la ruta de destino no existen, los crea
    automáticamente. El archivo se guarda con codificación UTF-8.

    Args:
        path (str): La ruta del archivo donde se guardará el contenido.
        content (str): El contenido de texto que se va a escribir.
    """
    p = Path(path)
    # Crea los directorios padre si no existen.
    p.parent.mkdir(parents=True, exist_ok=True)
    # Abre el archivo en modo escritura ("w") con codificación utf-8.
    with p.open("w", encoding="utf-8") as f:
        f.write(content)