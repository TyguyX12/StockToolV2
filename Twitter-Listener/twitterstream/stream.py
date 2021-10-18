from config import config
from twitterstream.mysql_connector import *
import tweepy
import json


CONNECTION = create_mysql_connection()

def start_live_listener():
    '''
    Starts Twitter Listener
    '''
    #instantiates listener processor
    listener = TwitterStreamListener()

    #connects to twitter api
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN_KEY, config.ACCESS_TOKEN_SECRET)

    #begins stream
    stream = tweepy.streaming.Stream(auth, listener)
    stream.filter(track=['#stocks', '#wallstreet', '#stockmarket', '#stonk', '#crypto'])


class TwitterStreamListener(tweepy.streaming.StreamListener):

    ''' Handles LIVE data received from the stream. '''

    def on_status(self, status):
        try:
            tweet_dict = {}
            #tweet_dict['id'] = status.id
            tweet_dict['username'] = status.user.name
            tweet_dict['location'] = status.user.location
            tweet_dict['text'] = status.text
            tweet_dict['followers'] = status.user.followers_count
            tweet_dict['total_tweets'] = status.user.statuses_count
            tweet_dict['following'] = status.user.following
            tweet_dict['friends_count'] = status.user.friends_count
            tweet_dict['created'] = status.created_at

            insert_tweets_db(CONNECTION, tweet_dict)

            config.LOGGER.info(tweet_dict)
            return True
        except Exception as e:
            config.LOGGER.error(e)

    def on_error(self, status_code):
        config.LOGGER.error('Got an error with status code: ' + str(status_code))
        return True # To continue listening

    def on_timeout(self):
        config.LOGGER.info('Timeout...')
        return True # To continue listening
