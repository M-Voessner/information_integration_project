from GoogleBooks import *
import GoodReads
import psycopg2 as gres
from config import config
import sys
from math import floor
import pandas as pd
import numpy as np
import psycopg2.extras as extras
import create_integrated_database
import connect

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
    global_df = pd.DataFrame()
    no_isbn_data = google_books_df[(google_books_df['ISBN13'] == 0)]

    frames = [google_books_df,good_reads_df]
    global_df = pd.concat(frames)

    #Filter out 
    global_df = global_df.sort_values(by=['ISBN13']).drop_duplicates('ISBN13')

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
                marked_for_deletion.append(df.iloc[index+offset]["book_id"])
                # Take description if it is available
                if df.iloc[index]['description'] == '' and df.iloc[index+offset]['description'] != '':
                    df.iloc[index]['description'] = df.iloc[index+offset]['description']
                    df.iloc[index]['book_id'] = df.iloc[index+offset]['book_id']
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
    df = df[~df["book_id"].isin(marked_for_deletion)]
    print(len(df))
    print("Duplicates dropped: ", str(total_duplicates))

    # Drop and renaming columns to fit DB schema
    df = df.drop('sorted_neighbourhood_key',axis=1)
    df = df.rename(columns={"average_user_rating":"average_rating"})       
    df = df.replace({np.nan: None})        
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

def execute_values(conn, df, table,load_genre_groups = False, book_ids = []):
  
    tuples = [tuple(x) for x in df.to_numpy()]
    # For genre groups, filter non existant book_ids
    if load_genre_groups:
        new_tuples = []
        for t in tuples:
            if int(t[0]) in (book_ids) and int(t[1]) < 273:
                #print(t[0], " exists")
                new_tuples.append(t)
        tuples = new_tuples 
    
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
    print("The dataframe has been inserted")
    cursor.close()

conn = None
try:
    # Prepare data 
    good_reads_loader = GoodReads.GoodReads()
    good_reads_loader.load_good_reads_pandas()

    google_books, genres, genre_groups = read_GoogleBooks_file()

    global_data = transfer_to_global_schema(google_books, good_reads_loader.data2)

    global_data = create_sorted_neighbourhood_keys(global_data)

    global_data = detect_duplicates(global_data)

    book_ids = global_data['book_id'].tolist()
    
    '''
    # Display global data preview
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    print(global_data.info())
    print(global_data.head(3))
    '''

    # Read connection information
    params = config()

    # connect to PostgreSQL server
    conn = gres.connect(**params)
    
    ''' Local DB connection
    conn = gres.connect(
        dbname ="postgres", 
        user='postgres',
        host='postgres',
        #host='localhost',
        password='1234',
        #password='postgres',
        port='5432'
        )
    '''
    conn.autocommit = True

    cur = conn.cursor()
    
    
    create_integrated_database.run()
    connect.initial_connect()

    execute_values(conn, global_data, 'books')
    execute_values(conn, genres, 'genres')
    execute_values(conn, genre_groups, 'genre_groups',True,book_ids)
    
    #cur.execute(sql)
    cur.close()
    conn.commit()

except (Exception, gres.DatabaseError) as error:
    print('FAILED: %s' % error, flush=True)
finally:
    if conn is not None:
        conn.close()


