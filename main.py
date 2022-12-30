import psycopg2 as gres
from config import config

conn = None
try:
    # Read connection information
    params = config()

    # connect to PostgreSQL server
    conn = gres.connect(**params)
    conn.autocommit = True

    cur = conn.cursor()

    sql = """INSERT INTO books(book_id,title,author,publication_date,review,review_url,page_count,price,average_rating,cover)
    VALUES(1,'The Witches', 'Dal', TIMESTAMP '2011-05-16 15:36:38', '', '', 0,0,0,'')
    """

    cur.execute(sql)
    cur.close()
    conn.commit()

except (Exception, gres.DatabaseError) as error:
    print('FAILED: %s' % error, flush=True)
finally:
    if conn is not None:
        conn.close()


