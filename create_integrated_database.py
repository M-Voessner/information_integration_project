import psycopg2 as gres

# establish connection to postgres
def run():
    conn = gres.connect(
        dbname ="postgres", 
        user='postgres',
        host='postgres',
        #host='localhost',
        password='1234',
        #password='postgres',
        port='5432'
    )

    conn.autocommit = True

    # Get Cursor and create DB for integration project
    cursor = conn.cursor()

    dropTable = """DROP DATABASE IF EXISTS Books"""
    sql = '''
    CREATE DATABASE Books
    WITH
        OWNER = postgres
        TEMPLATE = template1
        ENCODING = 'UTF8'
        ALLOW_CONNECTIONS = true
        CONNECTION LIMIT = 15
    '''

    cursor.execute(dropTable)
    cursor.execute(sql)
    conn.close()
