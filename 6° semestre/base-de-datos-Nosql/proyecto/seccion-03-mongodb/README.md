# Sección IV – MongoDB

Esta sección documenta el proceso de carga, consultas y comparativa de rendimiento utilizando MongoDB como gestor de base de datos NoSQL (documental) para el sistema hotelero.

---

## Carga de datos

Se realizó la inserción de **20,000 reservas** estructuradas en JSON multinivel. El tiempo de carga fue el siguiente:

| Motor   | Tiempo de carga |
|---------|------------------|
| MySQL   | 6.86 s           |
| MongoDB | 0.97 s           |

> ⚠️ MongoDB fue casi **7 veces más rápido** en la carga inicial que MySQL gracias a su modelo flexible y la ausencia de relaciones rígidas.

---

##  Consulta Principal: Top-10 ingresos por país → cadena → hotel

Se construyó una consulta idéntica en MySQL (usando 8 JOINs) y en MongoDB (usando un aggregation pipeline), con el objetivo de comparar resultados y tiempos.

###  Consulta en MongoDB (pipeline)

- Filtrado por año 2024
- Cálculo de ingresos por reserva (habitaciones + extras)
- Agrupación multinivel y métricas agregadas

### 📊 Resultados (idénticos a MySQL)

| País          | Cadena              | Hotel           | Ingresos | Huéspedes | Noches |
|---------------|---------------------|-----------------|----------|-----------|--------|
| United States | Barnes Hospitality  | Smith Hotel     | 458,923  | 244       | 5.71   |
| Mexico        | Ramirez Hospitality | Torres Inn      | 427,533  | 221       | 5.56   |
| United States | Fowler Hospitality  | Baker Inn       | 384,773  | 164       | 5.66   |
| Germany       | Martin Hospitality  | Allison Resort  | 348,477  | 166       | 5.16   |
| United States | Carlson Hospitality | Davis Resort    | 342,863  | 150       | 5.66   |
| United States | Foster Hospitality  | Frye Suites     | 338,524  | 142       | 5.53   |
| Spain         | Ray Hospitality     | West Resort     | 335,637  | 152       | 5.67   |
| United States | Fowler Hospitality  | Aguirre Suites  | 334,336  | 138       | 5.64   |
| Germany       | Perez Hospitality   | Williams Suites | 332,378  | 152       | 5.48   |
| Argentina     | Hicks Hospitality   | Wilson Resort   | 331,933  | 140       | 5.67   |

### ⏱ Latencias

| Motor                  | Tiempo de respuesta |
|------------------------|---------------------|
| MySQL (8 JOINs)        | 0.557 s             |
| MongoDB (pipeline)     | 0.348 s             |

>  MongoDB resultó más eficiente para esta consulta jerárquica con operaciones embebidas.

---

## Consultas adicionales

Se realizaron dos consultas más para ampliar la comparación de rendimiento.

### Consulta A – Promedio de ingresos por país × mes (2024)

| Motor   | Tiempo de respuesta |
|---------|---------------------|
| MySQL   | 0.130 s             |
| MongoDB | 0.282 s             |

> ✅ MySQL fue más eficiente en este caso, debido a su estructura tabular optimizada para agregaciones simples.

---

### Consulta B – Top-10 cadenas con estancias >7 noches y compra de servicios

| Motor   | Tiempo de respuesta |
|---------|---------------------|
| MySQL   | 0.073 s             |
| MongoDB | 0.230 s             |

> ✅ MySQL volvió a superar a MongoDB en este tipo de filtros combinados, aprovechando sus relaciones bien indexadas.

---

## 🧾 Conclusiones

- **MongoDB destaca por su rapidez en la carga inicial de datos**, especialmente en estructuras jerárquicas.
- Para consultas que aprovechan la estructura embebida, **MongoDB puede igualar o superar a MySQL**, especialmente si se diseñan pipelines eficientes con índices adecuados.
- **MySQL sigue siendo más rápido en consultas con agregaciones simples**, filtros y relaciones bien definidas.
- **Ambos motores devolvieron resultados consistentes**, lo que valida la equivalencia lógica del modelo en ambos entornos.

---

## ✅ Recomendación

- Usar MongoDB cuando se requiera flexibilidad de esquema, ingestión masiva y navegación jerárquica rápida.
- Considerar MySQL cuando se prioricen consultas rápidas, integridad referencial y un modelo clásico estructurado.

---
📁 Volver al índice: [Hotel Project – SQL vs NoSQL](../README.md)

