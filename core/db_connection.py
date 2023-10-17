import psycopg2

conn = psycopg2.connect(
    host="db",
    port=5432,
    database="davidenkovision_dev",
    user="postgres",
    password="postgres",
)

cur = conn.cursor()
