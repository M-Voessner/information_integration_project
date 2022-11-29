import pandas as pd
import re

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
    df = pd.read_csv('.\data_sources\google_books_1299.csv')

    df = format_date(df)

    genres = create_genre_keys(df)

    genre_groups = create_genre_groups(df,genres)
    
    #print(df['published_date'])
    #print(genres)
    #print(genre_groups)


read_GoogleBooks_file()
