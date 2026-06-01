"""
populate_hotels.py  –  versión con cronómetro
Genera datos y los inserta en MySQL · mide el tiempo total de ejecución.
"""

import random, datetime as dt, time, numpy as np
from faker import Faker
import mysql.connector as sql
from tqdm import tqdm

# ─── Config ──────────────────────────────────────────────────────────────────
DB_CFG = {
    "user": "root",
    "password": "Epsilon22",
    "host": "localhost",
    "database": "HotelAnalytics",
    "raise_on_warnings": True,
}

SEED = 42
faker = Faker()
Faker.seed(SEED)
random.seed(SEED)
np.random.seed(SEED)

def executemany(cur, q, data, chunk=1000):
    for i in range(0, len(data), chunk):
        cur.executemany(q, data[i : i + chunk])

# ─── Inicio del cronómetro ───────────────────────────────────────────────────
t0 = time.perf_counter()

cnx = sql.connect(**DB_CFG)
cur = cnx.cursor()

# 1. Country ------------------------------------------------------------------
countries = [
    ("Mexico", "MX", "MXN"), ("United States", "US", "USD"),
    ("Canada", "CA", "CAD"), ("Spain", "ES", "EUR"),
    ("France", "FR", "EUR"), ("Germany", "DE", "EUR"),
    ("Brazil", "BR", "BRL"), ("Argentina", "AR", "ARS"),
    ("Japan", "JP", "JPY"), ("Australia", "AU", "AUD"),
]
executemany(
    cur,
    "INSERT INTO Country (name,iso_code,currency) VALUES (%s,%s,%s)",
    countries,
)
cnx.commit()

cur.execute("SELECT country_id FROM Country ORDER BY country_id")
COUNTRY_IDS = [r[0] for r in cur.fetchall()]

# 2. HotelChain ---------------------------------------------------------------
chain_rows = [
    (
        f"{faker.last_name()} Hospitality",
        random.randint(1975, 2015),
        faker.city(),
        random.choice(COUNTRY_IDS),
    )
    for _ in range(25)
]
executemany(
    cur,
    """INSERT INTO HotelChain (name,founded_year,hq_city,country_id)
       VALUES (%s,%s,%s,%s)""",
    chain_rows,
)

# 3. Hotel --------------------------------------------------------------------
hotel_rows = []
for chain_id in range(1, 26):
    for _ in range(random.randint(5, 8)):
        hotel_rows.append(
            (
                chain_id,
                f"{faker.last_name()} {random.choice(['Resort','Inn','Suites','Hotel'])}",
                faker.city(),
                faker.street_address(),
                random.randint(3, 5),
            )
        )
executemany(
    cur,
    """INSERT INTO Hotel (chain_id,name,city,address,stars)
       VALUES (%s,%s,%s,%s,%s)""",
    hotel_rows,
)

# 4. Room ---------------------------------------------------------------------
ROOM_TYPES = [("single", 1, 80), ("double", 2, 120),
              ("suite", 3, 220), ("deluxe", 4, 350)]
room_rows = []
for hotel_id in range(1, len(hotel_rows) + 1):
    for i in range(random.randint(25, 40)):
        t, cap, rate = random.choice(ROOM_TYPES)
        room_rows.append((hotel_id, f"{(i // 10) + 1}{i % 10:02}", t, cap, rate))
executemany(
    cur,
    """INSERT INTO Room (hotel_id,room_number,room_type,capacity,base_rate)
       VALUES (%s,%s,%s,%s,%s)""",
    room_rows,
)

# 5. Guest --------------------------------------------------------------------
start_dt, end_dt = dt.datetime(2023, 1, 1), dt.datetime(2023, 12, 31, 23, 59, 59)
guest_rows = [
    (
        faker.first_name(),
        faker.last_name(),
        faker.unique.email(),
        random.choice(COUNTRY_IDS),
        faker.date_time_between_dates(start_dt, end_dt),
    )
    for _ in range(8_000)
]
executemany(
    cur,
    """INSERT INTO Guest
       (first_name,last_name,email,country_id,created_at)
       VALUES (%s,%s,%s,%s,%s)""",
    guest_rows,
)

# 6. Service ------------------------------------------------------------------
services = [
    ("Desayuno buffet", "alimentos", 15), ("Cena gourmet", "alimentos", 35),
    ("Spa básico", "spa", 45), ("Masaje deluxe", "spa", 90),
    ("Traslado aeropuerto", "transporte", 25), ("Tour ciudad", "transporte", 40),
    ("Lavandería", "otros", 10), ("Room-service", "alimentos", 20),
    ("Baby-sitting", "otros", 30), ("Parking", "otros", 8),
    ("Mini-bar", "alimentos", 12), ("Internet premium", "otros", 5),
]
executemany(
    cur,
    "INSERT INTO Service (name,category,base_price) VALUES (%s,%s,%s)",
    services,
)
cnx.commit()  # catálogos listos

# 7. Reservation & ReservationService -----------------------------------------
room_ids = list(range(1, len(room_rows) + 1))
guest_ids = list(range(1, 8_001))
service_ids = list(range(1, len(services) + 1))

def seasonal_date():
    weights = [0.8, 0.9, 1.0, 1.5, 1.3, 1.2, 1.6, 1.4, 1.0, 0.9, 0.8, 1.7]
    m = np.random.choice(range(12), p=np.array(weights) / sum(weights))
    return dt.date(2024, m + 1, random.randint(1, 28))

print("Insertando Reservas…")
res_rows = []
svc_rows = []  # (idx_res, service_id, qty, price_unit)

for idx in tqdm(range(20_000)):
    guest_id = random.choice(guest_ids)
    room_id = random.choice(room_ids)
    ci = seasonal_date()
    stay = random.randint(1, 10)
    co = ci + dt.timedelta(days=stay)
    rate = room_rows[room_id - 1][4]
    total = rate * stay
    status = random.choices(
        ["booked", "checked_in", "checked_out", "cancelled"],
        weights=[10, 20, 58, 12],
    )[0]
    res_rows.append((guest_id, room_id, ci, co, status, total))

    for serv in random.sample(service_ids, random.randint(0, 3)):
        svc_rows.append(
            (idx, serv, random.randint(1, 3), services[serv - 1][2])
        )

executemany(
    cur,
    """INSERT INTO Reservation
       (guest_id,room_id,check_in,check_out,status,total_amount)
       VALUES (%s,%s,%s,%s,%s,%s)""",
    res_rows,
)

cur.execute("SELECT reservation_id FROM Reservation ORDER BY reservation_id")
res_ids = [r[0] for r in cur.fetchall()]

for i, (idx, serv, qty, price) in enumerate(svc_rows):
    svc_rows[i] = (res_ids[idx], serv, qty, price)

executemany(
    cur,
    """INSERT INTO ReservationService
       (reservation_id,service_id,quantity,price_unit)
       VALUES (%s,%s,%s,%s)""",
    svc_rows,
)

cnx.commit()
cur.close()
cnx.close()

# ─── Fin del cronómetro ──────────────────────────────────────────────────────
elapsed = time.perf_counter() - t0
print(f"✓ Población completada en {elapsed:.2f} segundos.")
