from config import *
import tweepy
import json
import datetime
import csv

StocksToSearch = []

def start_live_listener():
    '''
    Starts Twitter Listener
    '''
    
    print("Starting Listener")
    
    stream = TwitterStreamListener(
            TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
            )

    StocksToSearch = readSuperCSV()

    stream.filter(track=StocksToSearch)

def readSuperCSV():
    #   Creates the  StocksToSearch dictionary with the schema for how Tweets will be collected using the superCSV and the dailyCSV
    #   First, the superCSV is used as a template, because it will always contain more stocks.
    #   Then, the dailyCSV is placed on top of the superCSV, the higher of the two TweetWeights will be used. 
    #   If a stock is the the superCSV and has a requirement, the  StocksToSearch dictionary will reflect this
    #   If a stock is in the dailyCSV and not the superCSV, it must be calculated whether or not the stock will need an additional requirement
        
        print("Reading SuperCSV")
        global StocksToSearch

        superPath = ('/Users/tymar/OneDrive/Documents/Capstone/Twitter/superCSV.csv')

        with open(superPath, newline='\n') as superFile:
            superReader = csv.reader(superFile, delimiter=',', quotechar='|')
            for line in superReader:
                if str(line[0]) ==  'stock':
                    continue
                newStock = "$" + str(line[0])
                StocksToSearch.append(newStock)
        
        print("Finished Reading SuperCSV")
        print("Stocks to search: " + str(StocksToSearch))
        return StocksToSearch

class TwitterStreamListener(tweepy.Stream):
    ''' Handles LIVE data received from the stream. '''
    #SortedCounts, TweetTexts, TweetCounts = {}, {}, {}
    global StocksToSearch
    print("Initializing Stream")    
    def on_status(self, status): 
        try:
            tweetsCSVPath = open(('/Users/tymar/OneDrive/Documents/Capstone/Twitter/Tweets/Tweets-' + str(datetime.date.today()) + '.csv'), 'a')
            tweetsCSVWriter = csv.writer(tweetsCSVPath)
            stock = ''
            tweetText = str(status.text.encode("utf-8"))
            tweetText = tweetText.replace("\\", " ")
            tweetText = tweetText.replace("b'",  " ")
            tweetText = tweetText.replace('b"',  " ")
            tweetText = tweetText.replace(",",  " ")

            for word in tweetText.split(' '):
                if len(word) > 0 and len(word) < 7 and word[0] == '$' and word.upper() in StocksToSearch:
                    stock = word[1:].upper()
                    print(stock + ": " + tweetText)
                    tweetsCSVWriter.writerow([stock, tweetText])    
            
            tweetsCSVPath.close()

            LOGGER.info(tweetText)
            return True
        except Exception as e:
            LOGGER.error(e)

    def on_error(self, status_code):
        LOGGER.error('Got an error with status code: ' + str(status_code))
        return True # To continue listening

    def on_timeout(self):
        LOGGER.info('Timeout...')
        return True # To continue listening


start_live_listener()
