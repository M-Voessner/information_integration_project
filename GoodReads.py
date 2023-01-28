from csv import DictReader
import pandas as pd


class ROW(object):
    """ Base class for row, define slots to prevent member creation """
    __slots__ = [
        'title',
        'author',
        'publication_date',
        'review',
        'review_url',
        'page_count',
        'price',
        'average_rating',
        'cover'
    ]


class Row(ROW):
    """ Class for row tuples with defined slots to prevent other members """
    __slots__ = [
        'title',
        'author',
        'publication_date',
        'review',
        'review_url',
        'page_count',
        'price',
        'average_rating',
        'cover'
    ]


class GoodReads():
    """ Container Class to load data from GoodReads csv data"""

    def __init__(self):
        """ Initializes data member to empty list """
        self.data = []
        self.data2 = pd.DataFrame()

    def load_good_reads_pandas(self, file='.\data_sources\\books_good_reads.csv'):
        df = pd.read_csv(file, on_bad_lines='skip',encoding='utf8')
        # Drop unnecessary columns
        df = df.drop(['isbn','text_reviews_count'],axis=1)

        # Rename columns, so they fit the global schema
        df = df.rename(columns={
        'authors':'author',
        'average_rating':'average_user_rating',
        'language_code':'language',
        '  num_pages':'page_count',
        'bookID':'book_id',
        'isbn13':'ISBN13'
        })

        # Change publication date format
        df['publication_date'] = pd.to_datetime(df['publication_date'], format='%m/%d/%Y', errors='coerce')
        
        df['author'] = df['author'].apply(lambda x: x.split("/")[0])

        # Add empty columns 
        df['price'] =  0.0
        df['currency'] =  'EUR'
        df['description'] = ''
        df['book_id'] = df['book_id'] + 2000
        self.data2 = df

    def load_good_reads(self, file='.\data_sources\books_good_reads.csv'):
        """ Reads data from csv file and expects the data to follow the schema of GoodReads """
        reader = None
        out = []
        try:
            with open(file, newline='\n', encoding='utf-8') as csvfile:
                reader = DictReader(csvfile)
                for row in reader:
                    r = Row()
                    # if index unknown the loop is sufficient, but index is known
                    # for column in ('pages', 'price','rating'):
                    #   r.'column' = row[reader.fieldnames.index(column)]
                    r.average_rating = row[4]
                    r.page_count = row[12]
                    r.price = row[-1]
                    out.append(r)
        except FileNotFoundError:
            raise
        if len(out) > 0:
            self.data = out
