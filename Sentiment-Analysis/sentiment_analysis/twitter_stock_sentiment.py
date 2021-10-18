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

    
    def process_tweets_from_db(self, sentiment_type):
        tweets = gather_tweets_from_db(CONNECTION, sentiment_type)
        tickers, comments = {}, {}
        fetch = tweets.fetchmany
        tweet_ids = []
        while True:
            rows = fetch(2000)
            if not rows: break
            
            for row in rows:
                #print(row)
                try:
                    #print(row)
                    words = row['TweetText'].split(" ")

                    for word in words:
                        word = word.replace("\\n", "")
                        word = word.replace("$", "")

                        if word.isupper() and word in us and word not in blacklist:

                            if word.upper() not in tickers:
                                tickers[word.upper()] = 1
                                comments[word.upper()] = [row['TweetText']]
                            else:
                                tickers[word.upper()] += 1
                                comments[word.upper()].append(row['TweetText'])
                
                except Exception as e:
                    print(e)
                
                tweet_ids.append(row['idTwitterData'])
        
        tweets.close()
        update_processed_col(CONNECTION, tweet_ids, sentiment_type)
            

        symbols = dict(sorted(tickers.items(), key=lambda item: item[1], reverse=True))
        self.top_picks = list(symbols.keys())[0:self.__top_picks]

        config.LOGGER.info("Finished processing tweets from the DB.")
        return (symbols, comments)


    def process_tweets_from_excel(self):
        file_tags = ['stocks']
        data_dir = os.getcwd() + os.path.sep + 'data' + os.path.sep

        tickers, comments = {}, {}

        for tag in file_tags:
            tweet_dict = pd.read_excel(data_dir + '{}_hashtag.xlsx'.format(tag)).to_dict()
            
            for tweet in tweet_dict['text']:
                #logic here for sentiment analysiss
                print(tweet_dict['text'][tweet])
                words = str(tweet_dict['text'][tweet]).split(" ")

                for word in words:
                    word = word.replace("\\n", "")
                    word = word.replace("$", "")

                    if word.isupper() and word in us and word not in blacklist:
                        
                        if word.upper() not in tickers:
                            tickers[word.upper()] = 1
                            comments[word.upper()] = [tweet_dict['text'][tweet]]
                        else:
                            tickers[word.upper()] += 1
                            comments[word.upper()].append(tweet_dict['text'][tweet])

        symbols = dict(sorted(tickers.items(), key=lambda item: item[1], reverse=True))
        self.top_picks = list(symbols.keys())[0:self.__top_picks]
        return symbols, comments
    

    def analyze_sentiment(self, symbols, comments):

        print(f"\n{self.__top_picks} most mentioned picks: ")
        self.times = []
        self.top = []
        for i in self.top_picks:
            print(f"{i}: {symbols[i]}")
            self.times.append(symbols[i])
            self.top.append(f"{i}: {symbols[i]}")
   
        print("Beginning sentiment analysis...")    

        scores, s = {}, {}


        picks_sentiment = list(symbols.keys())[0:self.__top_picks]
        for symbol in picks_sentiment:
            stock_comments = comments[symbol]
            for comment in stock_comments:
                score = self.vader.polarity_scores(comment)
                if symbol in s:
                    s[symbol][comment] = score
                else:
                    s[symbol] = {comment:score}
                if symbol in scores:
                    for key, _ in score.items():
                        scores[symbol][key] += score[key]
                else:
                    scores[symbol] = score

            for key in score:
                scores[symbol][key] = scores[symbol][key] / symbols[symbol]
                scores[symbol][key] = "{pol:.3f}".format(pol=scores[symbol][key])

        return scores

    
    def display_results(self, scores):
        df = pd.DataFrame(scores)
        df.index = ['Bearish', 'Neutral', 'Bullish', 'Total/Compound']
        df = df.T

        squarify.plot(sizes=self.times, label=self.top, alpha=.7)
        plt.axis('off')
        plt.title(f"{self.__top_picks} most mentioned picks")
        plt.show()  

        #Sentiment Analysis
        df = df.astype(float)
        colors = ['red', 'springgreen', 'forestgreen', 'coral']
        df.plot(kind = 'bar', color=colors, title=f"Sentiment analysis of top {self.__top_picks} picks:")
        plt.show()


    def run_from_excel(self):
        symbols, comments = self.process_tweets_from_excel()
        scores = self.analyze_sentiment(symbols, comments)
        self.display_results(scores)

    
    def run_from_db(self, sentiment_type):
        symbols, comments = self.process_tweets_from_db(sentiment_type)
        #print(self.process_tweets_from_db())
        scores = self.analyze_sentiment(symbols, comments)
        insert_sentiment_scores(CONNECTION, scores, 'twitter', sentiment_type)
        #self.display_results(scores)




###UNIT TESTS
if __name__ == '__main__':
    twitter - TwitterSentiment()
    twitter.run_from_db
