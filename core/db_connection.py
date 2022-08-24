import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5413,
    database="davidenkovision_dev",
    user="postgres",
    password="postgres",
)

cur = conn.cursor()
