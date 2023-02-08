#!/usr/bin/env python
from flask import Flask, jsonify, request
import psycopg2 as gres
import main
from config import config
from flask_cors import CORS
import main
from NYTimesExtractor import NYTimesExtractor

# creating a Flask app
app = Flask(__name__)
CORS(app)



def getReviewByTitle(list, term):
    for i in list:
        if ('title' in i.keys()):
            if (i['title']== term):
                return i
        elif ('book_title' in i.keys()):
            if (i['book_title'] ==term):
                return i
    return {'review': None, 'review_url': None, 'summary': None}
      
@app.route('/load_data', methods = ['GET'])
def loadDatabase():
    main.main()
    return jsonify({'success': True})

@app.route('/', methods = ['GET'])
def home():
    return jsonify({'routes': ['all_books', 'books'], 'args': ['title', 'author']})

@app.route('/all_books', methods = ['GET'])
def allBooks():
    conn = None
    try:
        sql = """SELECT * FROM BOOKS b 
            JOIN GENRE_GROUPS gg ON b.book_id = gg.book_id
            JOIN GENRES ge ON ge.genre_id = gg.genre_id"""
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        books = cur.fetchall()
        result = []
        for row in books:
            temp = {}
            temp['book_id'] = row[0]
            temp['autor'] = row[1]
            temp['title'] = row[2]
            temp['average_rating'] = row[3]
            temp['ratings_count'] = row[4]
            temp['price'] = row[5]
            temp['currency'] = row[6]
            temp['description'] = row[7]
            temp['publisher'] = row[8]
            temp['review']= row[9]
            temp['review_url'] = row[10]
            temp['page_count'] = row[11]
            temp['ISBN13'] = row[12]
            temp['language'] = row[13]
            temp['publication_date'] = row[14]
            temp['cover'] = row[15]
            temp['genre'] = row[19]
            result.append(temp)
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error, flush=True)
    finally:
        if conn is not None:
            conn.close()
            
@app.route('/all_titles', methods = ['GET'])
def alltitles():
    conn = None
    try:
        sql = """SELECT title FROM books"""
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        books = cur.fetchall()
        result = []
        for row in books:
            result.append(row[0])
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error, flush=True)
    finally:
        if conn is not None:
            conn.close()
            
@app.route('/all_authors', methods = ['GET'])
def allAuthors():
    conn = None
    try:
        sql = """SELECT author FROM books"""
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        books = cur.fetchall()
        result = []
        for row in books:
            result.append(row[0])
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error, flush=True)
    finally:
        if conn is not None:
            conn.close()
            
@app.route('/all_genres', methods = ['GET'])
def allGenres():
    conn = None
    try:
        sql = """SELECT genre_name FROM genres"""
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        books = cur.fetchall()
        result = []
        for row in books:
            result.append(row[0])
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error, flush=True)
    finally:
        if conn is not None:
            conn.close()
  
  
@app.route('/get_review', methods = ['GET'])
def getReview():
    args = request.args
    book_id = args.get('book_id')
    extractor = NYTimesExtractor()
    
    
    conn = None
    try:
        sql = """SELECT * FROM books WHERE book_id = %s"""
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql,(book_id,))
        books = cur.fetchall()
        review = {'review': None, 'review_url': None, 'summary': None}
        for row in books:
            if (row[9] is not None):
                return jsonify({'review': row[9], 'review_url': row[10]})
            else:
                extractor.getReviewWithTitle(row[2])
                review = getReviewByTitle(extractor.data, row[2])
                print(extractor.data)
                print(review)
                if (review['review'] == None):
                    review['review'] = review['summary']
                if (review['review_url'] is not None):
                    cur.execute("""
                        UPDATE books 
                        SET review_url = %s, review = %s
                        WHERE book_id = %s""",(review['review_url'], review['review'], book_id,))
        return jsonify(review)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error, flush=True)
    finally:
        if conn is not None:
            conn.close()

@app.route('/books', methods = ['GET'])
def disp():
    conn = None
    first = 10000000
    skip = 0
    try:
        args = request.args
        print(args)
        title = args.get('title')
        author = args.get('author')
        average_rating = args.get('average_rating')
        sign = args.get('sign')
        genre_name = args.get('genre_name')
        date = args.get('date')
        page_count = args.get('page-count')
        price = args.get('price')
        first = args.get('first')
        skip = args.get('skip')
        sql = """SELECT *, count(*) OVER() AS full_count FROM BOOKS b 
            LEFT JOIN GENRE_GROUPS gg ON b.book_id = gg.book_id
            LEFT JOIN GENRES ge ON ge.genre_id = gg.genre_id
            """
        sqlparams = {}
        where = []
        
        if (title):
            where.append("""title LIKE %(title)s""")
            sqlparams['title'] = '%{}%'.format(title)
        if (author):
            where.append("""author LIKE %(author)s""")
            sqlparams['author']='%{}%'.format(author)
        if (average_rating):
            where.append("""average_rating """ + sign +  """ %(average_rating)s""")
            sqlparams['average_rating'] = average_rating 
        if (genre_name):
            where.append("""genre_name = %(genre_name)s""")
            sqlparams['genre_name']=genre_name
        if (date):
            where.append("""publication_date = %(date)s""")
            sqlparams['date']=date
        if (page_count):
            where.append("""page_count = %(page_count)s""")
            sqlparams['page_count']=page_count
        if (price):
            where.append("""price = %(price)s""")
            sqlparams['price']=price
        if where:
            sql = '{} WHERE {}'.format(sql, ' AND '.join(where))
        sql += """LIMIT %(first)s OFFSET %(skip)s"""
        
        sqlparams['first'] = first
        sqlparams['skip'] = skip
        _sql = sql,sqlparams
        print(_sql)
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        
        cur.execute(*_sql)
        books = cur.fetchall()
        print(books)
        result = []
        
        for row in books:
            temp = {}
            temp['book_id'] = row[0]
            temp['author'] = row[1]
            temp['title'] = row[2]
            temp['average_rating'] = row[3]
            temp['ratings_count'] = row[4]
            temp['price'] = row[5]
            temp['currency'] = row[6]
            temp['description'] = row[7]
            temp['publisher'] = row[8]
            temp['review']= row[9]
            temp['review_url'] = row[10]
            temp['page_count'] = row[11]
            temp['ISBN13'] = row[12]
            temp['language'] = row[13]
            temp['publication_date'] = row[14]
            temp['cover'] = row[15]
            temp['genre'] = row[19]
            temp['result_count'] = row[20]
            result.append(temp)
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error, flush=True)
    finally:
        if conn is not None:
            conn.close()

@app.route('/chart_years', methods = ['GET'])
def getYearData():
    conn = None
    try:
        sql = """
        SELECT EXTRACT(YEAR FROM publication_date) AS Year, COUNT(*) 
        FROM books 
        GROUP BY Year 
        ORDER BY Year
        """
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        result = []
        for r in data:
            result.append((r[0], r[1]))
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error , flush=True)
    finally:
        if conn is not None:
            conn.close()

@app.route('/chart_rates', methods = ['GET'])
def getRateData():
    conn = None
    try:
        sql = """
        SELECT TRUNC(average_rating) AS Rating, COUNT(*) 
        FROM books
        GROUP BY Rating
        ORDER BY Rating 
        """
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        result = []
        for r in data:
            result.append((r[0], r[1]))
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error , flush=True)
    finally:
        if conn is not None:
            conn.close()

@app.route('/chart_rates_detail', methods = ['GET'])
def getRateStackData():
    conn = None
    try:
        sql = """
        SELECT TRUNC(average_rating) AS index, TRUNC(average_rating, 1) AS Rating, COUNT(average_rating)
        FROM books
        GROUP BY Rating, index
        ORDER BY Rating 
        """
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        result = []
        for r in data:
            result.append((r[0], r[1], r[2]))
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error , flush=True)
    finally:
        if conn is not None:
            conn.close()

@app.route('/chart_info', methods = ['GET'])
def getInfoChartData():
    conn = None
    try:
        sql = """
        SELECT COUNT(DISTINCT(title)) AS title_count, COUNT(DISTINCT(author)) AS author_count 
        FROM books
        """
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        result = []
        for r in data:
            result.append((r[0], r[1]))
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error , flush=True)
    finally:
        if conn is not None:
            conn.close()

# driver function
if __name__ == '__main__':

    app.run(debug = True)