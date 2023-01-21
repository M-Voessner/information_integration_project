from csv import DictReader


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
    __slots__ = ''


class GoodReads():
    """ Container Class to load data from GoodReads csv data"""

    def __init__(self):
        """ Initializes data member to empty list """
        self.data = []

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
