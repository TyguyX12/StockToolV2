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
            
#       This code is likely going to be heavily modified (or replaced). The current plan includes collecting historical
#   tweets and reddit posts using their respective APIs. The Reddit data is collected first, and among the most mentioned
#   reddit stocks, Tweets are collected. This will be run for each day, backwards, for as long as we are able to collect data.
#   This sentiment_analyzer will be a script in which a day is given as a parameter, and sentiment analysis is done for the 
#   Twitter and Reddit posts for that day. This score is saved in the sentimentdata table and includes:

#       `id`                (PRIMARY KEY)
#       `source`            (TWITTER OR REDDIT)
#       `asset`             (STOCK NAME)
#       `score_neg`         (AVERAGE NEGATIVE SCORES FOR DAY)
#       `score_neu`         (AVERAGE NEUTRAL SCORES FOR DAY)
#       `score_pos`         (AVERAGE POSITIVE SCORES FOR DAY)
#       `num_neg`           (NUMBER OF MOSTLY NEGATIVE TWEETS FOR DAY)
#       `num_neu`           (NUMBER OF MOSTLY NEUTRAL TWEETS FOR DAY)
#       `num_pos`           (NUMBER OF MOSTLY POSITIVE TWEETS FOR DAY)
#       `date`              (DATE OF SENTIMENT SCORES)
            
        
