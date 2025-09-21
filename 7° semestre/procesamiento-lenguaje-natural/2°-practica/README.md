#  Práctica II de Procesamiento del Lenguaje Natural

## 🎯 Objetivo
Aplicar conceptos básicos de la **teoría de la información** para evaluar la calidad de la información de un texto, bajo un enfoque de **precisión** y **sentido crítico**.

---

## 📂 Parte 1: Preprocesamiento del texto

### 🔹 Archivos a utilizar
- `text_1.txt`  
- `text_2.txt`  
- `text_3.txt`  
- `text_4.txt`  
- `text_5.txt`  
- `libro_1.txt`  
- `libro_2.txt`  

### 🔹 Tareas
Crear una función que ejecute al menos lo siguiente (se pueden incluir más transformaciones opcionales):

- ✅ Convertir todo el texto a **minúsculas**.  
- ✅ Quitar **acentos** (ejemplo: `á → a`).  
- ✅ Eliminar los siguientes caracteres especiales:
  ; : , . \ - " ' / ( ) [ ] ¿ ? ¡ ! { } ~ < > | « » - — ’ \t \n \r


---

## 📂 Parte 2: Frecuencias a nivel de carácter

1. Calcular la **frecuencia de aparición de cada carácter** en los archivos `text_1.txt` a `text_5.txt`.  
   - No se deben contar los **espacios en blanco**.  

2. Generar un **histograma** para cada archivo:  
   - Ordenar los caracteres de **mayor a menor frecuencia**.  

3. Interpretar cada histograma:  
   - Identificar qué caracteres destacan.  
   - Explicar posibles razones de esta distribución.  

---

## 📂 Parte 3: Frecuencias a nivel de palabra

1. Calcular las **frecuencias de palabras** en los archivos `libro_1.txt` y `libro_2.txt`.  

2. Responder para cada archivo:  
   - ¿Cuántas palabras hay en total?  
   - ¿Cuántas palabras únicas aparecen?  
   - ¿Cuántas palabras ocurren solo una vez (*hapax legomena*)?  

3. Generar **histogramas de palabras** ordenadas de mayor a menor frecuencia.  
   - Si hay demasiadas palabras, mostrar solo las más frecuentes (ejemplo: **las 30 más comunes**).  

---

## 📂 Parte 4: Entropía

1. Calcular la **entropía a nivel de carácter** en cada documento `text_1.txt` a `text_5.txt`.  
   - No considerar el **espacio en blanco**.  

2. Calcular la **entropía a nivel de palabra** en `libro_1.txt` y `libro_2.txt`:  
   - Primero con **todas las palabras**.  
   - Luego **eliminando las stopwords** (palabras como: `el`, `la`, `y`, `de`, etc.).  

---

## 📂 Parte 5: N-gramas

1. Realizar una revisión de **n-gramas** desde `n=2` hasta `n=5`.  
2. Responder:  
   -  ¿Qué patrones interesantes se encuentran en los textos?  

---

## 📦 Entregables

El resultado de la práctica debe ser un **Notebook en Python** que contenga:

- Código de **preprocesamiento**.  
- Cálculos de **frecuencias** y **entropía**.  
- **Histogramas** generados.  
- Respuestas e **interpretaciones** en celdas de texto.  

---

 **Nota:** Vamos modularizar el código en funciones reutilizables y mantener una estructura clara para facilitar la interpretación de los resultados.


