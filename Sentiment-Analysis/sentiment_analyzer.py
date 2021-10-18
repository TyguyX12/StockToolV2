from sentiment_analysis.twitter_stock_sentiment import TwitterSentiment
from sentiment_analysis.reddit_stock_sentiment import RedditSentiment
import time
import datetime
import _thread


def weekly_sentiment(twitter):
    while 1:
        twitter.run_from_db('weekly')
        time.sleep(604800)



if __name__ == '__main__':
    last_day = ''
    tw = TwitterSentiment()
    rd = RedditSentiment()
    while 1:
        day = datetime.datetime.now().day
        if day != last_day:
            last_day = day
            #function call
            tw.run_from_db('daily')
        

        tw.run_from_db('hourly')
        rd.run_reddit_sentiment()
        _thread.start_new_thread(weekly_sentiment, (tw, ))
        time.sleep(3600)