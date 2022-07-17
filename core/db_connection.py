import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="davidenkovision_dev",
    user="postgres",
    password="postgres")

cur = conn.cursor()
