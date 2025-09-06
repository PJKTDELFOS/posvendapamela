import psycopg2

conn = psycopg2.connect(
    dbname="posvendasdb",
    user="adminalbert",
    password="$Uc<0(JCBBLP2J^r",
    host="127.0.0.1",
    port="5433"
)
cur = conn.cursor()
cur.execute("SELECT 1;")
print(cur.fetchone())
conn.close()
