from sentiment_analysis.twitter_stock_sentiment import TwitterSentiment
from sentiment_analysis.reddit_stock_sentiment import RedditSentiment
import time
import datetime
import _thread

if __name__ == '__main__':
    last_day = ''
    tw = TwitterSentiment()
    rd = RedditSentiment()
    while 1:
        day = datetime.datetime.now().day
        if day != last_day:
            last_day = day
            #function call
            tw.run_from_db()
        
