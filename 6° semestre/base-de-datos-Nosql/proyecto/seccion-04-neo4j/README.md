# 📊 Benchmarks Comparativos: Neo4j vs MySQL

Este capítulo documenta una serie de comparaciones entre **Neo4j** (modelo de grafos) y **MySQL** (modelo relacional tradicional), aplicadas sobre un sistema hotelero multinivel con relaciones entre países, cadenas, hoteles, habitaciones, reservas y servicios. Se evaluaron tres consultas clave, enfocándose en **desempeño** y **facilidad de expresión**.

---

## 🔎 Consulta 1: Ingresos por País × Cadena × Hotel

**Objetivo:** Obtener los 10 hoteles con mayor ingreso total en 2024, sumando tanto el monto de las reservas como los servicios extra contratados por los huéspedes.

- **MySQL** requirió 8 `JOINs` para acceder a la información entre tablas.
- **Neo4j** lo resolvió mediante un camino relacional: `(Country) → (Chain) → (Hotel) → (Reservation) [opcionalmente → (Service)]`.

| Motor   | Técnica utilizada        | Tiempo total |
|---------|--------------------------|--------------|
| MySQL   | JOINs entre 8 tablas     | **0.155 s**  |
| Neo4j   | 5 relaciones (hops)      | **1.061 s**  |

### Resultados:

| País          | Cadena              | Hotel           | Ingresos |
|---------------|---------------------|-----------------|----------|
| United States | Barnes Hospitality  | Smith Hotel     | 255236   |
| Mexico        | Ramirez Hospitality | Torres Inn      | 251408   |
| Germany       | Perez Hospitality   | Williams Suites | 187805   |

🔍 **Comentario:**  
Aunque Neo4j es más expresivo (por ejemplo, no requiere subconsultas ni joins), en este escenario MySQL fue **más rápido** debido a su optimización en operaciones de agregación con índices bien definidos. Neo4j, al usar múltiples "saltos" entre nodos, puede presentar mayor latencia en consultas agregadas extensas.

---

## 🛏️ Consulta 2: Hoteles con estancias más largas

**Objetivo:** Identificar los hoteles donde los huéspedes se quedaron más noches en promedio, considerando solo hoteles con al menos 50 reservas en 2024.

- **MySQL** calculó la duración con `DATEDIFF(check_out, check_in)`.
- **Neo4j** utilizó `duration.inDays(...)` y `UNWIND` para contar las noches por relación.

| Motor   | Tiempo total |
|---------|--------------|
| MySQL   | **2.117 s**  |
| Neo4j   | **0.955 s**  ✅ (más rápido)

### Resultados:

| País          | Hotel            | Noches | Reservas |
|---------------|------------------|--------|----------|
| United States | Bennett Hotel    | 6.10   | 141      |
| Brazil        | Coleman Suites   | 6.00   | 137      |
| France        | Alvarado Hotel   | 5.98   | 100      |

🔍 **Comentario:**  
En este caso, **Neo4j fue más eficiente**, probablemente debido a que ya tiene las fechas como propiedades directas en sus nodos y no requiere reescritura ni joins adicionales. La consulta fue más directa al recorrer la estructura ya conectada.

---

## 📅 Consulta 3: Días con mayor ocupación de habitaciones

**Objetivo:** Determinar los días con mayor número de habitaciones ocupadas a nivel país durante el año 2024.

- **MySQL** utilizó una CTE recursiva para generar un calendario día a día y hacer un `JOIN` con las reservas.
- **Neo4j** aprovechó `UNWIND` y `duration` para calcular dinámicamente cada día entre `check_in` y `check_out`.

| Motor   | Tiempo total |
|---------|--------------|
| MySQL   | **3.255 s**  |
| Neo4j   | **1.423 s**  ✅ (más rápido)

### Resultados:

| País          | Fecha      | Habitaciones |
|---------------|------------|--------------|
| United States | 2024-12-16 | 151          |
| United States | 2024-12-17 | 148          |
| United States | 2024-07-21 | 148          |

🔍 **Comentario:**  
**Neo4j superó a MySQL** gracias a que puede descomponer directamente intervalos de fechas en nodos o propiedades sin requerir estructuras auxiliares como calendarios. Esto reduce los pasos intermedios y mejora el tiempo de ejecución en consultas de tipo temporal.

---

## 🧠 Reflexiones Finales

- **MySQL** brilla en consultas altamente agregadas y cuando los índices están bien definidos. Es ideal para datos estructurados con patrones relacionales simples.
- **Neo4j** sobresale cuando las relaciones entre entidades son complejas, profundas o jerárquicas. También es ventajoso en escenarios con análisis de trayectorias, patrones o datos temporales extensos.

### 🔁 Elección del motor según el caso:

| Caso de uso                          | Recomendación |
|--------------------------------------|---------------|
| Agregaciones simples o directas      | MySQL         |
| Caminos entre entidades (grafos)     | Neo4j         |
| Análisis temporal o de trayectorias  | Neo4j         |
| Consultas con múltiples joins        | Depende del volumen y diseño |

---

## Conclusiones

Neo4j es especialmente útil cuando queremos formular preguntas basadas en relaciones y estructura de nodos. Aunque MySQL puede ser más rápido en operaciones puramente tabulares, Neo4j ofrece consultas más expresivas y fáciles de mantener cuando los datos están interconectados.
