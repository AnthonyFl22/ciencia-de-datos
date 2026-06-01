"""
benchmark_sql_vs_neo4j.py
──────────────────────────────────────────────────────────────────────────────
Top-10 ingresos 2024 por País × Cadena × Hotel
• MySQL: 8 JOINs
• Neo4j : camino País→Cadena→Hotel→Reserva (+extras)

Requisitos:
    pip install mysql-connector-python neo4j tabulate
"""

import time, importlib
import mysql.connector as sql
from neo4j import GraphDatabase

TAB = importlib.util.find_spec("tabulate") is not None
if TAB: from tabulate import tabulate

# ─── credenciales ──────────────────────────────────────────────────────────
MYSQL = dict(user="root", password="Epsilon22",
             host="localhost", database="HotelAnalytics")

NEO = dict(uri="neo4j+s://0ba16138.databases.neo4j.io",
           user="neo4j",
           password="6JWD8Ri7C8C2NjGzi4VEfAxLibXwmKbOjbAirGzDXVw")

# ─── MySQL (8 JOINs) ───────────────────────────────────────────────────────
SQL = """
WITH e AS (
  SELECT rs.reservation_id, SUM(s.base_price) AS extras
  FROM   ReservationService rs
  JOIN   Service s ON s.service_id = rs.service_id
  GROUP  BY rs.reservation_id
)
SELECT
  c.name  AS pais,
  hc.name AS cadena,
  h.name  AS hotel,
  ROUND(SUM(r.total_amount + IFNULL(e.extras,0)),2) AS ingresos
FROM   Reservation r
LEFT   JOIN e          ON e.reservation_id = r.reservation_id
JOIN   Room      rm    ON rm.room_id   = r.room_id
JOIN   Hotel     h     ON h.hotel_id   = rm.hotel_id
JOIN   HotelChain hc   ON hc.chain_id  = h.chain_id
JOIN   Country   c     ON c.country_id = hc.country_id
WHERE  r.check_in BETWEEN '2024-01-01' AND '2024-12-31'
GROUP  BY pais,cadena,hotel
ORDER  BY ingresos DESC
LIMIT 10;
"""

# ─── Neo4j (dirección correcta) ────────────────────────────────────────────
CYPHER = """
MATCH (c:Country)<-[:HOSTS_CHAIN]-(hc:HotelChain)-[:OPERATES]->(h:Hotel)
MATCH (h)-[:HAS_BOOKING]->(r:Reservation)
WHERE r.check_in >= date('2024-01-01') AND r.check_in < date('2025-01-01')
OPTIONAL MATCH (r)-[:INCLUDES]->(svc:Service)
WITH c.name  AS pais,
     hc.name AS cadena,
     h.name  AS hotel,
     sum(r.total_amount)               AS base,
     sum(coalesce(svc.price_unit,0))   AS extras
RETURN pais,cadena,hotel, round(base + extras,2) AS ingresos
ORDER BY ingresos DESC
LIMIT 10
"""

def show(rows, hdr): print(tabulate(rows, headers=hdr, tablefmt="github") if TAB else rows)

# ─── ejecutar MySQL ─────────────────────────────────────────────────────────
cnx = sql.connect(**MYSQL); cur = cnx.cursor()
t0  = time.perf_counter()
cur.execute(SQL)
sql_rows = cur.fetchall()
t_sql = time.perf_counter() - t0
cur.close(); cnx.close()

# ─── ejecutar Neo4j ────────────────────────────────────────────────────────
driver = GraphDatabase.driver(NEO["uri"], auth=(NEO["user"], NEO["password"]))
with driver.session() as s:
    t0 = time.perf_counter()
    neo_rows = [(r["pais"], r["cadena"], r["hotel"], r["ingresos"])
                for r in s.run(CYPHER)]
    t_neo = time.perf_counter() - t0
driver.close()

# ─── resultados ────────────────────────────────────────────────────────────
hdr = ["País","Cadena","Hotel","Ingresos"]

print("\n=== MySQL Top-10 ===");  show(sql_rows, hdr)
print("\n=== Neo4j Top-10 ==="); show(neo_rows, hdr)

print("\n=== Latencias ===")
show([("MySQL (8 JOINs)", f"{t_sql:.3f} s"),
      ("Neo4j (5 hops)",  f"{t_neo:.3f} s")],
     ["Motor","Tiempo"])
