import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import json

class NYTimesExtractor():
    def __init__(self, apiKey):
        self.url = 'https://api.nytimes.com/svc/books/v3/reviews.json?api-key=' + apiKey
        self.data = []
        
    def getReviewWithTitle(self, title):
        print('Make api call for reviews with book title: ' + title)
        call = self.url + '&title=' + title
        response = requests.get(call)
        if (response.status_code == 200):
            response = response.json()['results']
            for i in range(len(response)):
                temp = {'review': None, 'review_url': None}
                review = self.getReview(response[i]['url'])
                temp['review'] = review
                temp['review_url'] = response[i]['url']
                self.data.append(temp)
        else:
            print('Error: ' + response.reason)
        
    def getReviewWithAuthor(self, author):
        print('Make api call for reviews with book author: ' + author)
        call = self.url + '&author=' + author
        response = requests.get(call)
        if (response.status_code == 200):
            response = response.json()['results']
            for i in range(len(response)):
                temp = {'review': None, 'review_url': None}
                review = self.getReview(response[i]['url'])
                temp['review'] = review
                temp['review_url'] = response[i]['url']
                self.data.append(temp)
        else:
            print('Error: ' + response.reason)
            
    def getReview(self, url):
        os.environ['MOZ_HEADLESS'] = '1'
        driver = webdriver.Firefox()
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        return soup.text
        
        
        
def main():
    #Api Key dont steal pls pBmtDGDaAMjxj1HhIzQoneHvdPMJlVxD
    extractor = NYTimesExtractor('pBmtDGDaAMjxj1HhIzQoneHvdPMJlVxD')
    extractor.getReviewWithTitle('the witches')
    print(extractor.data)
if __name__ == '__main__':
    main()