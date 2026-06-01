___

## 📌 Conclusiones Generales del Proyecto Comparativo SQL vs NoSQL

Este proyecto tuvo como propósito evaluar, contrastar y comprender el comportamiento de distintas tecnologías de bases de datos aplicadas a un mismo dominio: un sistema hotelero multinivel. Para ello, se analizaron motores relacionales (MySQL) y no relacionales (Neo4j, BigQuery y MongoDB), evaluando tiempos de ejecución, diseño de consultas y compatibilidad con herramientas analíticas como Power BI.

---

### 🏗️ Modelado y arquitectura

| Motor      | Modelo                 | Ideal para…                                |
|------------|------------------------|---------------------------------------------|
| **MySQL**  | Relacional clásico     | Datos tabulares y transacciones consistentes |
| **Neo4j**  | Grafo                  | Relaciones complejas y recorridos semánticos |
| **MongoDB**| Documental (JSON)      | Estructuras flexibles y jerárquicas          |
| **BigQuery**| Columnares distribuidos | Grandes volúmenes y analítica masiva        |

Cada uno demandó una transformación del modelo lógico:

- En **MySQL**, normalizamos las entidades y aseguramos la integridad referencial.
- En **Neo4j**, rediseñamos el modelo como nodos y relaciones, optimizando las consultas por caminos (hops).
- En **MongoDB**, convertimos los datos a estructuras jerárquicas multinivel (`país > cadena > hotel > reservas > servicios`).
- En **BigQuery**, cargamos archivos JSON como tablas anidadas, aprovechando su soporte nativo para estructuras complejas y procesamiento distribuido.

---

### ⏱️ Comparativa de rendimiento y uso

| Consulta                                          | Ganador   | Observaciones clave                                                                 |
|--------------------------------------------------|-----------|--------------------------------------------------------------------------------------|
| Ingresos por país/cadena/hotel                   | **MySQL** | JOINs indexados más eficientes en estructura tabular                                |
| Noches promedio y reservas por hotel             | **Neo4j** | Cálculos de duración y conteo sobre relaciones directas                             |
| Ocupación diaria por país                        | **Neo4j** | `UNWIND` permitió explotar fechas sin JOINs costosos                                |
| Solapamientos de reserva                         | **BigQuery** | Consulta JOIN intensiva ejecutada 2x más rápido que MySQL                           |
| Exploración y carga masiva flexible              | **MongoDB** | Inserción rápida (20,000 registros en segundos), ideal para documentos complejos     |

---

### ⚙️ Desventas y ventajas

#### ❌ Retos encontrados

- **Neo4j**  
  Presenta lentitud en cargas masivas si se usa JSON directamente; es preferible usar CSV y crear índices para mejorar el rendimiento.

- **MongoDB**  
  Las consultas con documentos anidados requieren pipelines con `$unwind`, `$group`, y `$project`, lo que complica el análisis y aumenta la dificultad de depuración.

- **BigQuery**  
  Su dialecto SQL tiene diferencias clave frente a SQL tradicional. Además, el manejo de estructuras anidadas exige limpieza previa para evitar errores en herramientas externas.

- **MySQL**  
  Cuando el número de relaciones crece, el uso excesivo de `JOINs` impacta negativamente el rendimiento. Es necesario optimizar con índices y subconsultas bien diseñadas.

---

#### ✅ Fortalezas destacadas

- **Neo4j**  
  Permite modelar y consultar relaciones complejas de forma clara y eficiente, ideal para navegar estructuras jerárquicas como país → cadena → hotel.

- **MongoDB**  
  Gran flexibilidad para modelar estructuras complejas sin necesidad de esquemas fijos. Ideal para documentos embebidos y consultas ágiles sobre objetos completos.

- **BigQuery**  
  Excelente rendimiento sobre grandes volúmenes de datos. Su arquitectura serverless permite escalar sin necesidad de gestionar infraestructura.

- **MySQL**  
  Fuerte consistencia, integridad referencial y soporte maduro para operaciones transaccionales. Ideal para esquemas bien definidos y aplicaciones con lógica relacional clara.


---

### 📎 Reflexión Final

**No existe un motor "mejor" universalmente.**  
Cada tecnología tiene su lugar dependiendo del objetivo:

- ¿Necesitas integridad referencial y reportes clásicos? → **MySQL**
- ¿Tu dominio tiene relaciones complejas? → **Neo4j**
- ¿Trabajas con datos semiestructurados o flexibles? → **MongoDB**
- ¿Quieres análisis de millones de registros en segundos? → **BigQuery**

Este proyecto permitió ejercitar la adaptabilidad y comprensión profunda de cómo los datos deben modelarse según la herramienta. **Lo importante no es solo almacenar, sino diseñar para consultar eficientemente.**

---

**Desarrollado por:** Luis Anthony Flores Portillo  

**Proyecto Final – Base de Datos No Estructuradas – 2025**

**Profesor:** Pablo Martínez Castro

