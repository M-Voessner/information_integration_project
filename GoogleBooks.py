import pandas as pd
import re

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def create_genre_keys(df):
    # Split genres column into lists 
    df['generes'] = df['generes'].str.replace(r'\&amp', '').str.replace(r' ', '').str.split(',')

    # Combine all genres and sort them
    genres = df.generes.sum()
    genres.sort()

    # Convert back to dataframe and remove duplicates
    genres_df = pd.DataFrame(genres,columns = ['genres'])
    genres_df = genres_df.drop_duplicates()

    # Generate genre keys
    genres_df = genres_df.reset_index()
    genres_df = genres_df.rename(columns={"index":"genre_ID"})
    genres_df = genres_df.rename(columns={"genres":"genre_name"})
    genres_df['genre_ID'] = genres_df.index
    genres_df['genre_ID']= genres_df['genre_ID'].astype("string")
    
    return genres_df
    

def format_date(df):
    # Month name to month number dictionary
    month_dict = {"Jan" : '1,' , 'Feb' : '2,' , 'Mar' : '3,',
                  "Apr" : '4,' , 'May' : '5,' , 'Jun' : '6,',
                  "Jul" : '7,' , "Aug" : '8,' , 'Sep' : '9,',
                  "Oct" : '10,', "Nov" : "11,", "Dec" : '12,'}

    #Replace month names with numeral values
    df['published_date'] = df['published_date'].replace(month_dict, regex = True).str.replace(" ", "")

    #Filter out invalid dates (one record has unformattable date)
    df = df[df.published_date.str.count(",").eq(2)]

    #Convert strings to YYYY-MM-DD
    df['published_date'] = pd.to_datetime(df['published_date'], format="%m,%d,%Y")

    # Rename to fit global schema
    df = df.rename(columns={"published_date":"publication_date"})
    return df

#The price value in Google Books data set is given for SAR (Saudi Riyal) currency, we are converting it to EUR (around 1 SAR = 0.25 EUR)
def convert_price(df):
    df['price'] = df['price'].apply(lambda x: x/4).round(2)
    df['currency'] = 'EUR'
    return df

#Some rows contain invalid ISBN values
def filter_ISBNs(df):
    df['ISBN'] = df['ISBN'].apply(lambda x: x if x.isnumeric() else 0)
    # Change ISBN format to int
    df['ISBN'] = df['ISBN'].astype('int64')
    df = df.rename(columns={"ISBN":"isbn13"})
    return df

def change_language_naming_convention(df):
    # All language values are 'English', we set it to 'eng', as in the other data source
    df['language'] = 'eng'
    return df

def cast_vote_quantity_to_int(df):
    df['voters'] = df['voters'].str.replace(',', '').fillna(0).astype('int64')
    df = df.rename(columns={"voters":"ratings_count"})
    return df

def clean_dataset(df):
    df = format_date(df)
    df = convert_price(df)
    df = filter_ISBNs(df)
    df = change_language_naming_convention(df)
    df = cast_vote_quantity_to_int(df)

    # Change rating column name to fit global schema
    df = df.rename(columns={"rating":"average_user_rating"})
    # Drop genres column, since there's a special table for that
    df = df.drop('generes',axis=1)

    return df

def create_genre_groups(df,genres):
    genre_dict = genres.set_index("genre_name").to_dict()

    df['generes'] = [','.join(map(str, l)) for l in df['generes']]
    df['generes'] = df['generes'].replace(genre_dict.get('genre_ID'), regex = True).str.replace(",", " ").apply(lambda x : re.sub(r'[A-z]', '', x))
    
    df = df.reset_index()
    df['genre_group_key'] = df.index
    df['genre_group_key'] = df['genre_group_key'].astype("string")
    genre_group_key_dict = df['generes'].to_dict()
    genre_groups = df['generes'].str.split(' ')
    genre_group_keys = df['genre_group_key']

    genres_df = pd.DataFrame({'genre_group_key' : genre_group_keys ,'genres' : genre_groups})

    return genres_df.explode('genres')

def read_GoogleBooks_file():

    df = pd.read_csv('.\data_sources\google_books_1299.csv',encoding='utf8')

    #df = clean_dataset(df)
    #df = df.rename(columns={"Unnamed: 0":"bookID"})
    
    genres = create_genre_keys(df)

    genre_groups = create_genre_groups(df,genres)
    
    # This is for testing purposes   
    #pd.set_option('display.max_columns', None)
    #pd.set_option('display.max_rows', None)

    df = clean_dataset(df)
    df = df.rename(columns={"Unnamed: 0":"bookID"})
    return df



