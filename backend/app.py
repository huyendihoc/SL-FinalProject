from flask import Flask, request, jsonify, send_from_directory
import json
from flask_cors import CORS, cross_origin
from flask_caching import Cache
import csv
import api

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/')
def index():
    return {'test': 'hello'}

@app.route('/autocomplete/<string:movie>', methods=['GET'])
@cross_origin()
def getAutoComplete(movie):
    cache_key = f'autocomplete_{movie.lower()}'
    cache_result = cache.get(cache_key)
    if cache_result:
        return cache_result
    
    results = api.autoComplete(movie)
    cache.set(cache_key, results, timeout=60*15)
    return results

@app.route('/imdb/<string:imdbID>', methods=['GET'])
@cross_origin()
def getImdb(imdbID):
    reviews = api.get_imdb_reviews(imdbID)
    return api.translate_and_sentiment(reviews)

@app.route('/rotten-tomatoes/<string:imdbID>', methods=['GET'])
@cross_origin()
def getRottenTomatoes(imdbID):
    data = api.getLink(imdbID=imdbID)
    platform = 'Rotten Tomatoes'
    if platform not in data:
        return {'error': f"{platform} not existed!"}
    
    id = list(filter(None, data[platform].split('/')))[-1]
    reviews = api.get_metacritic_reviews(id)
    return api.translate_and_sentiment(reviews)

@app.route('/metacritic/<string:imdbID>', methods=['GET'])
@cross_origin()
def getMetacritic(imdbID):
    data = api.getLink(imdbID=imdbID)
    platform = 'Metacritic'
    if platform not in data:
        return {'error': f"This film does not exist in {platform}!"}
    
    id = list(filter(None, data[platform].split('/')))[-1]
    reviews = api.get_metacritic_reviews(id)
    return api.translate_and_sentiment(reviews)

@app.route('/all/<string:imdbID>', methods=['GET'])
@cross_origin()
def getAllPlatforms(imdbID):
    data = api.getLink(imdbID=imdbID)

    if 'Metacritic' not in data:
        return {"error": f"This film does not exist in Metacritic"}
    
    if 'Rotten Tomatoes' not in data:
        return {'error': f'This film does not exist in Rotten Tomatoes'}
    
    rttm_id = list(filter(None, data['Rotten Tomatoes'].split('/')))[-1]
    metacritic_id = list(filter(None, data['Metacritic'].split('/')))[-1]

    imdb_reviews = api.get_imdb_reviews(imdbID, 100)
    rttm_reviews = api.get_rttm_reviews(rttm_id, 100)
    metacritic_reviews = api.get_metacritic_reviews(metacritic_id, 100)
    reviews = imdb_reviews + rttm_reviews + metacritic_reviews
    return api.translate_and_sentiment(reviews)

if __name__ == '__main__':
    app.run(debug=True)