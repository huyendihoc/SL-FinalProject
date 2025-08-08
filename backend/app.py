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

@app.route('/imdb/<string:movie>', methods=['GET'])
@cross_origin()
def getImdb(movie):
    return api.get_imdb_reviews(movie)

@app.route('/rotten-tomatoes/<string:movie>', methods=['GET'])
@cross_origin()
def getRottenTomatoes(movie):
    return api.get_rttm_reviews(movie)

@app.route('/metacritic/<string:movie>', methods=['GET'])
@cross_origin()
def getMetacritic(movie):
    return api.get_metacritic_reviews(movie)

if __name__ == '__main__':
    app.run(debug=True)