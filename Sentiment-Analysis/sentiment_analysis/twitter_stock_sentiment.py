import time
import os
import pandas as pd
from config.config import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from mysqlcon.mysql_connector import *


CONNECTION = create_mysql_connection()


class TwitterSentiment(object):
    
    def __init__(self):
        self.__top_picks = 30
        self.__follower_count_limit = 1000
        try:
            self.vader = SentimentIntensityAnalyzer()
        except Exception as e:
            print(e)
            print("Vader Lexicon missing. Downloading required file...")
            import nltk
            nltk.download('vader_lexicon')
            self.vader = SentimentIntensityAnalyzer()
        self.vader.lexicon.update(new_words)

    #   RUN_FROM_DB:
    #   Calls method to pull tweets from the db for a given date
    def run_from_db(self, date):                                                    #   REMOVED type, ADDED date
        SortedCounts, TweetTexts = self.process_tweets_from_db(date)                #   ADDED date. SortedCounts = list of stocks sorted by highest count
                                                                                    #   SortedCounts is a dict with a stock name as it's keys and the no. of references as a value
                                                                                    #   TweetTexts is a dict with a stock name as it's keys and TweetTexts as values
        #print(self.process_tweets_from_db())
        scores = self.analyze_sentiment(SortedCounts, TweetTexts)                   #   Gather sentiment scores for all tweets & aggregate as scores
        
        insert_sentiment_scores(CONNECTION, scores, 'twitter', date)                #   REMOVED type, ADDED date. 
        #self.display_results(scores)

    
    #   Calls tweets from the db for a given date
    def process_tweets_from_db(self, date):                                         #   ADDED date, Tweets will be pulled for a given date for sentiment analysis
        tweets = gather_tweets_from_db(CONNECTION, date)                            #   ADDED date
        TweetCount, TweetTexts = {}, {}                                             #   RENAMED tickers & comments TO TweetCount & TweetTexts FOR CLARITY.
                                                                                    #   TweetCount is a dict with a stock name as it's keys and the no. of references as a value
                                                                                    #   TweetTexts is a dict with a stock name as it's keys and TweetTexts as values. Returned by this function
        fetch = tweets.fetchmany
        tweet_ids = []
        while True:
            tweetsFromDB = fetch(2000)                                              #   RENAMED rows to tweetsFromDB
            if not tweetsFromDB: break
            
            for tweet in tweetsFromDB:                                              #   tweetsFromDB = 2000 Tweets fetched from DB
                #print(tweet)
                try:
                    #print(tweet)
                    words = tweet['TweetText'].split(" ")                           #   Words = words in the Tweet

                    for word in words:
                        word = word.replace("\\n", "")
                        word = word.replace("$", "")

                        #   Determines whether or not the Tweet is discussing a given stock 
                        #   This will likely be changed due to the new Tweet collection method including which stock is discussed
                        if word.isupper() and word in us and word not in blacklist:     

                            if word.upper() not in TweetCount:                      #   If a stock has not yet had a Tweet about it, create an index in TweetCount and TweetTexts 
                                TweetCount[word.upper()] = 1                    
                                TweetTexts[word.upper()] = [row['TweetText']]       
                            else:                                                   #   Otherwise, TweetCount is incremented, and TweetTexts gets a new row with another Tweet's text
                                TweetCount[word.upper()] += 1
                                TweetTexts[word.upper()].append(row['TweetText'])
                
                except Exception as e:
                    print(e)
                
                tweet_ids.append(row['idTwitterData'])                              #   TweetIds are stored so that they may be marked as processed
        
        tweets.close()
        update_processed_col(CONNECTION, tweet_ids)                                 #   REMOVED TYPE. Marks Tweets for deletion after they are processed
            
            
        SortedCounts = dict(sorted(TweetCount.items(), key=lambda item: item[1], reverse=True))  #   RENAMED SYMBOLS TO SortedCounts. Sorts TweetCounts with most Tweets First, returned by this function
        self.top_picks = list(SortedCounts.keys())[0:self.__top_picks]                           #   Contains top_picks no. of Stocks with the most Tweets about them. May be reevaluated to include all Tweets about top Reddit stocks.

        config.LOGGER.info("Finished processing tweets from the DB.")
        return (SortedCounts, TweetTexts)                                           #   Returns the sorted list of most mentioned stocks, as well as the Tweets about them, to be used in the following sentiment analysis
    

    
    #   This function takes in the list of stocks sorted by TweetCount, as well as the actual Tweet texts themselves
    def analyze_sentiment(self, SortedCounts, TweetTexts):
        print(f"\n{self.__top_picks} most mentioned picks: ")
#        self.times = []                                                            #   COMMENTED OUT TIMES, ONLY USED IN GRAPHING. Contains list of times that each stock is mentioned (detached from name). 
#        self.top = []                                                              #   COMMENTED OUT TOP, ONLY USED IN GRAPHING. Contains String-formatted list "Stock: Count" with all top picks
        for stock in self.top_picks:                                                #   Runs through the top_picks (30 most mentioned stocks) and does the following for each stock
            print(f"{stock}: {SortedCounts[stock]}")
#            self.times.append(SortedCounts[stock])                                 #   COMMMENTED OUT TIMES CODE, ONLY USED IN GRAPHING
#            self.top.append(f"{stock}: {SortedCounts[stock]}")                     #   COMMMENTED OUT TOP CODE, ONLY USED IN GRAPHING
   
        print("Beginning sentiment analysis...")    
        
        TweetScores, CumulativeScores = {}, {}                                      #   RENAMED s TO TweetScores, scores TO CumulativeScores 
                                                                                    #   TweetScores contains all neg, neu, and pos sentiment for all of a stock's tweets.
                                                                                    #   CumulativeScores contains an average of all neg, neu, and pos sentiment for a stock.  
                                                                                    
        
        picks_sentiment = list(SortedCounts.keys())[0:self.__top_picks]             #   SEEMS REDUNDANT, SAME AS self.top_picks?
        for stock in picks_sentiment:                                               #   RENAMED SYMBOL TO STOCK
            tweetsForStock = TweetTexts[stock]                                      #   RENAMED stock_comments TO tweetsForStock FOR CLARITY
            for tweet in tweetsForStock:                                            #   RENAMED comment TO tweet FOR CLARITY
                tweetScore = self.vader.polarity_scores(tweet)                      #   RENAMED score to tweetScore FOR CLARITY. tweetScore = neg, neu, pos, and compound scores for a given tweet
                
                if stock in TweetScores:                                            #   Adds score to TweetScores at index tweet if a Tweet has been processed for it
                    TweetScores[stock][tweet] = tweetscore                                       
                else:                                                               #   Initializes TweetScores if a Tweet has not yet been processed for it.
                    TweetScores[stock] = {tweet:tweetscore}
                
                if stock in CumulativeScores:                                       #   Adds score to CumulativeScores at if a Tweet has been processed for it
                    for sentimentType, _ in tweetScore.items():                     #   RENAMED key TO sentimentType (neg, neu, pos) FOR CLARITY.
                        CumulativeScores[stock][sentimentType] += tweetScore[sentimentType]
                else:                                                               #   Initializes CumulativeScores if a Tweet has not yet been processed for it.
                    CumulativeScores[stock] = tweetScore

            for sentimentType in tweetScore:                                        #   Runs through all scores for a stock 
                CumulativeScores[stock][sentimentType] = CumulativeScores[stock][sentimentType] / SortedCounts[stock]           #   The cumulative score for each type of sentiment (neg, neu, pos) is an average of all scores of that type. 
                CumulativeScores[stock][sentimentType] = "{pol:.3f}".format(pol=CumulativeScores[stock][sentimentType])         #   Formats CumulativeScores to 3 decimals

        return CumulativeScores

    
#    def display_results(self, scores):
#        df = pd.DataFrame(scores)
#        df.index = ['Bearish', 'Neutral', 'Bullish', 'Total/Compound']
#        df = df.T
#
#        squarify.plot(sizes=self.times, label=self.top, alpha=.7)
#        plt.axis('off')
#        plt.title(f"{self.__top_picks} most mentioned picks")
#        plt.show()  
#
#        #Sentiment Analysis
#        df = df.astype(float)
#        colors = ['red', 'springgreen', 'forestgreen', 'coral']
#        df.plot(kind = 'bar', color=colors, title=f"Sentiment analysis of top {self.__top_picks} picks:")
#        plt.show()   


#    def process_tweets_from_excel(self):
#        file_tags = ['stocks']
#        data_dir = os.getcwd() + os.path.sep + 'data' + os.path.sep
#
#        TweetCount, TweetTexts = {}, {}
#
#        for tag in file_tags:
#            tweet_dict = pd.read_excel(data_dir + '{}_hashtag.xlsx'.format(tag)).to_dict()
#            
#            for tweet in tweet_dict['text']:
#                #logic here for sentiment analysiss
#                print(tweet_dict['text'][tweet])
#                words = str(tweet_dict['text'][tweet]).split(" ")
#
#                for word in words:
#                    word = word.replace("\\n", "")
#                    word = word.replace("$", "")
#
#                    if word.isupper() and word in us and word not in blacklist:
#                        
#                        if word.upper() not in TweetCount:
#                            TweetCount[word.upper()] = 1
#                            TweetTexts[word.upper()] = [tweet_dict['text'][tweet]]
#                        else:
#                            TweetCount[word.upper()] += 1
#                            TweetTexts[word.upper()].append(tweet_dict['text'][tweet])
#
#        symbols = dict(sorted(TweetCount.items(), key=lambda item: item[1], reverse=True))
#        self.top_picks = list(symbols.keys())[0:self.__top_picks]
#        return symbols, TweetTexts        

#    def run_from_excel(self):
#        symbols, TweetTexts = self.process_tweets_from_excel()
#        scores = self.analyze_sentiment(symbols, TweetTexts)
#        self.display_results(scores)

###UNIT TESTS
if __name__ == '__main__':
    twitter - TwitterSentiment()
    twitter.run_from_db
