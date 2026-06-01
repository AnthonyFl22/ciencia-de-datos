"""
mongo_load_timed.py
Carga countries.json y reservations.json en MongoDB Atlas con un único insert_many.
Mide tiempos por colección y total.

Requisitos:
    pip install "pymongo[srv]" tqdm
"""

import json, os, time
from pymongo import MongoClient, WriteConcern

# ─── URI Atlas ───────────────────────────────────────────────────────────────
MONGO_URI = ("-")
DB_NAME  = "HotelBench"
CAT_COL  = "catalog"
RES_COL  = "reservations"
JSON_DIR = "data/json"
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def insert_collection(coll, docs):
    t0 = time.perf_counter()
    coll.insert_many(docs, ordered=False)     
    return time.perf_counter() - t0

def main():
    client = MongoClient(MONGO_URI, w=0, journal=False)  
    db     = client[DB_NAME]

    print("Leyendo JSON …")
    countries    = load_json(os.path.join(JSON_DIR, "countries.json"))
    reservations = load_json(os.path.join(JSON_DIR, "reservations.json"))

    db.drop_collection(CAT_COL)
    db.drop_collection(RES_COL)

    print("\nInsertando colecciones (batch único)…")
    total_start = time.perf_counter()

    cat_time = insert_collection(db.get_collection(CAT_COL, write_concern=WriteConcern(w=0)),
                                 countries)
    print(f"  ✔ {CAT_COL}: {len(countries):,} docs | {cat_time:6.2f} s")

    res_time = insert_collection(db.get_collection(RES_COL, write_concern=WriteConcern(w=0)),
                                 reservations)
    print(f"  ✔ {RES_COL}: {len(reservations):,} docs | {res_time:6.2f} s")

    total_time = time.perf_counter() - total_start
    client.close()

    print("\nResumen")
    print("┌──────────────────┬─────────┐")
    print(f"│ {CAT_COL:<15} │ {cat_time:7.2f} │")
    print(f"│ {RES_COL:<15} │ {res_time:7.2f} │")
    print("├──────────────────┼─────────┤")
    print(f"│ TOTAL            │ {total_time:7.2f} │")
    print("└──────────────────┴─────────┘")

if __name__ == "__main__":
    main()
