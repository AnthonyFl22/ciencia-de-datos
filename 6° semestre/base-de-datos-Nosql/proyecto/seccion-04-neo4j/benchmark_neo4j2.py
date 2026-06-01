import time, importlib, mysql.connector as sql
from neo4j import GraphDatabase
TAB = importlib.util.find_spec("tabulate") is not None
if TAB: from tabulate import tabulate

MYSQL = dict(user="root", password="Epsilon22",
             host="localhost", database="HotelAnalytics")
NEO   = dict(uri="neo4j+s://0ba16138.databases.neo4j.io",
             user="neo4j",
             password="6JWD8Ri7C8C2NjGzi4VEfAxLibXwmKbOjbAirGzDXVw")

SQL = """
SELECT c.name AS pais, h.name AS hotel,
       ROUND(AVG(DATEDIFF(r.check_out,r.check_in)),2) AS noches,
       COUNT(*) AS reservas
FROM   Reservation r
JOIN   Room rm  ON rm.room_id  = r.room_id
JOIN   Hotel h  ON h.hotel_id  = rm.hotel_id
JOIN   HotelChain hc ON hc.chain_id = h.chain_id
JOIN   Country c ON c.country_id    = hc.country_id
WHERE  r.check_in BETWEEN '2024-01-01' AND '2024-12-31'
GROUP  BY pais,hotel
HAVING reservas >= 50
ORDER  BY noches DESC
LIMIT 10;
"""

CYPHER = """
MATCH (c:Country)-[:HOSTS_CHAIN]->(:HotelChain)-[:OPERATES]->(h:Hotel)
MATCH (h)-[:HAS_BOOKING]->(r:Reservation)
WHERE r.check_in >= date('2024-01-01') AND r.check_in < date('2025-01-01')
WITH c.name AS pais, h.name AS hotel,
     avg(duration.inDays(r.check_in,r.check_out).days) AS noches,
     count(r) AS reservas
WHERE reservas >= 50
RETURN pais,hotel, round(noches,2) AS noches, reservas
ORDER BY noches DESC
LIMIT 10
"""

def run_mysql():
    cnx = sql.connect(**MYSQL); cur = cnx.cursor(); t=time.perf_counter()
    cur.execute(SQL); rows=cur.fetchall(); dt=time.perf_counter()-t
    cur.close(); cnx.close(); return rows,dt

def run_neo():
    drv=GraphDatabase.driver(NEO["uri"],auth=(NEO["user"],NEO["password"]))
    with drv.session() as s:
        t=time.perf_counter()
        rows=[(r["pais"],r["hotel"],r["noches"],r["reservas"]) for r in s.run(CYPHER)]
        dt=time.perf_counter()-t
    drv.close(); return rows,dt

hdr = ["País","Hotel","Noches","Reservas"]
sql_rows,ts = run_mysql()
neo_rows,tn = run_neo()

print("\n=== MySQL ==="); print(tabulate(sql_rows,hdr,tablefmt="github") if TAB else sql_rows)
print("\n=== Neo4j ==="); print(tabulate(neo_rows,hdr,tablefmt="github") if TAB else neo_rows)
print("\n=== Latencias ===")
print(tabulate([("MySQL",f"{ts:.3f}s"),("Neo4j",f"{tn:.3f}s")],["Motor","Tiempo"])
      if TAB else [ts,tn])
