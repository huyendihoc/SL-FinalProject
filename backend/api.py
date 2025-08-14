import requests
import os
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from models import getBertSentiment
from translate_t5 import translate_reviews
from dotenv import load_dotenv
import re

load_dotenv()

API_KEY = os.getenv('API_KEY')
METACRITIC_KEY = os.getenv('METACRITIC_KEY')
OMDB_KEY = os.getenv('OMDB_KEY')

def translate_and_sentiment(reviews:list):
    comments = [review['Comment'] for review in reviews]
    translated_comments = translate_reviews(comments)
    sentiments = getBertSentiment(translated_comments)

    for r, comment, sentiment in zip(reviews, translated_comments, sentiments):
        r['Sentiment'] = sentiment
        r['Comment'] = comment
        
    return reviews

# Auto-complete search api
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

# Get multiple platform urls
def getLink(imdbID: str):
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
    return result

# Get IMDb reviews
def get_imdb_reviews(id:str, limit:int=10):
    url = "https://caching.graphql.imdb.com/"
    operation_name = "TitleReviewsRefine"
    page_size = 25  # fixed

    headers = {
        'accept': 'application/graphql+json, application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.imdb.com',
        'priority': 'u=1, i'
    }

    def get_variables(after_cursor):
        variables = {
            "const": id,
            "filter": {},
            "first": page_size,
            "sort": {
                "by": "HELPFULNESS_SCORE",
                "order": "DESC"
            }
        }
        if after_cursor:
            variables["after"] = after_cursor
        return variables

    def fetch_page(after_cursor):
        payload = {
            "query": """query TitleReviewsRefine($const: ID!, $filter: ReviewsFilter, $first: Int!, $sort: ReviewsSort, $after: ID) {
            title(id: $const) {
                reviews(filter: $filter, first: $first, sort: $sort, after: $after) {
                edges {
                    node {
                    id
                    author {
                        nickName
                    }
                    authorRating
                    helpfulness {
                        upVotes
                        downVotes
                    }
                    submissionDate
                    text {
                        originalText {
                        plainText
                        }
                    }
                    summary {
                        originalText
                    }
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
                }
            }
            }""",
            "operationName": operation_name,
            "variables": get_variables(after_cursor)
        }

        print(f"Requesting page with cursor: {after_cursor or '[first page]'}")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()


    after_cursor = None
    n = 0
    reviews = []
    while n < limit:
        data = fetch_page(after_cursor)
        review_info = data['data']['title']['reviews']
        page_info = review_info['pageInfo']
        review_list = review_info['edges']
        for review in review_list:
            reviews.append({
                'Platform': 'IMDb',
                'Date': review['node']['submissionDate'],
                'Type': 'Review',
                'Comment': review['node']['text']['originalText']['plainText']
            })
        n = n + len(review_list)
        if not page_info.get("hasNextPage"):
            print("No more pages. Exiting.")
            break

        after_cursor = page_info.get("endCursor")
        if not after_cursor:
            print("No endCursor found. Exiting.")
            break
    reviews = reviews[:limit]
    return reviews


# Get Rotten Tomatoes reviews
def get_rttm_reviews(id:str, limit:int=10):
    url = f'https://www.rottentomatoes.com/m/{id}/reviews?type=user'

    headers = {'User-Agent':'Mozilla/5.0'}
    html = requests.get(url, headers=headers).text
    pat = r'/cnapi/movie/([a-f0-9\-]{36})/reviews/user'
    m = re.search(pat, html)
    if not m:
        return {"error": "Api not found!"}
    emsId = m.group(1)

    res = requests.get(f'https://www.rottentomatoes.com/cnapi/movie/{emsId}/reviews/user')
    if res.status_code != 200:
        return {'error': f'Api error: {res.status_code}'}
    data = res.json()
    n = 0
    reviews = []
    while n < limit and data['pageInfo']['hasNextPage']:
        try:
            review_list = data['reviews']
            endCursor = data['pageInfo']['endCursor']
            for review in review_list:
                reviews.append({
                    'Platform': 'Rotten Tomatoes',
                    'Date': review['creationDate'],
                    'Type': 'Review',
                    'Comment': review['quote']
                })
            n = n + len(review_list)
            res = requests.get(f'https://www.rottentomatoes.com/cnapi/movie/{emsId}/reviews/user?after={endCursor}', headers=headers)
            data = res.json()
        except Exception as e:
            return {'error': f'Fetch reviews error: {e}'}
    reviews = reviews[:limit]
    return reviews



# Get Metacritic reviews
def get_metacritic_reviews(id:str, limit:int=10):
    url = f'https://backend.metacritic.com/reviews/metacritic/user/movies/{id}/web'
    
    params = {
        'apiKey': METACRITIC_KEY,
        'offset': 0,
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
    try:
        for review in data[:limit]:
            reviews.append({
                'Title': review['reviewedProduct']['title'],
                'Platform': 'Metacritic',
                'Date': review['date'],
                'Type': 'Review',
                'Comment': review['quote']
            })
    except IndexError:
        return {'error': 'No reviews found'}
    return reviews