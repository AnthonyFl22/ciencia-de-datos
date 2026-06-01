"""
benchmark_query.py  – 8 JOINs vs Pipeline MongoDB (coincidentes)
─────────────────────────────────────────────────────────────────
Top-10 ingresos 2024 (habitación + extras) por País ▸ Cadena ▸ Hotel
           + huéspedes distintos y noches promedio
Requisitos:
    pip install "pymongo[srv]" mysql-connector-python tabulate
"""

import time, importlib
import mysql.connector as sql
from pymongo import MongoClient

# ─── Credenciales ───────────────────────────────────────────────────────────
MYSQL = dict(user="root", password=".",
             host="localhost", database="HotelAnalytics")

MONGO_URI = ("-")
MONGO_DB, RES_COL = "HotelBench", "reservations"
TABULATE = importlib.util.find_spec("tabulate") is not None
# ─────────────────────────────────────────────────────────────────────────────

# ---------- SQL (8 JOINs, ahora LEFT JOIN Service) ---------------------------
SQL_QUERY = """
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
LEFT  JOIN Service s ON s.service_id = rs.service_id
WHERE  r.check_in BETWEEN '2024-01-01' AND '2024-12-31'
GROUP  BY country, chain, hotel
ORDER  BY revenue DESC
LIMIT  10;
"""

# ---------- MongoDB pipeline (idéntico) --------------------------------------
PIPE = [
    {"$match": {"check_in": {"$gte": "2024-01-01", "$lte": "2024-12-31"}}},
    {"$unwind": {"path": "$services", "preserveNullAndEmptyArrays": True}},
    {"$addFields": {
        "row_rev": {
            "$add": [
                "$total_amount",
                { "$ifNull": [
                    { "$multiply": ["$services.quantity", "$services.price_unit"] }, 0
                ]}
            ]
        },
        "nights": {"$dateDiff": {
            "startDate": {"$toDate": "$check_in"},
            "endDate":   {"$toDate": "$check_out"},
            "unit": "day"
        }}
    }},
    {"$group": {
        "_id": {"country":"$country","chain":"$chain","hotel":"$hotel"},
        "revenue": {"$sum": "$row_rev"},
        "guests":  {"$addToSet": "$guest.email"},
        "nights":  {"$avg": "$nights"}
    }},
    {"$project": {
        "_id":0,
        "country":"$_id.country",
        "chain":"$_id.chain",
        "hotel":"$_id.hotel",
        "revenue":{"$round":["$revenue",2]},
        "guests":{"$size":"$guests"},
        "avg_nights":{"$round":["$nights",2]}
    }},
    {"$sort":{"revenue":-1}},
    {"$limit":10}
]

def pretty(rows, headers):
    if TABULATE:
        from tabulate import tabulate
        print(tabulate(rows, headers=headers, tablefmt="github"))
    else:
        print(headers); [print(r) for r in rows]

# ── Ejecutar MySQL ───────────────────────────────────────────────────────────
cx = sql.connect(**MYSQL)
cur= cx.cursor()
t0 = time.perf_counter()
cur.execute(SQL_QUERY)
sql_rows = cur.fetchall()
t_sql = time.perf_counter()-t0
cur.close(); cx.close()

# ── Ejecutar MongoDB (con índice) ────────────────────────────────────────────
cli = MongoClient(MONGO_URI)
col = cli[MONGO_DB][RES_COL]
col.create_index(
    [("check_in",1),("country",1),("chain",1),("hotel",1)],
    name="bench_idx", background=False
)
t0 = time.perf_counter()
mongo_docs = list(col.aggregate(PIPE))
t_mongo = time.perf_counter()-t0
cli.close()

mongo_rows = [(d["country"],d["chain"],d["hotel"],
               d["revenue"],d["guests"],d["avg_nights"]) for d in mongo_docs]

# ── Mostrar resultados ───────────────────────────────────────────────────────
print("\n=== MySQL ===")
pretty(sql_rows, ["País","Cadena","Hotel","Ingresos","Huéspedes","Noches"])

print("\n=== MongoDB ===")
pretty(mongo_rows, ["País","Cadena","Hotel","Ingresos","Huéspedes","Noches"])

print("\n=== Latencias ===")
pretty([("MySQL (8 JOINs)", f"{t_sql:.3f} s"),
        ("MongoDB (pipeline+idx)", f"{t_mongo:.3f} s")],
       ["Motor","Tiempo"])
