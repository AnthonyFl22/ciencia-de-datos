"""
sql_vs_bigquery.py
──────────────────────────────────────────────────────────────────────────────
Compara latencia y resultados entre:

  • MySQL local  (8 JOINs)
  • BigQuery     (LEFT JOIN UNNEST)

Consulta – Ingresos 2024 (tarifa + extras) agrupados por País ▸ Cadena ▸ Hotel,
incluye huéspedes distintos y noches promedio (Top-10).

Requisitos:
    pip install mysql-connector-python google-cloud-bigquery tabulate
Coloca gcp_key.json (service-account) junto al script.
"""

import os, time, importlib
import mysql.connector as sql
from google.cloud import bigquery

# ─── CREDENCIALES ────────────────────────────────────────────────────────────
MYSQL = {
    "user":     "root",
    "password": "Epsilon22",
    "host":     "localhost",
    "database": "HotelAnalytics",
}

PROJECT_ID  = "alert-arbor-461801-m9"        # ← reemplaza por tu ID
DATASET_ID  = "hotel_bench"
SERVICE_KEY = "gcp_key.json"           # cuenta de servicio BigQuery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(SERVICE_KEY)

TABULATE = importlib.util.find_spec("tabulate") is not None
if TABULATE:
    from tabulate import tabulate

# ─── SQL MySQL (8 JOINs) ─────────────────────────────────────────────────────
SQL_MYSQL = """
SELECT
  c.name  AS country,
  hc.name AS chain,
  h.name  AS hotel,
  ROUND(SUM(r.total_amount + IFNULL(rs.quantity*rs.price_unit,0)), 2) AS revenue,
  COUNT(DISTINCT g.email) AS guests,
  ROUND(AVG(DATEDIFF(r.check_out,r.check_in)),2) AS avg_nights
FROM   Reservation r
JOIN   Room          rm ON rm.room_id   = r.room_id
JOIN   Hotel         h  ON h.hotel_id   = rm.hotel_id
JOIN   HotelChain    hc ON hc.chain_id  = h.chain_id
JOIN   Country       c  ON c.country_id = hc.country_id
JOIN   Guest         g  ON g.guest_id   = r.guest_id
LEFT  JOIN ReservationService rs ON rs.reservation_id = r.reservation_id
LEFT  JOIN Service            s  ON s.service_id      = rs.service_id
WHERE  r.check_in BETWEEN '2024-01-01' AND '2024-12-31'
GROUP  BY country, chain, hotel
ORDER  BY revenue DESC
LIMIT  10;
"""

# ─── SQL BigQuery (LEFT JOIN UNNEST) ─────────────────────────────────────────
SQL_BQ = f"""
SELECT
  r.country.name                             AS country,
  r.chain                                    AS chain,
  r.hotel                                    AS hotel,
  ROUND(SUM(r.total_amount
            + IFNULL(svc.quantity*svc.price_unit,0)), 2)     AS revenue,
  COUNT(DISTINCT r.guest.email)                              AS guests,
  ROUND(AVG(DATE_DIFF(r.check_out, r.check_in, DAY)),2)      AS avg_nights
FROM `{PROJECT_ID}.{DATASET_ID}.reservations` AS r
LEFT JOIN UNNEST(r.services) AS svc
WHERE r.check_in BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY country, chain, hotel
ORDER BY revenue DESC
LIMIT 10
"""

def pretty(rows, headers):
    if TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="github"))
    else:
        print(headers); [print(r) for r in rows]

# ─── Ejecutar MySQL ──────────────────────────────────────────────────────────
cnx = sql.connect(**MYSQL)
cur = cnx.cursor()
t0  = time.perf_counter()
cur.execute(SQL_MYSQL)
mysql_rows = cur.fetchall()
t_mysql = time.perf_counter() - t0
cur.close(); cnx.close()

# ─── Ejecutar BigQuery ───────────────────────────────────────────────────────
bq = bigquery.Client(project=PROJECT_ID)
t0 = time.perf_counter()
bq_rows = list(bq.query(SQL_BQ).result())
t_bq = time.perf_counter() - t0
bq_rows_fmt = [(r.country, r.chain, r.hotel, r.revenue, r.guests, r.avg_nights)
               for r in bq_rows]

# ─── Mostrar resultados y tiempos ───────────────────────────────────────────
headers = ["País","Cadena","Hotel","Ingresos","Huésp.","Noches"]

print("\n=== MySQL ===")
pretty(mysql_rows, headers)

print("\n=== BigQuery ===")
pretty(bq_rows_fmt, headers)

print("\n=== Latencias ===")
lat = [("MySQL",    f"{t_mysql:.3f} s"),
       ("BigQuery", f"{t_bq:.3f} s")]
pretty(lat, ["Motor","Tiempo"])
