El proyecto está modularizado en varios archivos `.py` para favorecer la reutilización:

# 📖 Proyecto de Procesamiento de Lenguaje Natural

El proyecto está modularizado en varios archivos `.py` para favorecer la **reutilización** y la **claridad del código**.  
Cada módulo se centra en una responsabilidad específica.

---

## 📂 scripts/

### **io_utils.py**
Funciones para manejo básico de archivos de texto:

- `read_text(path: str) -> str`  
  Lee el contenido completo de un archivo de texto (UTF-8). Ignora errores de decodificación.

- `write_text(path: str, content: str) -> None`  
  Escribe texto en un archivo (UTF-8). Si la ruta no existe, crea los directorios necesarios.

---

### **text_preprocess.py**
Funciones de limpieza y normalización de texto:

- `strip_accents(s: str) -> str`  
  Elimina acentos y diacríticos de una cadena (ej: `"canción" → "cancion"`).

- `preprocess_text(s: str) -> str`  
  Pipeline completo: minúsculas, quitar acentos, eliminar puntuación y normalizar espacios.

- `tokenize_words(s: str) -> List[str]`  
  Divide una cadena limpia en una lista de palabras.

- `characters_no_spaces(s: str) -> str`  
  Elimina **todos** los espacios y saltos de línea de un texto.

---

### **freq_analysis.py**
Funciones para conteo de frecuencias:

- `char_frequencies(s: str) -> Counter`  
  Cuenta las frecuencias de caracteres.

- `word_frequencies(tokens: List[str]) -> Counter`  
  Cuenta las frecuencias de palabras.

- `top_items(counter: Counter, n: int) -> List[Tuple[str, int]]`  
  Devuelve los *n* elementos más comunes de un `Counter`.

---

### **entropy_utils.py**
Funciones para medir aleatoriedad:

- `shannon_entropy(items: Iterable) -> float`  
  Calcula la entropía de Shannon en bits sobre una secuencia de elementos.  
  Indica el nivel de incertidumbre: 0.0 es predictibilidad total, valores altos indican mayor aleatoriedad.

---

### **ngrams.py**
Generación de secuencias de tokens:

- `ngrams(tokens: List[str], n: int) -> Counter`  
  Genera y cuenta *n*-gramas contiguos en una lista de tokens.  
  Ejemplo: con `n=2` y tokens `["el", "perro", "corre"]` genera `"el perro"`, `"perro corre"`.

---

### **plots.py**
Visualización de frecuencias:

- `plot_histogram_from_counter(counter: Counter, title: str, max_items: int = None, rotation: int = 0)`  
  Genera un histograma de barras a partir de un `Counter`. Permite limitar el número de ítems y rotar etiquetas.

---

### **io_titles.py**
Funciones específicas para datasets de noticias:

- `read_titles_csv(path: str | Path, title_col: str = "title") -> list[str]`  
  Lee un archivo CSV y devuelve la columna de títulos como lista de strings.  
  Valida que la columna exista.

- `join_titles(titles: list[str]) -> str`  
  Une una lista de títulos en un solo string separado por espacios.

---

### **pmi.py**
Cálculo de asociaciones de palabras usando **PMI** (*Pointwise Mutual Information*):

- `unigram_counts(tokens: list[str]) -> Counter[str]`  
  Cuenta frecuencias de unigramas.

- `bigram_counter_from_str_keys(counter_str: Counter[str]) -> Counter[tuple[str,str]]`  
  Convierte bigramas en string (`"w1 w2"`) a tuplas (`("w1","w2")`).

- `probabilities(tokens: list[str], bigram_c: Counter[tuple[str,str]])`  
  Calcula probabilidades unigramales y bigramales.

- `pmi_df(tokens: list[str], bigram_c: Counter[tuple[str,str]], min_freq: int = 1) -> pd.DataFrame`  
  Devuelve un DataFrame con pares de palabras, frecuencia y valor PMI.

---

### **report.py**
Funciones auxiliares para reportar resultados:

- `top_pmi(df: pd.DataFrame, k: int = 10) -> pd.DataFrame`  
  Selecciona las *k* asociaciones con mayor PMI.

- `save_table(df: pd.DataFrame, path: str) -> None`  
  Guarda un DataFrame en CSV.

