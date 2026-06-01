"""
export_to_json_noid.py
MySQL  ➜  countries.json / reservations.json  SIN campos *_id
Requisitos:
    pip install mysql-connector-python tqdm
"""

import json, os
import mysql.connector as sql
from tqdm import tqdm

# ─── Conexión ────────────────────────────────────────────────────────────────
DB = {"user":"root","password":"Epsilon22","host":"localhost","database":"HotelAnalytics"}
cnx = sql.connect(**DB)
cur = cnx.cursor(dictionary=True)
os.makedirs("data/json", exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. countries.json  (Country → chains → hotels → rooms)
# ─────────────────────────────────────────────────────────────────────────────
print("→ countries.json …")

cur.execute("""
SELECT
  c.name            AS country,
  c.iso_code,
  c.currency,

  hc.name           AS chain,
  hc.founded_year,
  hc.hq_city,

  h.name            AS hotel,
  h.city            AS hotel_city,
  h.address,
  h.stars,

  r.room_number,
  r.room_type,
  r.capacity,
  r.base_rate
FROM Country c
JOIN HotelChain hc ON hc.country_id = c.country_id
JOIN Hotel      h  ON h.chain_id    = hc.chain_id
JOIN Room       r  ON r.hotel_id    = h.hotel_id
ORDER BY country, chain, hotel, r.room_number
""")

countries, last_country, last_chain, last_hotel = [], None, None, None
for row in cur.fetchall():
    # Country
    if row["country"] != last_country:
        countries.append({
            "name":     row["country"],
            "iso_code": row["iso_code"],
            "currency": row["currency"],
            "chains":   []
        })
        last_chain = last_hotel = None
        last_country = row["country"]
    c_ref = countries[-1]

    # Chain
    if row["chain"] != last_chain:
        c_ref["chains"].append({
            "name":         row["chain"],
            "founded_year": row["founded_year"],
            "hq_city":      row["hq_city"],
            "hotels":       []
        })
        last_hotel = None
        last_chain = row["chain"]
    ch_ref = c_ref["chains"][-1]

    # Hotel
    if row["hotel"] != last_hotel:
        ch_ref["hotels"].append({
            "name":    row["hotel"],
            "city":    row["hotel_city"],
            "address": row["address"],
            "stars":   row["stars"],
            "rooms":   []
        })
        last_hotel = row["hotel"]
    h_ref = ch_ref["hotels"][-1]

    # Room
    h_ref["rooms"].append({
        "room_number": row["room_number"],
        "room_type":   row["room_type"],
        "capacity":    row["capacity"],
        "base_rate":   float(row["base_rate"])
    })

with open("data/json/countries.json", "w", encoding="utf-8") as f:
    json.dump(countries, f, indent=2, ensure_ascii=False)
print("  ✓ countries.json listo")

# ─────────────────────────────────────────────────────────────────────────────
# 2. reservations.json  (Reserva + huésped + servicios)
# ─────────────────────────────────────────────────────────────────────────────
print("→ reservations.json …")

cur.execute("""
SELECT res.reservation_id,          -- solo se usa para agrupar, no se guarda
       res.room_id,
       res.check_in, res.check_out, res.status, res.total_amount,
       g.first_name, g.last_name, g.email, g.country_id,

       r.room_number, r.room_type,
       h.name  AS hotel_name, ch.name AS chain_name, c.name AS country_name
FROM   Reservation res
JOIN   Guest g   ON g.guest_id   = res.guest_id
JOIN   Room  r   ON r.room_id    = res.room_id
JOIN   Hotel h   ON h.hotel_id   = r.hotel_id
JOIN   HotelChain ch ON ch.chain_id = h.chain_id
JOIN   Country c ON c.country_id = ch.country_id
ORDER  BY res.reservation_id
""")

reservations = {}
for row in tqdm(cur.fetchall(), desc="Res/Guest"):
    rid = row["reservation_id"]
    reservations[rid] = {
        # SIN reservation_id ni room_id
        "guest": {
            "first_name": row["first_name"],
            "last_name":  row["last_name"],
            "email":      row["email"],
            "country_id": row["country_id"]   # se puede borrar igual si quieres
        },
        "hotel":   row["hotel_name"],
        "chain":   row["chain_name"],
        "country": row["country_name"],
        "room": {
            "number": row["room_number"],
            "type":   row["room_type"]
        },
        "check_in":     str(row["check_in"]),
        "check_out":    str(row["check_out"]),
        "status":       row["status"],
        "total_amount": float(row["total_amount"]),
        "services":     []
    }

# Servicios
cur.execute("""
SELECT rs.reservation_id, s.name, rs.quantity, rs.price_unit
FROM   ReservationService rs
JOIN   Service s ON s.service_id = rs.service_id
""")
for row in tqdm(cur.fetchall(), desc="Servicios"):
    reservations[row["reservation_id"]]["services"].append({
        "name":       row["name"],
        "quantity":   row["quantity"],
        "price_unit": float(row["price_unit"])
    })

with open("data/json/reservations.json", "w", encoding="utf-8") as f:
    json.dump(list(reservations.values()), f, indent=2, ensure_ascii=False)
print("  ✓ reservations.json listo")

cur.close(); cnx.close()
print("Exportación completada.\n")
