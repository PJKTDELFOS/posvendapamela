import psycopg2
conn = psycopg2.connect(
    dbname='pos_vendas_otica',
    user='adminalbert',
    password='15Al1992A',
    host='127.0.0.1',
    port=5433
)
print("Conectado com sucesso")
conn.close()