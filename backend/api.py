import requests
import os
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from models import getBertSentiment
from translate_t5 import translate_reviews
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
METACRITIC_KEY = os.getenv('METACRITIC_KEY')
OMDB_KEY = os.getenv('OMDB_KEY')

# def autoComplete(title:str):
#     url = f'https://imdb236.p.rapidapi.com/api/imdb/autocomplete'
#     params = {
#         'query': title
#     }
#     headers = {
#         'x-rapidapi-host': 'imdb236.p.rapidapi.com',
#         'x-rapidapi-key': API_KEY,
#     }
#     res = requests.get(url, params=params, headers=headers)
#     if res.status_code != 200:
#         return {'error': f'API error: {res.status_code}'}
#     result_list = res.json()
#     seen_ids = set()
#     results = []
#     for res in result_list:
#         if res['id'] not in seen_ids and res['type'] == 'movie':
#             score = fuzz.token_sort_ratio(title.lower(), title.lower())
#             results.append((score, {
#                 "imdbID": res['id'],
#                 "Title": res['primaryTitle'],
#                 "Year": res['startYear'],
#                 "Type": res['type'],
#                 "Poster": res['primaryImage']
#             }))

#     results.sort(key=lambda x: x[0], reverse=True)
#     return [movie for _, movie in results[:5]]

def autoComplete(title:str):
    url = f'https://omdbapi.com/'
    params = {
        'apikey': OMDB_KEY,
        's': title,
        'type': 'movie'
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        return {'error': f'API error: {res.status_code}'}
    results = res.json()['Search']
    return sorted(results, key=lambda x: x['Year'], reverse=True)[0:5]

def getLink(imdbID: str, platform: str):
    url = 'https://film-show-ratings.p.rapidapi.com/item/'
    params = {
        'id': imdbID
    }
    headers = {
        "x-rapidapi-host": "film-show-ratings.p.rapidapi.com",
        "x-rapidapi-key": API_KEY
    }
    res = requests.get(url, params=params, headers=headers)
    if res.status_code != 200:
        return {"error": f'API error: {res.status_code}'}
    result = res.json()['result']['ids']
    print(result)
    if platform not in result:
        return {'error': f"Platform not existed!"}
    return result[platform]  

def get_imdb_reviews(id:str):

    url = 'https://imdb8.p.rapidapi.com/title/v2/get-user-reviews-summary'
    params = {
        'tconst':id
    }
    headers = {
        'x-rapidapi-host': 'imdb8.p.rapidapi.com',
        'x-rapidapi-key': API_KEY
    }
    res = requests.get(url, params=params, headers=headers)
    if res.status_code != 200:
        return {'error': f'API error: {res.status_code}'}
    review_list = res.json()['data']['title']['featuredReviews']['edges']

    if not review_list:
        return {'error': 'No reviews found'}
    
    reviews = []
    comments = []
    try:
        seen_ids = set()
        for review in review_list:
            if review['node']['id'] not in seen_ids:
                seen_ids.add(review['node']['id'])
                comments.append(review['node']['text']['originalText']['plainText'])
                reviews.append({
                    # 'Title': title,
                    'Platform': 'IMDb',
                    'Date': review['node']['submissionDate'],
                    'Type': review['node']['__typename'],
                })
        # sentiments = getBertSentiment(comments)
        translated_comments = translate_reviews(comments)
        sentiments = getBertSentiment(translated_comments)
        for r, comment, sentiment in zip(reviews, translated_comments, sentiments):
            r['Sentiment'] = sentiment
            r['Comment'] = comment
    except:
        return {'error': 'No reviews found'}
    
    return reviews


def get_rttm_reviews(id:str, mode:str='user', limit:int=10, offset:int=0):
    url = f'https://www.rottentomatoes.com/m/{id}/reviews'
    if mode=='user':
        url = url + "?type=user"

    headers = {'User-Agent':'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    reviews = []
    comments = []
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
                comments.append(review)
                reviews.append({
                    # 'Title': title,
                    'Platform': 'Rotten Tomatoes',
                    'Date': date,
                    'Type': 'Critic' if mode =='critic' else 'Review',
                })
        # sentiments = getBertSentiment(comments)
        translated_comments = translate_reviews(comments)
        sentiments = getBertSentiment(translated_comments)
        for r, comment, sentiment in zip(reviews, translated_comments, sentiments):
            r['Sentiment'] = sentiment
            r['Comment'] = comment
        
    except IndexError:
        return {'error': 'Out of range'}
    return reviews


def get_metacritic_reviews(id:str, limit:int=10, offset:int=0):
    url = f'https://backend.metacritic.com/reviews/metacritic/user/movies/{id}/web'
    
    params = {
        'apiKey': METACRITIC_KEY,
        'offset': offset,
        'limit': limit,
        'fiterBySentiment': 'all',
        'sort': 'date',
        'componentName': 'user-reviews',
        'componentDisplay': 'user+Reviews',
        'componentType': 'ReviewList',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    res = requests.get(url, params=params, headers=headers)
    if res.status_code != 200:
        return {'error': f'Failed to get response: {res.status_code}'}
    data = res.json()['data']['items']
    if len(data) == 0:
        return {'error': 'No reviews found'}
    reviews = []
    comments = []
    try:
        for review in data[offset:offset+limit]:
            comments.append(review['quote'])
            reviews.append({
                'Title': review['reviewedProduct']['title'],
                'Platform': 'Metacritic',
                'Date': review['date'],
                'Type': 'Review',
            })
        # sentiments = getBertSentiment(comments)
        translated_comments = translate_reviews(comments)
        sentiments = getBertSentiment(translated_comments)
        for r, comment, sentiment in zip(reviews, translated_comments, sentiments):
            r['Sentiment'] = sentiment
            r['Comment'] = comment
    except IndexError:
        return {'error': 'No reviews found'}
    return reviews