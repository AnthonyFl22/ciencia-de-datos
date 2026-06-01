# ☁ Sección VI – BigQuery

Esta sección documenta la carga y ejecución de consultas sobre el modelo de reservas hoteleras en Google BigQuery, comparando su rendimiento frente a MySQL. BigQuery es un motor analítico en la nube especializado en procesamiento de datos a gran escala.

---

##  Carga de datos

Los datos fueron insertados en una tabla particionada y optimizada del dataset `hotel_bench` bajo el proyecto `alert-arbor-461801-m9`.

| Motor    | Tiempo de carga |
|----------|------------------|
| MySQL    | 6.86 s           |
| MongoDB  | 0.97 s           |
| BigQuery | 4.53 s           |

> ⚠️ BigQuery presentó un buen desempeño de carga, teniendo en cuenta que la inserción se realizó a través de una conexión externa (API) y que los datos quedaron listos para ser consultados en un entorno altamente paralelo.

---

## Consulta comparativa: Overlap de reservas por hotel (2024)

Esta consulta evalúa qué tan **ocupado y solapado** está un hotel durante el año 2024. El objetivo es identificar **cuántas reservas coinciden en el tiempo**, es decir, **pares de reservas que se traslapan** dentro del mismo hotel.

---

###  Descripción detallada de la consulta

1. **Filtrado de reservas del año 2024**  
   Se seleccionan únicamente las reservas cuya fecha de `check_in` esté dentro del año 2024.

2. **Autojoin de la tabla de reservas**  
   Se cruza la tabla consigo misma (autojoin) para comparar cada reserva con las demás. Esto permite revisar si dos reservas en el mismo hotel se **solapan en el tiempo**.

3. **Condiciones para detectar solapamientos**
   - `a.check_in < b.check_out`  
     La primera reserva comienza antes de que termine la segunda.
   - `b.check_in < a.check_out`  
     La segunda reserva comienza antes de que termine la primera.
   - `a.check_in < b.check_in`  
     Esto evita duplicar pares (porque A con B es igual que B con A).

4. **Agrupamiento por hotel**  
   Una vez encontrados todos los pares que cumplen con esas condiciones, se agrupan por nombre de hotel para contar cuántos **pares solapados** hay en cada uno.

5. **Orden descendente de solapamientos**  
   Finalmente, se ordena la lista de hoteles de mayor a menor cantidad de pares de reservas solapadas, mostrando los 15 con mayor concurrencia.

---

###  ¿Qué información aporta esta consulta?

- **Nivel de ocupación simultánea por hotel**
- **Hoteles más concurridos o con mayor sobreposición de estadías**
- Puede ayudar a entender el **uso de recursos**, **riesgos operativos** y necesidades de **optimización de espacio y personal**


---

##  Resultados comparativos

### 🔹 MySQL

| Hotel           | Pares solapados |
|-----------------|------------------|
| Smith Hotel     | 1576             |
| Wilson Resort   | 1133             |
| Smith Inn       | 979              |
| ...             | ...              |

### 🔹 BigQuery

| Hotel           | Pares solapados |
|-----------------|------------------|
| Smith Hotel     | 1576             |
| Wilson Resort   | 1133             |
| Smith Inn       | 979              |
| ...             | ...              |

> ✅ **Los resultados fueron exactamente iguales** en ambos motores, validando la equivalencia lógica de los datos y la precisión del pipeline.

---

## ⏱ Tiempos de ejecución

| Motor    | Tiempo de respuesta |
|----------|---------------------|
| MySQL    | 5.496 s             |
| BigQuery | 2.327 s             |

> ⚡ **BigQuery resolvió la consulta en menos de la mitad del tiempo** que MySQL. Esto se debe a:
> - Su capacidad para ejecutar en paralelo masivo.
> - Arquitectura orientada a columnas, que optimiza filtros y joins por campos específicos.
> - Indexación interna y particionado automático de datos.

---

##  Análisis

- La consulta representa un escenario realista de **detención de colisiones de reservas**, útil para gestión de disponibilidad y detección de sobreventa.
- Aunque ambos motores manejaron bien la lógica, **BigQuery demostró ser más adecuado para operaciones complejas con grandes volúmenes**, donde la arquitectura distribuida marca una diferencia.

---

## 🧾 Conclusiones

- **BigQuery es ideal para consultas analíticas intensivas**, especialmente con datasets grandes, gracias a su paralelismo nativo.
- **MySQL sigue siendo válido** para operaciones OLTP o analíticas simples, pero empieza a ceder terreno en consultas pesadas con joins autocomparativos.
- Se confirma que el modelo de datos funciona de forma consistente y correcta en ambos entornos.

---

📁 Volver al índice: [Hotel Project – SQL vs NoSQL](../README.md)

