"""
A sample Hello World server.
"""
import os
from flask import Flask, render_template
import schedule
import time
import datetime
import sys

from sentiment import twitter_sentiment as ts
from sentiment import reddit_sentiment as rs

tw = ts.TwitterSentiment()
rd = rs.RedditSentiment()

# pylint: disable=C0103
app = Flask(__name__)

# Functions setup
def sentiment_analysis():
	TODAY = datetime.date.today()
	tw.run_for_date(TODAY)               
	rd.run_for_date(TODAY)

# Every day at 12am or 00:00 time bedtime() is called.
schedule.every().day.at("23:30").do(sentiment_analysis)   

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return render_template('index.html',
        message=message,
        Service=service,
        Revision=revision)


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)
