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

        sql_create_books = '''
            DROP TABLE IF EXISTS books CASCADE;
            CREATE TABLE books (
                book_id INTEGER PRIMARY KEY,
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

        sql_create_genre_groups = '''
            DROP TABLE IF EXISTS genre_groups;
            CREATE TABLE genre_groups (
                book_id INTEGER,
                genre_id INTEGER,
                FOREIGN KEY (book_id) REFERENCES books(book_id),
                FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
            )
            '''
        sql_create_genres = '''
            DROP TABLE IF EXISTS genres CASCADE;
            CREATE TABLE genres (
                genre_id INTEGER PRIMARY KEY,
                genre_name VARCHAR(30)
            )
        '''

        cur.execute(sql_create_books)
        cur.execute(sql_create_genres)
        cur.execute(sql_create_genre_groups)
        cur.close()
        conn.commit()

    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error, flush=True)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    initial_connect()
