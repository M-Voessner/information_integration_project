import psycopg2 as gres
from config import config


def initial_connect() -> None:
    """ Connects to the database with the information provided in the database.ini file and creates the table on the first connection"""
    conn = None
    try:
        # Read connection information
        params = config()

        # connect to PostgreSQL server
        conn = gres.connect(**params)
        conn.autocommit = True

        cur = conn.cursor()

        sql = '''
            CREATE TABLE books (
                id INTEGER PRIMARY KEY,
                title VARCHAR(511),
                author VARCHAR(255),
                publication_date DATE,
                review TEXT,
                review_url VARCHAR(511),
                page_count INTEGER,
                price NUMERIC(8, 2),
                average_rating NUMERIC(4,2),
                cover VARCHAR(511)
            )
        '''

        cur.execute(sql)
        cur.close()
        conn.commit()

    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error, flush=True)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    initial_connect()
