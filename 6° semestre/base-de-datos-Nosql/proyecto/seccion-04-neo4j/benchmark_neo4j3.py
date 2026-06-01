import time, importlib, mysql.connector as sql
from neo4j import GraphDatabase
TAB = importlib.util.find_spec("tabulate") is not None
if TAB: from tabulate import tabulate

MYSQL = dict(user="root", password="Epsilon22",
             host="localhost", database="HotelAnalytics")
NEO   = dict(uri="neo4j+s://0ba16138.databases.neo4j.io",
             user="neo4j",
             password="6JWD8Ri7C8C2NjGzi4VEfAxLibXwmKbOjbAirGzDXVw")

# ---- MySQL (usa calendar table ad-hoc) ------------------------------------
SQL = """
WITH RECURSIVE cal AS (
  SELECT DATE('2024-01-01') d UNION ALL
  SELECT DATE_ADD(d,INTERVAL 1 DAY) FROM cal WHERE d<'2024-12-31')
SELECT c.name AS pais, cal.d,
       COUNT(*) AS habitaciones
FROM   cal
JOIN   Reservation r ON cal.d BETWEEN r.check_in AND DATE_ADD(r.check_out,INTERVAL -1 DAY)
JOIN   Room rm ON rm.room_id=r.room_id
JOIN   Hotel h ON h.hotel_id=rm.hotel_id
JOIN   HotelChain hc ON hc.chain_id=h.chain_id
JOIN   Country c ON c.country_id=hc.country_id
GROUP  BY pais,cal.d
ORDER  BY habitaciones DESC
LIMIT 10;
"""

# ---- Cypher ---------------------------------------------------------------
CYPHER = """
MATCH (c:Country)-[:HOSTS_CHAIN]->(:HotelChain)-[:OPERATES]->(h:Hotel)
MATCH (h)-[:HAS_BOOKING]->(r:Reservation)
WHERE r.check_in.year = 2024
WITH c, r, r.check_in AS ci, r.check_out AS co
UNWIND range(0, duration.inDays(ci,co).days-1) AS offset
WITH c.name AS pais, (ci + duration({days:offset})) AS dia
RETURN pais, dia AS fecha, count(*) AS habitaciones
ORDER BY habitaciones DESC
LIMIT 10
"""

def run_mysql():
    cnx=sql.connect(**MYSQL);cur=cnx.cursor();t=time.perf_counter()
    cur.execute(SQL); rows=cur.fetchall(); dt=time.perf_counter()-t
    cur.close(); cnx.close(); return rows,dt

def run_neo():
    drv=GraphDatabase.driver(NEO["uri"],auth=(NEO["user"],NEO["password"]))
    with drv.session() as s:
        t=time.perf_counter()
        rows=[(r["pais"],str(r["fecha"]),r["habitaciones"]) for r in s.run(CYPHER)]
        dt=time.perf_counter()-t
    drv.close(); return rows,dt

hdr1=["País","Fecha","Habitaciones"]
sql_rows,ts=run_mysql(); neo_rows,tn=run_neo()

print("\n=== MySQL ==="); print(tabulate(sql_rows,hdr1,tablefmt="github") if TAB else sql_rows)
print("\n=== Neo4j ==="); print(tabulate(neo_rows,hdr1,tablefmt="github") if TAB else neo_rows)
print("\n=== Latencias ===")
print(tabulate([("MySQL",f"{ts:.3f}s"),("Neo4j",f"{tn:.3f}s")],["Motor","Tiempo"])
      if TAB else [ts,tn])
