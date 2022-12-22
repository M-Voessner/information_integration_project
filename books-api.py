from flask import Flask, jsonify, request
import psycopg2 as gres
from config import config
  
# creating a Flask app
app = Flask(__name__)
  
# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/all_books', methods = ['GET'])
def allBooks():
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
  
  
# A simple function to calculate the square of a number
# the number to be squared is sent in the URL when we use GET
# on the terminal type: curl http://127.0.0.1:5000 / home / 10
# this returns 100 (square of 10)
@app.route('/books', methods = ['GET'])
def disp():
    try:
        args = request.args
        title = args.get('title')
        author = args.get('author')
        if (title):
            term = title
            sql = """SELECT * FROM books WHERE title = %s"""
        if (author):
            term = author
            sql = """SELECT * FROM books WHERE author = %s"""
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
  
# driver function
if __name__ == '__main__':
        

    app.run(debug = True)