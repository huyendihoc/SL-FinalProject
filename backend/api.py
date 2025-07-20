import requests
import os
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

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
            return {'error': 'API error'}
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
            return {'error': 'API error'}
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
            return {'error': 'Failed to get response'}
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
            return {'error': 'Failed to get response'}
        
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
    
    def get_reviews(title, url):
        if mode == 'user':
            url = url + 'user-reviews/'
        else: url = url + 'critic-reviews/'
        url = url + '?sort-by=Recently%20Added'

        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--window-size=1920,1080')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-extensions')
        opts.add_argument('--disable-software-rasterizer')
        opts.add_argument('--disable-logging')
        opts.add_argument('--log-level=3')
        opts.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        
        prefs = {
            'profile.managed_default_content_settings.images': 2,
            'profile.default_content_setting_values.javascript': 1,
        }
        opts.add_experimental_option('prefs', prefs)

        browser = webdriver.Chrome(options=opts)
        browser.get(url)
        html_text = browser.page_source
        browser.quit()
        soup = BeautifulSoup(html_text, 'html.parser')
        
        review_elements = soup.find_all('div', class_ = 'c-siteReview_main')
        if not review_elements:
            return {'error': 'No reviews found'}
        reviews = []
        try:
            for element in review_elements[offset:offset+limit]:
                date_tag = element.find('div', class_='c-siteReviewHeader_reviewDate')
                review_tag = element.find('div', class_='c-siteReview_quote')
                date = date_tag.text.strip()
                review = review_tag.find('span').text.strip()
                reviews.append({
                    'Title': title,
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
    url = 'https://www.metacritic.com' + result['suburl']
    reviews = get_reviews(result['title'], url)
    return reviews