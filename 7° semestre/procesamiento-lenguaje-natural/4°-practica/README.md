#  Práctica — Detección de Plagio con Medidas de Similitud

##  Descripción general

En esta práctica se desarrolla un ejercicio de **detección básica de plagio** entre un conjunto de documentos de noticias en inglés.  
El objetivo es **identificar qué documentos sospechosos se parecen más a los documentos fuente** utilizando **medidas de similitud léxica**.

Los datos consisten en dos directorios:

-  `source-document/` → documentos **fuente** (textos originales).  
-  `suspicious-document/` → documentos **sospechosos** (algunos contienen fragmentos plagiados y otros no).  

El conjunto de datos contiene tanto plagios reales como casos simulados, por lo que el análisis busca detectar patrones de similitud sin conocer de antemano cuáles son verdaderos.

---

##  Objetivo de la práctica

Detectar, a nivel básico, posibles casos de plagio mediante **medidas de similitud** entre documentos del conjunto `suspicious-document` y documentos del conjunto `source-document`.

---

##  Flujo general del proyecto

1. **Lectura de los documentos** desde ambas carpetas.  
2. **Preprocesamiento de texto**, aplicando:
   - Conversión a **minúsculas**.  
   - Eliminación de **stopwords** (palabras sin contenido semántico).  
   - Aplicación de **stemming** usando el *Porter Stemmer* de NLTK para reducir las palabras a su raíz.  

     ```python
     from nltk.stem.porter import PorterStemmer
     stemmer = PorterStemmer()
     word = stemmer.stem('pages')  # → 'page'
     ```
3. **Cálculo de medidas de similitud léxica**:
   - **Jaccard**  
     \[
     J(A,B) = \frac{|A ∩ B|}{|A ∪ B|}
     \]
   - **Dice**  
     \[
     D(A,B) = \frac{2|A ∩ B|}{|A| + |B|}
     \]
4. **Comparación cruzada**:  
   Para cada documento sospechoso se calcula la similitud con **todos los documentos fuente**, y se seleccionan los **10 más similares**.
5. **Generación de resultados**:  
   Se obtiene una tabla con los nombres de los documentos y sus valores de similitud, ordenados de mayor a menor.

---

##  Ejemplo de salida

| suspicious_document | source_document | jaccard_similarity | dice_similarity |
|----------------------|----------------|--------------------|----------------|
| suspicious-document0001.txt | source-document0015.txt | 0.321 | 0.486 |
| suspicious-document0001.txt | source-document0008.txt | 0.295 | 0.462 |
| … | … | … | … |

---

##  Estructura del notebook

| Bloque | Descripción |
|--------|--------------|
| **Bloque 1** | Configuración del entorno y carga de librerías |
| **Bloque 2** | Limpieza y preprocesamiento (minúsculas, stopwords, stemming) |
| **Bloque 3** | Lectura de documentos `source` y `suspicious` |
| **Bloque 4** | Implementación de las medidas de similitud Jaccard y Dice |
| **Bloque 5** | Cálculo de los 10 documentos fuente más similares por cada sospechoso y visualización en tabla |

---

##  Datos

- Formato: archivos de texto plano codificados en UTF-8.  
- Idioma: inglés.  
- Ubicación dentro del proyecto:
