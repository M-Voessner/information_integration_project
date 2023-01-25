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

    sql = """INSERT INTO books(book_id,title,author,publication_date,review,review_url,page_count,price,average_rating,cover,genre)
    VALUES
    (1,'The Witches', 'Roald Dahl', TIMESTAMP '2002-01-13 00:00:00', Null, Null, 120,20,8.0,'', 'Thriller'),
    (2,'How To Win Friends and Influence People', 'Dale Carnegie', TIMESTAMP '2013-06-11 00:00:00', Null, Null, 320,51,8.6,'', 'SELF-HELP'),
    (3,'Death of a Bachelorette', 'Laura Levine', TIMESTAMP '2015-09-15 00:00:00', Null, Null, 204,29.90,7.9,'', 'THRILLER'),
    (4,'Murder on the Orient Express', 'Agatha Christie', TIMESTAMP '1985-06-15 00:00:00', Null, Null, 207,19.90,8.7,'', 'Detective and Mystery'),
    (5,'Ready Player One', 'Ernest Cline', TIMESTAMP '2011-08-11 00:00:00', Null, Null, 285,25,9.2,'', 'Action')
    """

    cur.execute(sql)
    cur.close()
    conn.commit()

except (Exception, gres.DatabaseError) as error:
    print('FAILED: %s' % error, flush=True)
finally:
    if conn is not None:
        conn.close()


