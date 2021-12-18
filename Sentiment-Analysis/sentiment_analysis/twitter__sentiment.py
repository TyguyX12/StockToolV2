from abc import ABC
import time
import os
import pandas as pd
from config import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from mysql_connector_sentiment_analysis import *
import tweepy
import csv
import datetime



#   CONNECTION = create_mysql_connection()


class TwitterSentiment(object):
    
    def __init__(self):

        LOGGER.info("Connected to Twitter")

        self.set_parameters()

        try:
            self.vader = SentimentIntensityAnalyzer()
        except Exception as e:
            print(e)
            print("Vader Lexicon missing. Downloading required file...")
            import nltk
            nltk.download('vader_lexicon')
            self.vader = SentimentIntensityAnalyzer()
        self.vader.lexicon.update(new_words)

    def set_parameters(self):
        # set the program parameters
        self.tweepyClient = tweepy.Client(
            bearer_token = TWITTER_BEARER_TOKEN,
            consumer_key = TWITTER_CONSUMER_KEY, 
            consumer_secret = TWITTER_CONSUMER_SECRET, 
            access_token= TWITTER_ACCESS_TOKEN, 
            access_token_secret = TWITTER_ACCESS_SECRET,
            wait_on_rate_limit = "true"                                             #   Ensures the Twitter API rate limit is not exceeded, prevents error
            )

        auth = tweepy.AppAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        #auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        
        self.tweepyAPI = tweepy.API(auth, wait_on_rate_limit = "true")
        self.tweepyLabel = "30DaySearch"

        self.__top_picks = 30
        self.__follower_count_limit = 1000
        self.superCSVThreshold = 5                                                   #   Determines how many Reddit posts a stock needs to be included on the superCSV
        self.stockNameSizeThreshold = 2                                              #   Stocks with names at least this small require an additional hashtag

    def run_for_date(self, date):                                                    
        
        #open csv of all tweets to run every day
        #open csv of posts for specific day
        #eliminate duplicates between csvs
        #collect tweets based on new schema
        #score tweets and store in csv

        #self.createSuperCSV(self.superCSVThreshold)                                #   Run when a superCSV should be created. superCSV is the CSV that determines which stocks will have Tweets read every day, due to repeated instances of Reddit posts
                                                                                    #   threshold determines how many instances will put a stock on the superCSV
        
        StocksToSearch = self.handleCSVs(date)                                      #   Creates the StocksToSearch Dictionary utilizing the daily/super CSVs. 
                                                                                    #   The StocksToSearch Dictionary CSV will determine whether or not Tweets should be read for each stock name for a given day.
                                                                                    #   The StocksToSearch Dictionary CSV will also indicate whether or not stocks will require an additional hashtag

        #self.collectTweetsForDate(StocksToSearch, date)
        SortedCounts, CumulativeScores = self.runSentimentAnalysisForDate(date)

        self.create_sentiment_csv(CumulativeScores, SortedCounts, date)

    
    def createSuperCSV(self, threshold):
    #   Creates the superCSV file that determines stocks that should be read every day, parameterized by threshold
    #   If a stock appears more than threshold amount of times over the course of all of the csv files, it is added to the superCSV
    #   The schema of the superCSV is as follows: [stockName,   requiresAdditionalHashtag   tweetWeight] 
    #   Where requiresAdditionalHashtag is a boolean indicating whether or not the stock requires a second stock-related hashtag (ex. a 1-2 character stock, or a common word)  
    #   and tweetWeight is the number of Tweets that are collected in one scrape of the Tweet Collector (NOT IMPLEMENTED)
    #   This algorithm may be imperfect, and may require additional dilligence on behalf of the user to make sure common words are not included ("Ex. HOPE")

        StockCounts, StockAdditionalHashtags = {}, {}                                              #   StockCounts keeps track of stock names and counts while iterating over all of the stocks
                                                                                                   #   StockAdditionalHashtags keeps track of stock names and whether or not they will need an additional hashtag.

        superCSVPath = open(('/users/tymar/downloads/Schoolwork/Machine Learning/Twitter/superCSV.csv'), 'w')
        superCSVWriter = csv.writer(superCSVPath)

        scorePath = '/users/tymar/downloads/Schoolwork/Machine Learning/RedditScores/'
        for fileName in os.listdir(scorePath):
            filePath = str(scorePath) + str(fileName)
            with open(filePath, newline='\n') as csvfile:
                csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')
                for line in csvReader:
                    #   Skips top line of each CSV
                    if str(line[0]) ==  'source':
                        continue
                    #   Handles adding instances of stocks to StockCounts
                    if line[2] in StockCounts:                                                      #   An instance has already been processed for this stock
                        StockCounts[line[2]] += int(line[7])
                    else: 
                        StockCounts[line[2]] = int(line[7])
                        if len(line[2]) <= self.stockNameSizeThreshold:                                 
                            StockAdditionalHashtags[line[2]] = "true"
                        else:
                            StockAdditionalHashtags[line[2]] = "false"
        
        #Messy Code, Orders stocks by StockCount and adds them to superCSV.csv
        superCSVWriter.writerow(["stock", "requiresAdditionalHashtag", "redditInstances", "tweetWeight"])
        for stock in reversed(sorted(StockCounts.items(), key=lambda item: item[1])):
            if stock[1] >= threshold:
                superCSVWriter.writerow([str(stock[0]), str(StockAdditionalHashtags[stock[0]]), str(StockCounts[stock[0]]), str(3)])

        superCSVPath.close()

    
    def handleCSVs(self, date):
    #   Creates the  StocksToSearch dictionary with the schema for how Tweets will be collected using the superCSV and the dailyCSV
    #   First, the superCSV is used as a template, because it will always contain more stocks.
    #   Then, the dailyCSV is placed on top of the superCSV, the higher of the two TweetWeights will be used. 
    #   If a stock is the the superCSV and has a requirement, the  StocksToSearch dictionary will reflect this
    #   If a stock is in the dailyCSV and not the superCSV, it must be calculated whether or not the stock will need an additional requirement
        
        StocksToSearch = {}

        dailyPath = ('/users/tymar/downloads/Schoolwork/Machine Learning/RedditScores/Reddit-' + str(date) + '.csv')
        superPath = ('/users/tymar/downloads/Schoolwork/Machine Learning/Twitter/superCSV.csv')

        with open(dailyPath, newline='\n') as dailyFile, open(superPath, newline='\n') as superFile:
            dailyReader = csv.reader(dailyFile, delimiter=',', quotechar='|')
            superReader = csv.reader(superFile, delimiter=',', quotechar='|')
            for line in superReader:
                if str(line[0]) ==  'stock':
                    continue
                StocksToSearch[line[0]] = line[1]
            for line in dailyReader:
                if str(line[0]) ==  'source':
                    continue
                
                if line[2] not in StocksToSearch:
                    StocksToSearch[line[2]] = "true"                               #   Stocks not in superCSV require an additional hashtag by default, since there is no way to manually change this status, and stocks may have names that are similar to common words

        return StocksToSearch
     

    def collectTweetsForDate(self, StocksToSearch, date):
        #   This function takes in a list of stocks to search, and whether or not an additional hashtag will be required for that stock.
        #   For backup purposes, each Tweet will be saved in a csv, that Twitter API calls are not wasted.
        SortedCounts, TweetTexts, TweetCounts = {}, {}, {}

        tweetsCSVPath = open(('/users/tymar/downloads/Schoolwork/Machine Learning/Twitter/Tweets/Tweets-' + str(date) + '.csv'), 'w')
        tweetsCSVWriter = csv.writer(tweetsCSVPath)

        startDate = datetime.datetime(date.year, date.month, date.day)
        endDate = (startDate + datetime.timedelta(days=1))        
        
        endDate = datetime.datetime.now()
        endDate = (endDate - datetime.timedelta(seconds=10))

        print("Collecting Tweets for date: " + str(date))
        for stock in StocksToSearch:
            counter = 1
            nextToken = ''
            print("Collecting Tweets for Stock: " + str(stock))
            if StocksToSearch[stock] == "true":
                tweepyQuery = "-is:retweet " + str(stock) + " (#stocks OR #wallstreet OR #stockmarket OR #stonk OR #crypto OR #NYSE OR #NASDAQ)"

            else:
                tweepyQuery = "-is:retweet " + str(stock)
            
            while counter <= 10 and nextToken != None:
                if counter == 1:
                    tweetResponse = self.tweepyClient.search_recent_tweets(tweepyQuery, start_time = startDate, end_time = endDate, max_results = 100)
                else:
                    tweetResponse = self.tweepyClient.search_recent_tweets(tweepyQuery, start_time = startDate, end_time = endDate, max_results = 100, next_token = nextToken)

  
                tweetData = tweetResponse.data
                tweetMeta = tweetResponse.meta
                
                if tweetData == None:
                    continue

                for tweet in tweetData:
                    tweetText = str(tweet.text.encode("utf-8"))
                    tweetsCSVWriter.writerow([stock, tweetText])

                try:
                   nextToken = tweetMeta["next_token"]
                except Exception as e: 
                   break

                
                counter = counter + 1

        tweetsCSVPath.close()


#    def process_tweets_from_db(self, date):                                         
#        tweets = gather_tweets_from_db(CONNECTION, date)                           
#        TweetCount, TweetTexts = {}, {}                                            
#                                                                                    #   TweetCount is a dict with a stock name as it's keys and the no. of references as a value
#                                                                                    #   TweetTexts is a dict with a stock name as it's keys and TweetTexts as values. Returned by this function
#        fetch = tweets.fetchmany
#        tweet_ids = []
#        while True:
#            tweetsFromDB = fetch(2000)                                             
#            if not tweetsFromDB: break
#            
#            for tweet in tweetsFromDB:                                              #   tweetsFromDB = 2000 Tweets fetched from DB
#                #print(tweet)
#                try:
#                    #print(tweet)
#                    words = tweet['TweetText'].split(" ")                           #   Words = words in the Tweet
#
#                    for word in words:
#                        word = word.replace("\\n", "")
#                        word = word.replace("$", "")
#
#                        #   Determines whether or not the Tweet is discussing a given stock 
#                        #   This will likely be changed due to the new Tweet collection method including which stock is discussed
#                        if word.isupper() and word in us and word not in blacklist:     
#
#                            if word.upper() not in TweetCount:                      #   If a stock has not yet had a Tweet about it, create an index in TweetCount and TweetTexts 
#                                TweetCount[word.upper()] = 1                    
#                                TweetTexts[word.upper()] = [words['TweetText']]       
#                            else:                                                   #   Otherwise, TweetCount is incremented, and TweetTexts gets a new row with another Tweet's text
#                                TweetCount[word.upper()] += 1
#                                TweetTexts[word.upper()].append(words['TweetText'])
#                
#                except Exception as e:
#                    print(e)
#                
#                tweet_ids.append(row['idTwitterData'])                              #   TweetIds are stored so that they may be marked as processed
#        
#        tweets.close()
#        update_processed_col(CONNECTION, tweet_ids)                                
#            
#            
#        SortedCounts = dict(sorted(TweetCount.items(), key=lambda item: item[1], reverse=True))  #   Sorts TweetCounts with most Tweets First, returned by this function
#        self.top_picks = list(SortedCounts.keys())[0:self.__top_picks]                           #   Contains top_picks no. of Stocks with the most Tweets about them. May be reevaluated to include all Tweets about top Reddit stocks.
#
#        config.LOGGER.info("Finished processing tweets from the DB.")
#        return (SortedCounts, TweetTexts)                                           #   Returns the sorted list of most mentioned stocks, as well as the Tweets about them, to be used in the following sentiment analysis


    def runSentimentAnalysisForDate(self, date):
        TweetTexts, TweetCounts, TweetScores, CumulativeScores = {}, {}, {}, {}

        tweetPath = '/users/tymar/downloads/Schoolwork/Machine Learning/Twitter/Tweets/Tweets-' + str(date) + '.csv'

        # adding custom words from data.py 
        self.vader.lexicon.update(new_words)
                
        print("Starting Sentiment Analysis for date: " + str(date))
        with open(tweetPath, newline='\n') as tweetCSV:
            tweetReader = csv.reader(tweetCSV, delimiter=',', quotechar='|')
            for line in tweetReader:
                if line[0] in TweetCounts:                                                #   If a stock has had a tweet about it, TweetCount is incremented & TweetTexts gets new rows with text of the comment
                    TweetCounts[line[0]] += 1
                    TweetTexts[line[0]].append(line[1])
        
                else:                                                                       #   Otherwise, initialize TweetCount TweetTexts
                    TweetCounts[line[0]] = 1
                    TweetTexts[line[0]] = [line[1]]

        SortedCounts = dict(sorted(TweetCounts.items(), key=lambda item: item[1], reverse = True))
        SortedList = list(SortedCounts.keys())
        
        for stock in SortedList:                                                        
            stock_tweets = TweetTexts[stock]

            for tweet in stock_tweets:                                                         #   Runs through all comments for the most popular stocks                                          
                tweetScore = self.vader.polarity_scores(tweet)                                
               
                if stock in TweetScores:                                                      #   Adds score to CommentScores at index comment if a comment has been processed for it
                    TweetScores[stock][tweet] = tweetScore
                else:                                                                           #   Initializes CommentScores if a comment has not yet been processed for it.
                    TweetScores[stock] = {tweet:tweetScore}  
                    
                if stock in CumulativeScores:                                                   #   Adds score to CumulativeScores at if a comment has been processed for it
                    for sentimentType, score in tweetScore.items():                                                       
                        CumulativeScores[stock][sentimentType] = str(float(CumulativeScores[stock][sentimentType]) + score)
                else:                                                                           #   Initializes CumulativeScores if a comment has not yet been processed for it.
                    CumulativeScores[stock] = tweetScore
                    
                    # calculating avg.
            for sentimentType in CumulativeScores[stock]:                                                   #   Runs through all scores for a stock
                CumulativeScores[stock][sentimentType] = float(CumulativeScores[stock][sentimentType]) / float(SortedCounts[stock])          #   The cumulative score for each type of sentiment (neg, neu, pos) is an average of all scores of that type. 
                CumulativeScores[stock][sentimentType]  = "{pol:.3f}".format(pol=CumulativeScores[stock][sentimentType])        #   Formats CumulativeScores to 3 decimals
        
        return SortedCounts, CumulativeScores           


    def create_sentiment_csv(self, scores, counts, date):
    #   Creates the CSV file with the sentiment information for a given day
        csvName = "Twitter-" + str(date)
        pathToCSV = open(('/users/tymar/downloads/Schoolwork/Machine Learning/Twitter/Sentiment Scores/' + csvName + ".csv"), 'w')   
        csvWriter = csv.writer(pathToCSV)
        csvWriter.writerow(["source", "date", "stock", "neg", "neu", "pos", "comp", "instances"])
        for stock in scores:
            csvWriter.writerow(["twitter", str(date), stock, scores[stock]['neg'], scores[stock]['neu'], scores[stock]['pos'],  scores[stock]['compound'], counts[stock]])
        pathToCSV.close()
        LOGGER.info(f"\n{csvName} Created: ")
    
    
        

    ###UNIT TESTS
if __name__ == '__main__':
    twitter = TwitterSentiment()
    twitter.run_for_date(datetime.date(2021, 11, 30))

    
