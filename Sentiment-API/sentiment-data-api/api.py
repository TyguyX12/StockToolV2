import os
import json
import config
import logging
from flask import Flask, jsonify, request
from mysql_connector import *


logging.getLogger('werkzeug').setLevel(logging.DEBUG)
#MYSQL_CONNECTION = create_mysql_connection()
app = Flask(__name__)

#app.config.from_object(os.environ['APP_SETTINGS'])


@app.route('/')
def home():
    return '<p> App is running! </p>'


@app.route('/status')
def status():
    return jsonify({'status':'up'})


@app.route('/get_sentiment_data_ticker', methods=['GET'])
def get_sentiment_data_ticker():

    try:
        request_data = json.loads(request.data)
    except Exception as e:
        return "Missing body of request", 400
    
    if request_data['ticker'] is None or request_data['ticker'] == '':
        return 'Missing ticker in request', 400
    if request_data['type'] is None or request_data['type'] == '':
        return 'Missing type of sentiment in request', 400
    if 'source' not in request_data:
        source = 'twitter'
    else:
        source = request_data['source']
    
    sentiment_data = get_sentiment_data_ticker_db(request_data['ticker'], request_data['type'], source)

    if isinstance(sentiment_data, str):
        return sentiment_data, 200

    return jsonify(sentiment_data), 200
    

@app.route('/get_sentiment_data_reddit', methods=['GET'])
def get_sentiment_data_reddit():
    try:

        try:
            request_data = json.loads(request.data)
        except Exception as e:
            return "Missing body of request", 400

        if request_data['type'] not in {'weekly', 'daily', 'hourly'}:
            return "Invalid sentiment type", 400

        
        sentiment_data = get_sentiment_data_db_reddit(request_data['type'])
        return jsonify(sentiment_data), 200
    except Exception as e:
        config.LOGGER.error(e)
        return str(e), 500




@app.route('/get_sentiment_data_twitter', methods=['GET'])
def get_sentiment_data_twitter():
    try:
        
        try:
            request_data = json.loads(request.data)
        except Exception as e:
            return "Missing body of request", 400

        if request_data['type'] not in {'weekly', 'daily', 'hourly'}:
            return "Invalid sentiment type", 400
        
        sentiment_data = get_sentiment_data_db_twitter(request_data['type'])
        return jsonify(sentiment_data), 200
    except Exception as e:
        config.LOGGER.error(e)
        return str(e), 500


if __name__ == '__main__':
    app.run()