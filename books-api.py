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
    return {'review': None, 'review_url': None}
      
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
            result.append(temp)
        return jsonify(result)
    except (Exception, gres.DatabaseError) as error:
        print('FAILED: %s' % error, flush=True)
    finally:
        if conn is not None:
            conn.close()
  
@app.route('/books', methods = ['GET'])
def disp():
    conn = None
    try:
        extractor = NYTimesExtractor()
        args = request.args
        title = args.get('title')
        author = args.get('author')
        if (title):
            term = title
            extractor.getReviewWithTitle(term)
            sql = """SELECT * FROM books WHERE title = %s"""
        if (author):
            term = author
            extractor.getReviewWithAuthor(term)
           
            sql = """SELECT * FROM books WHERE author = %s"""
        print(extractor.data)
        params = config()
        conn = gres.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql, (term,))
        books = cur.fetchall()
        result = []
        
        for row in books:
            temp = {}
            temp['book_id'] = row[0]
            temp['title'] = row[1]
            temp['author'] = row[2]
            temp['publication_date'] = row[3]
            temp['review'] = getReviewByTitle(extractor.data, row[1])['review']
            temp['review_url'] = getReviewByTitle(extractor.data, row[1])['review_url']
            temp['page_count'] = row[6]
            temp['price'] = row[7]
            temp['rating'] = row[8]
            result.append(temp)
            if(row[5] == None):
                #Update review_url in db
                cur.execute("""
                            UPDATE books 
                            SET review_url = %s
                            WHERE book_id = %s""",(extractor.data[0]['review_url'], row[0],))
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