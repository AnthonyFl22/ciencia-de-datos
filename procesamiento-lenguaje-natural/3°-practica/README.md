# 📘 Práctica 3 – Análisis de asociaciones con PMI

## 🎯 Objetivo
El propósito de esta práctica fue analizar asociaciones significativas de palabras en títulos de noticias utilizando la medida de **Información Mutua Puntual (PMI, *Pointwise Mutual Information*)**.  

Con ello buscamos identificar pares de palabras que ocurren juntas más frecuentemente de lo esperado por azar, lo cual permite detectar relaciones semánticas en el lenguaje.

---

## 🛠️ Pasos realizados

### 1. Preprocesamiento de texto
- Conversión a **minúsculas**.  
- Eliminación de **acentos**.  
- Eliminación de caracteres especiales y puntuación definidos:  

";:,.\-"'/()[]¿?¡!{}~<>|«»-—’\t\n\r"


- Normalización de espacios en blanco.  
- Tokenización en palabras.

> Para esta etapa se utilizó la función `preprocess_text` desarrollada previamente en prácticas anteriores.

---

### 2. Conjuntos de datos analizados
Se utilizaron tres archivos CSV con títulos de noticias, trabajando de manera independiente en cada uno:

- `archivo_emojis_Proceso.csv`
- `archivo_emojis_Elpais.csv`
- `archivo_emojis_Elfinanciero.csv`

De cada archivo se leyó la columna **`title`**, que fue preprocesada y unida en un solo texto.

---

### 3. Cálculo de asociaciones con PMI
1. A partir del texto preprocesado se generaron **bigramas** (pares de palabras consecutivas).  
2. Se calcularon las probabilidades:
 - Unigramas: `p(x)`  
 - Bigramas: `p(x, y)`  
3. Se aplicó la fórmula de PMI:  

 \[
 PMI(x,y) = \log_2 \frac{p(x,y)}{p(x)\,p(y)}
 \]

4. Se filtraron asociaciones que aparecen **al menos 10 veces** en el texto.  
5. Se seleccionaron las **10 asociaciones más significativas** con mayor valor de PMI.

---

### 4. Resultados esperados
Para cada dataset (`Proceso`, `El País`, `El Financiero`) se obtuvo una tabla con las siguientes columnas:

- **w1** → Primera palabra del bigrama.  
- **w2** → Segunda palabra del bigrama.  
- **freq** → Frecuencia absoluta de aparición del bigrama.  
- **pmi** → Valor de información mutua puntual.  

La tabla presenta los **10 bigramas con mayor PMI**, es decir, las asociaciones de palabras más relevantes.

---

## 📒 Notebook
Todo el procedimiento se implementó en un **notebook de Jupyter** que:
- Lee los datasets.  
- Preprocesa los textos.  
- Genera tokens y bigramas.  
- Calcula probabilidades y PMI.  
- Muestra las 10 asociaciones más significativas por dataset.  

---

## ✅ Conclusión
La práctica permitió:
- Aplicar técnicas de preprocesamiento de texto.  
- Construir modelos simples de lenguaje basados en n-gramas.  
- Identificar asociaciones relevantes en lenguaje natural mediante **PMI**.  

Esto constituye un paso hacia el análisis semántico y la detección de relaciones entre palabras en grandes volúmenes de texto.
