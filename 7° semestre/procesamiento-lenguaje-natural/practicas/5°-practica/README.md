# Práctica — Búsqueda por Similaridad de Texto con Modelos de Lenguaje

## Descripción general

En esta práctica se implementa un sistema de **búsqueda semántica** de títulos de noticias utilizando **modelos de lenguaje preentrenados**.  
El objetivo es representar cada título como un **vector numérico (embedding)** y luego realizar consultas que encuentren los títulos más similares dentro del conjunto de datos.

El dataset contiene títulos de noticias en español provenientes de *El Financiero*.  
Se utilizan los modelos **BETO** y **Robertuito**, ambos diseñados para procesamiento del lenguaje natural en español.

---

##  Objetivo de la práctica

Desarrollar un proceso que permita, dado un conjunto de títulos, **encontrar los textos más parecidos semánticamente** usando embeddings generados por modelos de lenguaje.

---

##  Flujo general del proyecto

1. **Lectura del conjunto de datos**  
   - Archivo: `archivo_emojis_Elfinanciero.csv`  
   - Columna utilizada: `title`  
   - Solo se consideran los primeros **1000 registros**.

2. **Generación de embeddings**  
   - Se usan los modelos:
     - **BETO:** `dccuchile/bert-base-spanish-wwm-cased`  
     - **Robertuito:** `pysentimiento/robertuito-base-uncased`
   - Cada título se convierte en un vector numérico mediante la función `predict()` 

3. **Base de datos vectorial**  
   - Se forma una matriz `S` con todos los embeddings de los títulos.

4. **Consultas**  
   Se realizan búsquedas de los 5 títulos más cercanos para las siguientes oraciones:
   ```python
   [
       "Muerte de migrantes en un incendio en Ciudad Juárez",
       "¿Qué tan sano es comer tacos de cabeza?",
       "La crisis humanitaria de Estados Unidos",
       "Lo que hay del otro laredo",
       "¿Existe un acuerdo entre la banca tradicional y los nuevos jugadores?",
       "Maribel Guardia afirma: Ya no le tengo miedo",
       "Graban pelea en Xochimilco (Video)"
   ]
