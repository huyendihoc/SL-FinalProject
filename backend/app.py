from flask import Flask, request, jsonify, send_from_directory
import json
from flask_cors import CORS, cross_origin
import csv
import api

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

@app.route('/')
def index():
    return {'test': 'hello'}

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