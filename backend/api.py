import requests
import os
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import re
import json

load_dotenv()

API_KEY = os.getenv('API_KEY')

def get_imdb_reviews(title:str):

    def search_movie():
        url = 'https://imdb8.p.rapidapi.com/v2/search'
        params = {
            'searchTerm': title,
            'type': 'MOVIE'
        }
        headers = {
            'x-rapidapi-host': 'imdb8.p.rapidapi.com',
            'x-rapidapi-key': API_KEY,
        }

        res = requests.get(url, params=params, headers=headers)
        if (res.status_code != 200):
            return {'error': f'API error: {res.status_code}'}
        return res.json()['data']['mainSearch']['edges'][0]['node']['entity']
    
    movie = search_movie()
    if not movie:
        return {'error': f"Cannot find movie named {movie['titleText']}"}
    
    print(movie['id'], movie['titleText']['text'])

    def get_reviews():
        url = 'https://imdb8.p.rapidapi.com/title/v2/get-user-reviews-summary'
        params = {
            'tconst': movie['id']
        }
        headers = {
            'x-rapidapi-host': 'imdb8.p.rapidapi.com',
            'x-rapidapi-key': API_KEY
        }
        res = requests.get(url, params=params, headers=headers)
        if res.status_code != 200:
            return {'error': f'API error: {res.status_code}'}
        return res.json()['data']['title']['featuredReviews']['edges']
    
    review_list = get_reviews()
    if not review_list:
        return {'error': 'No reviews found'}
    
    reviews = []

    try:
        seen_ids = set()
        for review in review_list:
            if review['node']['id'] not in seen_ids:
                seen_ids.add(review['node']['id'])
                reviews.append({
                    'Title': title,
                    'Platform': 'IMDb',
                    'Date': review['node']['submissionDate'],
                    'Comment': review['node']['text']['originalText']['plainText'],
                    'Type': review['node']['__typename'],
                    'Sentiment': 'Positive'
                })
    except:
        return {'error': 'No reviews found'}
    
    return reviews


def get_rttm_reviews(title:str, mode:str='user', limit:int=5, offset:int=0):

    def search_movie():
        url = f'https://www.rottentomatoes.com/search'
        params = {
            'search': title,
        }
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, params=params, headers=headers)
        if res.status_code != 200:
            return {'error': f'Failed to get response: {res.status_code}'}
        soup = BeautifulSoup(res.text, 'html.parser')

        movie = soup.find('search-page-media-row')
        if not movie:
            return {'error': f'Cannot find movie named {title}'}
        tag = movie.find('a', slot='title')
        movie_title = tag.text.strip()
        suburl = tag['href']
        return {
            'title': movie_title,
            'suburl': suburl
        }
    
    def get_reviews(title, url):
        if mode=='user':
            url = url + "?type=user"

        headers = {'User-Agent':'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        reviews = []

        review_elements = soup.find_all('div', {'data-qa': 'review-item'})

        if not review_elements:
            return {'error': 'No reviews found'}
        try:
            for element in review_elements[offset:offset+limit]:
                if mode == 'user':
                    review_tag = element.find('p', {'data-qa': 'review-text'})
                    date_tag = element.find('span', {'data-qa': 'review-duration'})
                else: 
                    review_tag = element.find('p', {'data-qa':'review-quote'})
                    date_tag = element.find('span', {'data-qa': 'review-date'})

                if review_tag and date_tag:
                    review= review_tag.text.strip()
                    date = date_tag.text.strip()
                    reviews.append({
                        'Title': title,
                        'Platform': 'Rotten Tomatoes',
                        'Date': date,
                        'Comment': review,
                        'Type': 'Critic' if mode =='critic' else 'Review',
                        'Sentiment': 'Positive',
                    })
        except IndexError:
            return {'error': 'Out of range'}
        return reviews
    
    result = search_movie()
    if 'error' in result:
        return result
    url = result['suburl'] + '/reviews'
    reviews = get_reviews(result['title'], url)
    return reviews


def get_metacritic_reviews(title:str, mode:str='user', limit:int=5, offset:int=0):
    
    def search_movie():
        url = f'https://www.metacritic.com/search/{title}/?page=1&category=2'
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return {'error': f'Failed to get response: {res.status_code}'}
        
        soup = BeautifulSoup(res.text, 'html.parser')
        movie = soup.find('div', class_='g-grid-container u-grid-columns')
        if not movie:
            return {'error': f'Cannot find movie named {title}'}
        tag = movie.find('a', {'data-testid': 'search-result-item'})
        suburl = tag['href']
        movie_title = tag.find('p').text.strip()
        return {
            'title': movie_title,
            'suburl': suburl
        }
    
    def fix_invalid_json(json_str):
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][\w]*)(\s*:)', r'\1"\2"\3', json_str)
        json_str = json_str.replace('\\u002F', '/')
        lowercase = [chr(i) for i in range(ord('a'), ord('z') + 1)]
        uppercase = [chr(i) for i in range(ord('A'), ord('D') + 1)]
        invalid_values = lowercase + uppercase
        for val in invalid_values:
            json_str = re.sub(rf':{val}', rf':"{val}"', json_str)
            json_str = re.sub(rf':\[*{val}\]*', rf':["{val}"]', json_str)
        
        return json_str
    
    def get_reviews(title, url):
        if mode == 'user':
            url = url + 'user-reviews/'
        else: url = url + 'critic-reviews/'
        url = url + '?sort-by=Recently%20Added'

        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return {'error': f'Failed to get response: {res.status_code}'}
        soup = BeautifulSoup(res.text, 'html.parser')
        script_tag = soup.find('script', string=re.compile('window\.__NUXT__'))
        match = re.search(r'm.components=(\[.*?\]);m.footer', script_tag.string, re.DOTALL)
        if not match:
            return {'error': 'Scrape error'}
        json_str = match.group(1)
        json_str = fix_invalid_json(json_str)
        data = json.loads(json_str)
        review_elements = data[2]['items']
        reviews = []
        try:
            for review in review_elements[offset:offset+limit]:
                    reviews.append({
                        'Title': title,
                        'Platform': 'Metacritic',
                        'Date': review['date'],
                        'Comment': review['quote'],
                        'Type': 'Critic' if mode =='critic' else 'Review',
                        'Sentiment': 'Positive',
                    })
        except IndexError:
            return {'error': 'Out of range'}
        return reviews
        
    result = search_movie()
    if 'error' in result:
        return result
    url = 'https://www.metacritic.com' + result['suburl']
    reviews = get_reviews(result['title'], url)
    return reviews