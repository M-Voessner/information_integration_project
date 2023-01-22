from GoogleBooks import *
import GoodReads
import psycopg2 as gres
from config import config
import sys
from math import floor
import pandas as pd
import psycopg2.extras as extras

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

def get_consonants(text,component_length = 20):
    consonants = "bcdfghjklmnpqrstvwxyz1234567890"
    text = text.lower()
    key_component = ""
    count = 0
    for x in text:
        if x in consonants and count < component_length:
            count += 1
            key_component += x
    return key_component
def get_year(date):
    return str(date.year)

def transfer_to_global_schema(google_books_df, good_reads_df):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    global_df = pd.DataFrame()
    no_isbn_data = google_books_df[(google_books_df['isbn13'] == 0)]

    frames = [google_books_df,good_reads_df]
    global_df = pd.concat(frames)

    #Filter out 
    global_df = global_df.sort_values(by=['isbn13']).drop_duplicates('isbn13')

    frames = [global_df,no_isbn_data]
    global_df = pd.concat(frames)
    
    return global_df

def create_sorted_neighbourhood_keys(df):
    df['sorted_neighbourhood_key'] = df['title'].apply(lambda x: get_consonants(x)) + df['author'].apply(lambda x: get_consonants(x)) + df['publication_date'].apply(lambda x: get_year(x))
    df = df.sort_values(by='sorted_neighbourhood_key')
    return df

def detect_duplicates(df,window_size = 5, similarity_threshhold = 0.9):
    marked_for_deletion = []
    total_duplicates = 0
    #for index in range(len(df) - window_size):
    for index in range(len(df) - window_size):
        for offset in range(1, window_size):
            if jaro_distance(df.iloc[index]['sorted_neighbourhood_key'],df.iloc[index+offset]['sorted_neighbourhood_key']) > similarity_threshhold:
                marked_for_deletion.append(df.iloc[index+offset]["bookID"])
                # Take description if it is available
                if df.iloc[index]['description'] == '' and df.iloc[index+offset]['description'] != '':
                    df.iloc[index]['description'] = df.iloc[index+offset]['description']
                    #print("Description copied for row ",str(index))
                # Take better/more relevant ratings
                if df.iloc[index]['ratings_count'] < df.iloc[index+offset]['ratings_count']:
                    df.iloc[index]['ratings_count'] = df.iloc[index+offset]['ratings_count']
                    df.iloc[index]['average_user_rating'] = df.iloc[index+offset]['average_user_rating']
                    #print("Ratings copied for row ",str(index))
                # Take price if available
                if df.iloc[index]['price'] == 0 and df.iloc[index+offset]['price'] != 0:
                    df.iloc[index]['price'] = df.iloc[index+offset]['price']
                    #print("Price copied for row ",str(index))
                total_duplicates += 1
    # Remove duplicates from rows marked for deletion
    marked_for_deletion = list(dict.fromkeys(marked_for_deletion))

    # Reverse marked_for_deletion order
    marked_for_deletion = marked_for_deletion[::-1]

    print("Dropping duplicates...")
    # Drop duplicate rows from global data
    print(len(df))
    df = df[~df["bookID"].isin(marked_for_deletion)]
    print(len(df))
    print("Duplicates dropped: ", str(total_duplicates))
            
    return df

def jaro_distance(s1, s2):  
    # If the s are equal
    if (s1 == s2):
        return 1.0
 
    # Length of two s
    len1 = len(s1)
    len2 = len(s2)
 
    # Maximum distance upto which matching
    # is allowed
    max_dist = floor(max(len1, len2) / 2) - 1
 
    # Count of matches
    match = 0
 
    # Hash for matches
    hash_s1 = [0] * len(s1)
    hash_s2 = [0] * len(s2)
 
    # Traverse through the first
    for i in range(len1):
 
        # Check if there is any matches
        for j in range(max(0, i - max_dist),
                       min(len2, i + max_dist + 1)):
             
            # If there is a match
            if (s1[i] == s2[j] and hash_s2[j] == 0):
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break
 
    # If there is no match
    if (match == 0):
        return 0.0
 
    # Number of transpositions
    t = 0
    point = 0
 
    # Count number of occurrences
    # where two characters match but
    # there is a third matched character
    # in between the indices
    for i in range(len1):
        if (hash_s1[i]):
 
            # Find the next matched character
            # in second
            while (hash_s2[point] == 0):
                point += 1
 
            if (s1[i] != s2[point]):
                t += 1
            point += 1
    t = t//2
 
    # Return the Jaro Similarity
    return (match/ len1 + match / len2 +
            (match - t) / match)/ 3.0

def execute_values(conn, df, table):
  
    tuples = [tuple(x) for x in df.to_numpy()]
  
    cols = ','.join(list(df.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, gres.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("the dataframe is inserted")
    cursor.close()

conn = None
try:
    # Prepare data 
    good_reads_loader = GoodReads.GoodReads()
    good_reads_loader.load_good_reads_pandas()
    good_reads_loader.data2.info()
    google_books = read_GoogleBooks_file()

    global_data = transfer_to_global_schema(google_books, good_reads_loader.data2)

    global_data = create_sorted_neighbourhood_keys(global_data)

    global_data = detect_duplicates(global_data)

    # Read connection information
    params = config()

    # connect to PostgreSQL server
    conn = gres.connect(**params)
    conn.autocommit = True

    cur = conn.cursor()

    # I still need to remake the DB books table schema
    #execute_values(conn, global_data, 'books')

    sql = """INSERT INTO books(book_id,title,author,publication_date,review,review_url,page_count,price,average_rating,cover)
    VALUES(2,'The Witches', 'Dal', TIMESTAMP '2011-05-16 15:36:38', Null, Null, 0,0,0,'')
    """

    cur.execute(sql)
    cur.close()
    conn.commit()

except (Exception, gres.DatabaseError) as error:
    print('FAILED: %s' % error, flush=True)
finally:
    if conn is not None:
        conn.close()


