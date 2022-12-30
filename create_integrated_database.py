import psycopg2 as gres

# establish connection to postgres
conn = gres.connect(
    dbname ="postgres", 
    user='postgres',
    host='postgres',
    password='1234',
    port='5432'
)

conn.autocommit = True

# Get Cursor and create DB for integration project
cursor = conn.cursor()

sql = '''CREATE DATABASE Books
WITH
    OWNER = postgres
    TEMPLATE = template1
    ENCODING = 'UTF8'
    ALLOW_CONNECTIONS = true
    CONNECTION LIMIT = 15
'''

cursor.execute(sql)
conn.close()
