"""
benchmark_extra_queries.py
──────────────────────────────────────────────────────────────────────────────
Ejecuta dos consultas analíticas en MySQL (JOINs) y en MongoDB (pipeline),
mide latencias y muestra los tiempos.

Consulta A – Promedio de ingresos por país × mes (2024)
Consulta B – Top-10 cadenas con estancias >7 noches que compraron extras
"""

import time, mysql.connector as sql
from pymongo import MongoClient, ASCENDING

# ─── ACCESOS ────────────────────────────────────────────────────────────────
MYSQL = dict(user="root", password="-",
             host="localhost", database="HotelAnalytics")

MONGO_URI = ("-")
MONGO_DB, RES_COL = "HotelBench", "reservations"
# ────────────────────────────────────────────────────────────────────────────

# ╔══════════════════════════════════════════════════════════════════════════╗
# █  Consulta A  –  Promedio de ingresos por país × mes (2024)              █
# ╚══════════════════════════════════════════════════════════════════════════╝
SQL_A = """
SELECT
  c.name                         AS country,
  MONTH(r.check_in)              AS month,
  ROUND(AVG(r.total_amount + IFNULL(s.svc_rev,0)),2) AS avg_revenue
FROM Reservation r
JOIN Room          rm ON rm.room_id   = r.room_id
JOIN Hotel         h  ON h.hotel_id   = rm.hotel_id
JOIN HotelChain    hc ON hc.chain_id  = h.chain_id
JOIN Country       c  ON c.country_id = hc.country_id
LEFT JOIN (
    SELECT reservation_id, SUM(quantity*price_unit) AS svc_rev
    FROM   ReservationService
    GROUP  BY reservation_id
) s ON s.reservation_id = r.reservation_id
WHERE r.check_in BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY country, month;
"""

PIPE_A = [
    {"$match": {"check_in": {"$gte": "2024-01-01", "$lte": "2024-12-31"}}},
    {"$unwind": {"path": "$services", "preserveNullAndEmptyArrays": True}},
    {"$addFields": {
        "row_rev": {
            "$add": [
                "$total_amount",
                {"$ifNull": [
                    {"$multiply": ["$services.quantity", "$services.price_unit"]},
                    0
                ]}
            ]
        },
        "month": {"$toInt": {"$substrBytes": ["$check_in",5,2]}}
    }},
    {"$group": {
        "_id": {"country":"$country","month":"$month"},
        "avg_revenue":{"$avg":"$row_rev"}
    }}
]

# ╔══════════════════════════════════════════════════════════════════════════╗
# █  Consulta B  –  Top-10 cadenas: estancias >7 noches con extras          █
# ╚══════════════════════════════════════════════════════════════════════════╝
SQL_B = """
SELECT
  hc.name AS chain,
  COUNT(*) AS long_stays
FROM Reservation r
JOIN Room       rm ON rm.room_id   = r.room_id
JOIN Hotel      h  ON h.hotel_id   = rm.hotel_id
JOIN HotelChain hc ON hc.chain_id  = h.chain_id
LEFT JOIN ReservationService rs ON rs.reservation_id = r.reservation_id
WHERE r.check_in BETWEEN '2024-01-01' AND '2024-12-31'
  AND DATEDIFF(r.check_out,r.check_in) > 7
  AND rs.service_id IS NOT NULL
GROUP BY chain
ORDER BY long_stays DESC
LIMIT 10;
"""

PIPE_B = [
    {"$match": {"check_in": {"$gte": "2024-01-01", "$lte": "2024-12-31"}}},
    {"$unwind": "$services"},
    {"$addFields": {
        "nights": {"$dateDiff": {
            "startDate": {"$toDate": "$check_in"},
            "endDate":   {"$toDate": "$check_out"},
            "unit": "day"
        }}
    }},
    {"$match": {"nights": {"$gt": 7}}},
    {"$group": {
        "_id": "$chain",
        "long_stays": {"$sum": 1}
    }},
    {"$sort": {"long_stays": -1}},
    {"$limit": 10}
]

# ─── Funciones de medición ──────────────────────────────────────────────────
def run_mysql(query):
    cnx = sql.connect(**MYSQL)
    cur = cnx.cursor()
    t0  = time.perf_counter()
    cur.execute(query)
    _   = cur.fetchall()
    t   = time.perf_counter() - t0
    cur.close(); cnx.close()
    return t

def run_mongo(pipe):
    cli = MongoClient(MONGO_URI)
    col = cli[MONGO_DB][RES_COL]
    # aseguramos índice para filtros por fecha y jerarquía
    col.create_index(
        [("check_in",1),("country",1),("chain",1),("hotel",1)],
        name="bench_idx", background=False
    )
    t0  = time.perf_counter()
    _   = list(col.aggregate(pipe))
    t   = time.perf_counter() - t0
    cli.close()
    return t

# ─── Ejecutar y mostrar tiempos ─────────────────────────────────────────────
print("⏱️  Ejecutando Consulta A …")
t_sql_A   = run_mysql(SQL_A)
t_mongo_A = run_mongo(PIPE_A)

print("⏱️  Ejecutando Consulta B …")
t_sql_B   = run_mysql(SQL_B)
t_mongo_B = run_mongo(PIPE_B)

print("\n=== Latencias ===")
print(f"Consulta A  →  MySQL : {t_sql_A:.3f} s   |   MongoDB : {t_mongo_A:.3f} s")
print(f"Consulta B  →  MySQL : {t_sql_B:.3f} s   |   MongoDB : {t_mongo_B:.3f} s")
