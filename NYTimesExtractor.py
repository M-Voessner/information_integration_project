import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os

class NYTimesExtractor():
    def __init__(self):
        self.url = 'https://api.nytimes.com/svc/books/v3/reviews.json?api-key=' + 'pBmtDGDaAMjxj1HhIzQoneHvdPMJlVxD'
        self.data = []
        
    def getReviewWithTitle(self, title):
        print('Make api call for reviews with book title: ' + title)
        call = self.url + '&title=' + title
        response = requests.get(call)
        if (response.status_code == 200):
            response = response.json()['results']
            print(response)
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
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36'}
        page = requests.get(url, headers=headers)
        if (page.status_code == 200):
            soup = BeautifulSoup(page.content, 'html.parser')
            return soup.get_text()
        else:
            return None
        
        
        
def main():
    #Api Key dont steal pls pBmtDGDaAMjxj1HhIzQoneHvdPMJlVxD
    extractor = NYTimesExtractor()
    extractor.getReviewWithTitle('the witches')
if __name__ == '__main__':
    main()