from nltk.sentiment.vader import SentimentIntensityAnalyzer

import datetime

import mysql.connector as mysql
import sys

HOST = "35.222.225.4" 
SENTIMENTDB = "Sentiment_DB"
POSTDB = "Posts_DB"
USER = "root"
PASSWORD = "sentimentdata"

sentimentConn = mysql.connect(user=USER, password=PASSWORD, host=HOST, database=SENTIMENTDB)
postConn = mysql.connect(user=USER, password=PASSWORD, host=HOST, database=POSTDB)

TODAY = datetime.date.today()

# adding wsb/reddit flavour to vader to improve sentiment analysis, score: 4.0 to -4.0
new_words = {
    'citron': -4.0,  
    'hidenburg': -4.0,        
    'moon': 4.0,
    'highs': 2.0,
    'mooning': 4.0,
    'long': 2.0,
    'short': -2.0,
    'call': 4.0,
    'calls': 4.0,    
    'put': -4.0,
    'puts': -4.0,    
    'break': 2.0,
    'tendie': 2.0,
     'tendies': 2.0,
     'town': 2.0,     
     'overvalued': -3.0,
     'undervalued': 3.0,
     'buy': 4.0,
     'buying': 4.0,
     'buys': 3.0,
     'sell': -4.0,
     'selling': -4.0,
     'sells': -3.5,
     'sold': -3.0,
     'gone': -1.0,
     'gtfo': -1.7,
     'paper': -1.7,
     'bullish': 3.7,
     'bearish': -3.7,
     'bagholder': -1.7,
     'stonk': 1.9,
     'money': 1.2,
     'print': 2.2,
     'rocket': 2.2,
     'bull': 2.9,
     'bear': -2.9,
     'pumping': -1.0,
     'sus': -3.0,
     'offering': -2.3,
     'rip': -4.0,
     'downgrade': -3.0,
     'upgrade': 3.0,     
     'maintain': 1.0,          
     'pump': 1.9,
     'hot': 1.5,
     'drop': -2.5,
     'rebound': 1.5,  
     'crack': 2.5,
     'earn': 3.5,
     'earns': 3.5,
     'earned': 3.0,
     'earning': 2.5,
     'earnings': 2.5,
     'lose': -3.5,
     'loses': -3.5,
     'lost': -3.0,
     'soar': 4.0,
     'soaring': 4.0,
     'soared': 3.5,
     'scandal': 2.5,
     'surging': 3.5,
     'surge': 3.5,
     'surged': 3.0,
     'up': 4.0,
     'upside': 3.0,
     'down': -4.0,
     'downside': -3.0,
     'best': 4.0,
     'worst': 4.0,
     'dump': -4.0,
     'dumping': -4.0,
     'dumped': -3.0,
     'dumps': -3.0,
     'plummet': -4.0,
     'plummeting': -4.0,
     'plummets': -3.5,
     'plummeted': -3.0,
     'crash': -4.0,
     'crashing': -4.0,
     'crashes': -3.5,
     'crashed': -3.0,
     'tank':-4.0,
     'tanks':-3.5,
     'tanking':-4.0,
     'tanked':-3.0,
     'green':4.0,
     'red':-4.0,
     }

StocksToSearch = ['TSLA', 'GME', 'FB', 'NVDA', 'AMD', 'AAPL', 'TWTR', 'AMZN', 'NFLX', 'BABA', 'PLTR', 'TLRY', 'MSFT', 'MMS', 'GOOGL', 'GOOG', 'BBBY', 'ZM', 'ROKU', 'TDOC', 'BBY', 'TGT', 'UPST', 'RH', 'FDS', 'PYPL', 'NIO', 'SQ', 'WMT', 'SPCE', 'HMHC', 'DKNG', 'BYND', 'XOM', 'ROST', 'CRM', 'LULU', 'UBER', 'LYFT', 'JPM', 'DTE', 'COKE', 'ABNB', 'PANW', 'PTON', 'ETSY', 'SU', 'INTC', 'CSCO', 'OXY', 'KSS', 'JWN', 'BP', 'LMT', 'LUNA', 'MU', 'SBUX', 'HD', 'CCS', 'CRSR', 'BTC', 'MRNA', 'VIAC', 'CVNA', 'EBAY', 'RKT', 'SP', 'ANF', 'TSM', 'BAC', 'MCD', 'NYC', 'ULTA', 'EA', 'DOCU', 'GM', 'AAP', 'EGO', 'CLF', 'JD', 'MSM', 'CHWY', 'CVX', 'AMAT', 'NKLA', 'EL', 'COP', 'QCOM', 'SE', 'DKS', 'HYMC', 'QS', 'OFC', 'LE', 'FUBO', 'SAVA', 'MTCH', 'TWLO', 'CHGG', 'CMG', 'MSTR', 'GE', 'CVS', 'ABT', 'SIRI', 'INTU', 'ADP', 'CGC', 'IBKR', 'SAN', 'GS', 'ETH', 'CRSP', 'AZZ', 'FSD', 'AL', 'CRWD', 'III', 'TTWO', 'SNP', 'RL', 'NBA', 'VZ', 'AB', 'LI', 'SPR', 'BLK', 'AAL', 'MARA', 'DEN', 'CS', 'FSLY', 'UAL', 'SDC', 'ATVI', 'FSR', 'URBN', 'DG', 'WDAY', 'CB', 'AC', 'PING', 'NKE', 'NOK', 'ACB', 'SI', 'WFC', 'UNH', 'OKTA', 'MSCI', 'FN', 'SHO', 'BAK', 'EFF', 'MMM', 'LNG', 'DK', 'IBM', 'TTD', 'CROX', 'RTX', 'MVIS']

class TwitterSentiment(object):
    
    def __init__(self):

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
        self.maxNeutralSentiment = 0.75                                            #   Excludes Tweets with a higher neutral score than this. Removes noise from data   
    
    def run_for_date(self, date):                                                      
        SortedCounts, CumulativeScores = self.run_sentiment_analysis_for_date(date)
        upload_sentiment_to_db(CumulativeScores, SortedCounts, date)
        clear_table_in_db()

    
    def run_sentiment_analysis_for_date(self, date):
        print("Running Twitter sentiment analysis for " + str(date))
        TweetTexts, TweetCounts, ProcessedTweetCounts, TweetScores, CumulativeScores = {}, {}, {}, {}, {}

        #tweetPath = '/Users/tymar/OneDrive/Documents/Capstone/Twitter/Tweets/Tweets-' + str(date) + '.csv'

        Posts = gather_posts_from_db()
        # adding custom words from config
        self.vader.lexicon.update(new_words)
                
        for post in Posts:
            stock = post[1]
            postText = post[2].replace('\x00', '')
            if stock in TweetCounts:                                                #   If a stock has had a tweet about it, TweetCount is incremented & TweetTexts gets new rows with text of the comment
                TweetCounts[stock] += 1
                TweetTexts[stock].append(postText)
        
            else:                                                                       #   Otherwise, initialize TweetCount TweetTexts
                TweetCounts[stock] = 1
                TweetTexts[stock] = [postText]

        SortedCounts = dict(sorted(TweetCounts.items(), key=lambda item: item[1], reverse = True))
        SortedList = list(SortedCounts.keys())
        
        for stock in SortedList:                                                                
            for tweet in TweetTexts[stock]:                                                         #   Runs through all comments for the most popular stocks                                          
                
                #TODO: MAKE IT SO THAT ONLY NEARBY WORDS ARE COUNTED (POSSIBLY REMOVE NOISE)
                tweet = processTweetText(tweet, stock)
                tweetScore = self.vader.polarity_scores(tweet)                                
                
                if (tweetScore['neu'] < self.maxNeutralSentiment):
                    

                    if stock in TweetScores:                                                      #   Adds score to CommentScores at index comment if a comment has been processed for it
                        TweetScores[stock][tweet] = tweetScore
                        if tweetScore['compound'] < -0.33:
                            ProcessedTweetCounts[stock]['neg'] += 1
                        elif tweetScore['compound'] < 0.33:
                            ProcessedTweetCounts[stock]['neu'] += 1
                        else:
                            ProcessedTweetCounts[stock]['pos'] += 1
                        ProcessedTweetCounts[stock]['total'] += 1
                    else:                                                                           #   Initializes CommentScores if a comment has not yet been processed for it.
                        TweetScores[stock] = {tweet:tweetScore}
                        if tweetScore['compound'] < -0.33:
                            ProcessedTweetCounts[stock] = {'neg': 1, 'neu': 0, 'pos': 0, 'total': 1}
                        elif tweetScore['compound'] < 0.33:
                            ProcessedTweetCounts[stock] = {'neg': 0, 'neu': 1, 'pos': 0, 'total': 1}
                        else:
                            ProcessedTweetCounts[stock] = {'neg': 0, 'neu': 0, 'pos': 1, 'total': 1}
                    
                    if stock in CumulativeScores:                                                   #   Adds score to CumulativeScores at if a comment has been processed for it
                        for sentimentType, score in tweetScore.items():                                                       
                            CumulativeScores[stock][sentimentType] = str(float(CumulativeScores[stock][sentimentType]) + score)
                    else:                                                                           #   Initializes CumulativeScores if a comment has not yet been processed for it.
                        CumulativeScores[stock] = tweetScore
                    

                    # calculating avg.
            try:
                for sentimentType in CumulativeScores[stock]:                                                   #   Runs through all scores for a stock
                    CumulativeScores[stock][sentimentType] = float(CumulativeScores[stock][sentimentType]) / float(ProcessedTweetCounts[stock]['total'])          #   The cumulative score for each type of sentiment (neg, neu, pos) is an average of all scores of that type. 
                    CumulativeScores[stock][sentimentType]  = "{pol:.3f}".format(pol=CumulativeScores[stock][sentimentType])        #   Formats CumulativeScores to 3 decimals
            except Exception:    #  Catch exceptions for stocks with posts, but without processed posts (neutral score under threshold)
                pass

        return ProcessedTweetCounts, CumulativeScores           

def upload_sentiment_to_db(scores, counts, date):
    try:
        print("Uploading Twitter Sentiment to DB")
        for stock in sorted(counts.keys(), key=lambda stock:(-counts[stock]['total'], stock)):
            insert_sentiment_score_to_db(str(date), stock, scores[stock]['neg'], scores[stock]['neu'], scores[stock]['pos'], scores[stock]['compound'], counts[stock]['neg'], counts[stock]['neu'], counts[stock]['pos'], counts[stock]['total'])
    except Exception:
        createNewConnection()
        upload_sentiment_to_db(scores, counts, date)

def gather_posts_from_db():	
    try:
        conn = postConn
        sql = """SELECT * FROM twitterposts"""
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql)
        Posts = cursor.fetchall()
        cursor.close()
        return Posts
    except Exception:
        createNewConnection()
        Posts = gather_posts_from_db()
        return Posts
    

def insert_sentiment_score_to_db(date, stock, neg, neu, pos, compound, numNeg, numNeu, numPos, numTot):					       
    '''
    Inserts sentiment scores into sentimentdata table
    '''
    try:
        conn = sentimentConn
        sql = """INSERT INTO sentimentdata (id, source, date, asset, score_neg, score_neu, score_pos, score_comp, num_neg, num_neu, num_pos, tot_posts) VALUES (null, 'twitter', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        sentimentData = (date, stock, neg, neu, pos, compound, numNeg, numNeu, numPos, numTot)
        cursor = conn.cursor()
        cursor.execute(sql, sentimentData)
        cursor.close()
        conn.commit()
    except Exception:
        createNewConnection()
        insert_sentiment_score_to_db(date, stock, neg, neu, pos, compound, numNeg, numNeu, numPos, numTot)
    
def clear_table_in_db():
    print("Clearing twitterposts db")

    try:
        conn = postConn
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM twitterposts""")
        cursor.close()
        conn.commit()
    except Exception:
        createNewConnection()
        clear_table_in_db()

def processTweetText(tweet, stock):
    newTweet = ""
    deconTweet = tweet.split(" ")
    for word in deconTweet:
        if len(word) > 1 and (word.isalnum() or word[0] == "$"):
            newTweet = newTweet + word + " "
        
    #print(stock + ": " + newTweet)

    return tweet

def createNewConnection():
    global postConn, sentimentConn
    sentimentConn = mysql.connect(user=USER, password=PASSWORD, host=HOST, database=SENTIMENTDB)
    postConn = mysql.connect(user=USER, password=PASSWORD, host=HOST, database=POSTDB)


