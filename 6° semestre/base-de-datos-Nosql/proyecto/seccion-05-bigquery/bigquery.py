"""
benchmark_overlap.py  –  MySQL vs BigQuery
──────────────────────────────────────────────────────────────────────────────
• MISMA lógica en ambos motores, sólo JOINs reales (sin artificios).
• Overlap de reservas 2024 por hotel; Top-15 y latencias.

Requisitos:
    pip install mysql-connector-python google-cloud-bigquery tabulate
    Coloca gcp_key.json en la misma carpeta.
"""

import os, time, importlib
import mysql.connector as sql
from google.cloud import bigquery

# ── CREDENCIALES ────────────────────────────────────────────────────────────
MYSQL = {"user":"root","password":"Epsilon22",
         "host":"localhost","database":"HotelAnalytics"}

PROJECT_ID  = "alert-arbor-461801-m9"   # ← tu proyecto
DATASET_ID  = "hotel_bench"
SERVICE_KEY = "gcp_key.json"            # cuenta de servicio
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(SERVICE_KEY)

TAB = importlib.util.find_spec("tabulate") is not None
if TAB: from tabulate import tabulate

# ── SQL MySQL ───────────────────────────────────────────────────────────────
SQL_MYSQL = """
WITH rez AS (
  SELECT h.name      AS hotel,
         r.check_in,
         r.check_out
  FROM   Reservation r
  JOIN   Room  rm ON rm.room_id = r.room_id
  JOIN   Hotel h  ON h.hotel_id = rm.hotel_id
  WHERE  r.check_in BETWEEN '2024-01-01' AND '2024-12-31'
)
SELECT a.hotel,
       COUNT(*) AS overlaps
FROM rez a
JOIN rez b
  ON a.hotel       = b.hotel
 AND a.check_in    < b.check_in        -- evita duplicados
 AND a.check_in    < b.check_out
 AND b.check_in    < a.check_out
GROUP BY a.hotel
ORDER BY overlaps DESC
LIMIT 15;
"""

# ── SQL BigQuery ────────────────────────────────────────────────────────────
SQL_BQ = f"""
WITH rez AS (
  SELECT hotel AS hotel,
         check_in,
         check_out
  FROM `{PROJECT_ID}.{DATASET_ID}.reservations`
  WHERE check_in BETWEEN '2024-01-01' AND '2024-12-31'
)
SELECT a.hotel,
       COUNT(*) AS overlaps
FROM rez AS a
JOIN rez AS b
ON  a.hotel      = b.hotel
AND a.check_in   < b.check_in         -- evita duplicados
AND a.check_in   < b.check_out
AND b.check_in   < a.check_out
GROUP BY a.hotel
ORDER BY overlaps DESC
LIMIT 15
"""

def show(rows, hdr):
    print(tabulate(rows, headers=hdr, tablefmt="github") if TAB else rows)

# ── Ejecutar MySQL ──────────────────────────────────────────────────────────
print("⏱️  Ejecutando MySQL …")
cnx = sql.connect(**MYSQL)
cur = cnx.cursor(buffered=True)
t0  = time.perf_counter()
cur.execute(SQL_MYSQL)
mysql_rows = list(cur)
t_mysql = time.perf_counter() - t0
cur.close(); cnx.close()

# ── Ejecutar BigQuery ───────────────────────────────────────────────────────
print("⏱️  Ejecutando BigQuery …")
bq = bigquery.Client(project=PROJECT_ID)
t0 = time.perf_counter()
bq_rows = [(r.hotel, r.overlaps) for r in bq.query(SQL_BQ).result()]
t_bq = time.perf_counter() - t0

# ── Mostrar resultados y tiempos ────────────────────────────────────────────
hdr = ["Hotel","Pares solapados"]

print("\n=== MySQL Top-15 ===")
show(mysql_rows, hdr)

print("\n=== BigQuery Top-15 ===")
show(bq_rows, hdr)

print("\n=== Latencias ===")
show([("MySQL",    f"{t_mysql:.3f} s"),
      ("BigQuery", f"{t_bq:.3f} s")],
     ["Motor","Tiempo"])
