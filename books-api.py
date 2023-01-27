#!/usr/bin/env python
from flask import Flask, jsonify, request
import psycopg2 as gres
from config import config
from flask_cors import CORS
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
      
@app.route('/', methods = ['GET'])
def home():
    return jsonify({'routes': ['all_books', 'books'], 'args': ['title', 'author']})

@app.route('/all_books', methods = ['GET'])
def allBooks():
    conn = None
    try:
        sql = """SELECT * FROM books"""
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
            temp['title'] = row[1]
            temp['author'] = row[2]
            temp['publication_date'] = row[3]
            temp['review'] = row[4]
            temp['review_url'] = row[5]
            temp['page_count'] = row[6]
            temp['price'] = row[7]
            temp['rating'] = row[8]
            temp['cover']= row[9]
            temp['genre'] = row[10]
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
            if (row[5] is not None):
                return jsonify({'review': row[4], 'review_url': row[5]})
            else:
                extractor.getReviewWithTitle(row[1])
                review = getReviewByTitle(extractor.data, row[1])
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
    try:
        args = request.args
        title = args.get('title')
        author = args.get('author')
        rating = args.get('rating')
        genre = args.get('genre')
        date = args.get('date')
        page_count = args.get('page-count')
        price = args.get('price')
        print(args)
        sql = """SELECT * FROM books"""
        where = []
        sqlparams = {}
        if (title):
            where.append("""title = %(title)s""")
            sqlparams['title'] = title
        if (author):
            where.append("""author = %(author)s""")
            sqlparams['author']=author
        if (rating):
            where.append("""average_rating = %(rating)s""")
            sqlparams['rating']=rating
        if (genre):
            where.append("""genre = %(genre)s""")
            sqlparams['genre']=genre
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
        _sql = sql,sqlparams
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(*_sql)
        books = cur.fetchall()
        result = []
        
        for row in books:
            temp = {}
            temp['book_id'] = row[0]
            temp['title'] = row[1]
            temp['author'] = row[2]
            temp['publication_date'] = row[3]
            temp['review'] = row[4]
            temp['review_url'] = row[5]
            temp['page_count'] = row[6]
            temp['price'] = row[7]
            temp['rating'] = row[8]
            temp['cover']= row[9]
            temp['genre'] = row[10]
            result.append(temp)
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error, flush=True)
    finally:
        if conn is not None:
            conn.close()
  
# driver function
if __name__ == '__main__':
    print('Test')

    app.run(debug = True)