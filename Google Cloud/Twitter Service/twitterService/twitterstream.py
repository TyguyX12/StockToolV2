
import tweepy
import datetime

import mysql.connector as mysql
import sys

HOST = "35.222.225.4" 
POSTDB = "Posts_DB"
USER = "root"
PASSWORD = "sentimentdata"

conn = mysql.connect(user=USER, password=PASSWORD, host=HOST, database=POSTDB)

StocksToSearch = ['$TSLA', '$GME', '$FB', '$NVDA', '$AMD', '$AAPL', '$TWTR', '$AMZN', '$NFLX', '$BABA', '$PLTR', '$TLRY', '$MSFT', '$MMS', '$GOOGL', '$GOOG', '$BBBY', '$ZM', '$ROKU', '$TDOC', '$BBY', '$TGT', '$UPST', '$RH', '$FDS', '$PYPL', '$NIO', '$SQ', '$WMT', '$SPCE', '$HMHC', '$DKNG', '$BYND', '$XOM', '$ROST', '$CRM', '$LULU', '$UBER', '$LYFT', '$JPM', '$DTE', '$COKE', '$ABNB', '$PANW', '$PTON', '$ETSY', '$SU', '$INTC', '$CSCO', '$OXY', '$KSS', '$JWN', '$BP', '$LMT', '$LUNA', '$MU', '$SBUX', '$HD', '$CCS', '$CRSR', '$BTC', '$MRNA', '$VIAC', '$CVNA', '$EBAY', '$RKT', '$SP', '$ANF', '$TSM', '$BAC', '$MCD', '$NYC', '$ULTA', '$EA', '$DOCU', '$GM', '$AAP', '$EGO', '$CLF', '$JD', '$MSM', '$CHWY', '$CVX', '$AMAT', '$NKLA', '$EL', '$COP', '$QCOM', '$SE', '$DKS', '$HYMC', '$QS', '$OFC', '$LE', '$FUBO', '$SAVA', '$MTCH', '$TWLO', '$CHGG', '$CMG', '$MSTR', '$GE', '$CVS', '$ABT', '$SIRI', '$INTU', '$ADP', '$CGC', '$IBKR', '$SAN', '$GS', '$ETH', '$CRSP', '$AZZ', '$FSD', '$AL', '$CRWD', '$III', '$TTWO', '$SNP', '$RL', '$NBA', '$VZ', '$AB', '$LI', '$SPR', '$BLK', '$AAL', '$MARA', '$DEN', '$CS', '$FSLY', '$UAL', '$SDC', '$ATVI', '$FSR', '$URBN', '$DG', '$WDAY', '$CB', '$AC', '$PING', '$NKE', '$NOK', '$ACB', '$SI', '$WFC', '$UNH', '$OKTA', '$MSCI', '$FN', '$SHO', '$BAK', '$EFF', '$MMM', '$LNG', '$DK', '$IBM', '$TTD', '$CROX', '$RTX', '$MVIS']


def start_live_listener():
    '''
    Starts Twitter Listener
    '''
    
    print("Starting Listener")

    
    #stream = TwitterStreamListener(
    #        TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
    #        TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
    #        )


    stream = TwitterStreamListener(
            'iVC7rCZAJ1RUk43daM7CNFrzi', '47jBQSmn9j3X8egZHjUom7fMxiWRdzHj90kKH7j1qJeEJGdR7v',
            '1462869214893514757-tzWkumIOifrPlu9UezKzB4RRE86S9o', 'cCCrechjol9YfrsoUgu6lLTCdxTK5oiU3ThiPjU4xWJu5'
            )

    stream.filter(track=StocksToSearch)


class TwitterStreamListener(tweepy.Stream):
    ''' Handles LIVE data received from the stream. '''
    print("Initializing Stream")    
    def on_status(self, status): 
        try:
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
                    insert_tweet_to_db(stock, tweetText)
            
            print(tweetText)
            return True
        except Exception as e:
            print(e)

    def on_error(self, status_code):
        print('Got an error with status code: ' + str(status_code))
        return True # To continue listening

    def on_timeout(self):
        print('Timeout...')
        return True # To continue listening

def insert_tweet_to_db(stock, tweetText):					       
        '''
        Inserts sentiment scores into sentimentdata table
        '''
        try:
            sql = """INSERT INTO twitterposts (id, stock, tweetText) VALUES (null, %s, %s)"""
            postData = (stock, tweetText)
            cursor = conn.cursor()
            cursor.execute(sql, postData)
            cursor.close()
            conn.commit()
        except Exception:
            createNewConnection()
            insert_tweet_to_db(stock, tweetText)

def createNewConnection():
    global conn
    conn = mysql.connect(user=USER, password=PASSWORD, host=HOST, database=POSTDB)



