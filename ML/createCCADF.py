import pandas as pd
import yfinance as yf

from pathlib import Path
import csv
import dateutil.parser as dparser 
from datetime import datetime, timedelta



Dates = []
Top50Stocks = ['BTC', 'TSLA', 'GME', 'TWTR', 'AAPL', 'FB', 'AMZN', 'NFLX', 'NVDA', 'AMD', 'NIO', 'BABA', 'PLTR', 'MSFT', 'ROKU', 'PYPL', 'DKNG', 'UPST', 'MRNA', 'SQ', 'GOOGL', 'TLRY', 'GOOG', 'WMT', 'TGT', 'PTON', 'TDOC', 'XOM', 'UBER', 'JPM', 'BAC', 'SE', 'CVX', 'ZM', 'BYND', 'SBUX', 'OXY', 'ABNB', 'INTC', 'HYMC', 'BBBY', 'MU', 'TWLO', 'LYFT', 'LMT', 'FUBO', 'GM', 'JD', 'ETSY']

SentimentData = {"reddit": {}, "twitter": {}}
PriceData = {}
yfData = None

#   Outline of New CCA:
#   For the top 50 most mentioned stocks:
#   For Twitter, Reddit, and Combined:
#   Random sample (Or exhaustive, permitting) using days & weeks of sentiment/price change

#   Runs through price change and sentiment data for a given stock, will be done for the top most mentioned stocks
#   Outline of new DF:
#   stock, date, compound_scores, total_posts, price_change_dollars, price_change_percent
#   OTHER NOTES
    #   Try with negative_posts, neutral_posts, positive_posts, volume, etc.

def getSentimentChangeData(source, stock, date, sentiment, posts):
    global SentimentData
    date = dparser.parse(date,fuzzy=True).date()

    oneDayPrevDate = str(date - timedelta(days=1))
    threeDayPrevDate = str(date - timedelta(days=3))
    fiveDayPrevDate = str(date - timedelta(days=5))
    oneWeekPrevDate = str(date - timedelta(weeks=1))
    twoWeekPrevDate = str(date - timedelta(weeks=2))
    threeWeekPrevDate = str(date - timedelta(weeks=3))
    oneMonthPrevDate = str(date - timedelta(weeks=4))
    oneDayPrevSentiment, threeDayPrevSentiment, fiveDayPrevSentiment, oneWeekPrevSentiment, twoWeekPrevSentiment, threeWeekPrevSentiment, oneMonthPrevSentiment = 0, 0, 0, 0, 0, 0, 0

    oneDayPrevPosts, threeDayPrevPosts, fiveDayPrevPosts, oneWeekPrevPosts, twoWeekPrevPosts, threeWeekPrevPosts, oneMonthPrevPosts = 0, 0, 0, 0, 0, 0, 0
    #print(SentimentData)
    #print(str(date))
    #print(str(oneDayPrevDate))
    try:
        #print(SentimentData[source][oneDayPrevDate][stock]["comp_score"])
        oneDayPrevSentiment = SentimentData[source][oneDayPrevDate][stock]["comp_score"]
        threeDayPrevSentiment = SentimentData[source][threeDayPrevDate][stock]["comp_score"]
        fiveDayPrevSentiment = SentimentData[source][fiveDayPrevDate][stock]["comp_score"]
        oneWeekPrevSentiment = SentimentData[source][oneWeekPrevDate][stock]["comp_score"]
        twoWeekPrevSentiment = SentimentData[source][twoWeekPrevDate][stock]["comp_score"]
        threeWeekPrevSentiment = SentimentData[source][threeWeekPrevDate][stock]["comp_score"]
        oneMonthPrevSentiment = SentimentData[source][oneMonthPrevDate][stock]["comp_score"]

        oneDayPrevPosts = SentimentData[source][oneDayPrevDate][stock]["total_posts"]
        threeDayPrevPosts = SentimentData[source][threeDayPrevDate][stock]["total_posts"]
        fiveDayPrevPosts = SentimentData[source][fiveDayPrevDate][stock]["total_posts"]
        oneWeekPrevPosts = SentimentData[source][oneWeekPrevDate][stock]["total_posts"]
        twoWeekPrevPosts = SentimentData[source][twoWeekPrevDate][stock]["total_posts"]
        threeWeekPrevPosts = SentimentData[source][threeWeekPrevDate][stock]["total_posts"]
        oneMonthPrevPosts = SentimentData[source][oneMonthPrevDate][stock]["total_posts"]
    except Exception:
        pass
    
    #print(sentiment)
    #print(oneDayPrevSentiment)

    oneDaySentimentChange, threeDaySentimentChange, fiveDaySentimentChange,  oneWeekSentimentChange, twoWeekSentimentChange, threeWeekSentimentChange, oneMonthSentimentChange = 0, 0, 0, 0, 0, 0, 0


    if oneDayPrevSentiment != 0:
        oneDaySentimentChange = sentiment - oneDayPrevSentiment
    
    if threeDayPrevSentiment != 0:
        threeDaySentimentChange = sentiment - threeDayPrevSentiment

    if fiveDayPrevSentiment != 0:
        fiveDaySentimentChange = sentiment - fiveDayPrevSentiment

    if oneWeekPrevSentiment != 0:
        oneWeekSentimentChange = sentiment - oneWeekPrevSentiment

    if twoWeekPrevSentiment != 0:
        twoWeekSentimentChange = sentiment - twoWeekPrevSentiment

    if threeWeekPrevSentiment != 0:
        threeWeekSentimentChange = sentiment - threeWeekPrevSentiment

    if oneMonthPrevSentiment != 0:
        oneMonthSentimentChange = sentiment - oneMonthPrevSentiment

    #print("Stock: + " + stock + ", 1 day change: " + str(oneDaySentimentChange) + ", 3 day change: " + str(threeDaySentimentChange) + ", 5 day change: " + str(fiveDaySentimentChange) + ", 1 week change: " + str(oneWeekSentimentChange)) 

    return oneDaySentimentChange, threeDaySentimentChange, fiveDaySentimentChange, oneWeekSentimentChange, twoWeekSentimentChange, threeWeekSentimentChange, oneMonthSentimentChange, oneDayPrevPosts, threeDayPrevPosts, fiveDayPrevPosts, oneWeekPrevPosts, twoWeekPrevPosts, threeWeekPrevPosts, oneMonthPrevPosts

def getPriceChangeData(stock, date):
    global PriceData, yfData, Dates

    currentPrice = float(yfData["Adj Close"][stock][date])

    oneDayPrevDate = date - timedelta(days=1)
    threeDayPrevDate = date - timedelta(days=3)
    fiveDayPrevDate = date - timedelta(days=5)
    oneWeekPrevDate = date - timedelta(weeks=1)
    twoWeekPrevDate = date - timedelta(weeks=2)
    threeWeekPrevDate = date - timedelta(weeks=3)
    oneMonthPrevDate = date - timedelta(weeks=4)

    oneDayPrevPrice, threeDayPrevPrice, fiveDayPrevPrice, oneWeekPrevPrice, twoWeekPrevPrice, threeWeekPrevPrice, oneMonthPrevPrice = 0, 0, 0, 0, 0, 0, 0

    #print(PriceData)
    #print(str(date))
    #print(str(oneDayPrevDate))
    try:
        oneDayPrevPrice = float(yfData["Adj Close"][stock][oneDayPrevDate])
    except Exception:
        oneDayPrevPrice = currentPrice
    
    try:
        threeDayPrevPrice = float(yfData["Adj Close"][stock][threeDayPrevDate])
    except Exception:
        threeDayPrevPrice = oneDayPrevPrice

    try:
        fiveDayPrevPrice = float(yfData["Adj Close"][stock][fiveDayPrevDate])
    except Exception:
        fiveDayPrevPrice = threeDayPrevPrice
    
    try:
        oneWeekPrevPrice = float(yfData["Adj Close"][stock][oneWeekPrevDate])
    except Exception:
        oneWeekPrevPrice = fiveDayPrevPrice

    try:
        twoWeekPrevPrice = float(yfData["Adj Close"][stock][twoWeekPrevDate])
    except Exception:
        twoWeekPrevPrice = oneWeekPrevPrice

    try:
        threeWeekPrevPrice = float(yfData["Adj Close"][stock][threeWeekPrevDate])
    except Exception:
        threeWeekPrevPrice = twoWeekPrevPrice

    try:
        oneMonthPrevPrice = float(yfData["Adj Close"][stock][oneMonthPrevDate])
    except Exception:
        oneMonthPrevPrice = threeWeekPrevPrice

    oneDayPriceChange, threeDayPriceChange, fiveDayPriceChange,  oneWeekPriceChange, twoWeekPriceChange, threeWeekPriceChange, oneMonthPriceChange = 0, 0, 0, 0, 0, 0, 0

    oneDayPriceChange = 100*((currentPrice-oneDayPrevPrice)/currentPrice)
    threeDayPriceChange = 100*((currentPrice-threeDayPrevPrice)/currentPrice)
    fiveDayPriceChange = 100*((currentPrice-fiveDayPrevPrice)/currentPrice)
    oneWeekPriceChange = 100*((currentPrice-oneWeekPrevPrice)/currentPrice)
    twoWeekPriceChange = 100*((currentPrice-twoWeekPrevPrice)/currentPrice)
    threeWeekPriceChange = 100*((currentPrice-threeWeekPrevPrice)/currentPrice)
    oneMonthPriceChange = 100*((currentPrice-oneMonthPrevPrice)/currentPrice)
    
    #print("Stock: " + stock + ", 1 day change: " + str(oneDayPriceChange) + ", 3 day change: " + str(threeDayPriceChange) + ", 5 day change: " + str(fiveDayPriceChange) + ", 1 week change: " + str(oneWeekPriceChange)) 

    return oneDayPriceChange, threeDayPriceChange, fiveDayPriceChange, oneWeekPriceChange, twoWeekPriceChange, threeWeekPriceChange, oneMonthPriceChange

def getSentimentData():
    global SentimentData, Dates
    prevSentiment = {'reddit': {}, 'twitter': {}}

    folderList = ["/Users/tymar/OneDrive/Documents/Capstone/Reddit/Sentiment Scores/", "/Users/tymar/OneDrive/Documents/Capstone/Twitter/Sentiment Scores/"]
    for folderName in folderList:
        for path in Path(folderName).iterdir():
            date = str(dparser.parse(str(path),fuzzy=True).date())
            Dates.append(date)
            with open(path, newline='') as csvFile:
                sentimentCSVReader = csv.reader(csvFile, delimiter=',')
                next(sentimentCSVReader)
                for row in sentimentCSVReader:
                    if row:             #   Prevents blank rows
                        source = row[0]
                        stock = row[2]
                        currentSentiment = float(row[6])
                        totalPosts = int(row[10])
                        negativePosts = int(row[7])
                        positivePosts = int(row[9])
                        oneDaySentimentChange, threeDaySentimentChange, fiveDaySentimentChange, oneWeekSentimentChange, twoWeekSentimentChange, threeWeekSentimentChange, oneMonthSentimentChange, oneDayPrevPosts, threeDayPrevPosts, fiveDayPrevPosts, oneWeekPrevPosts, twoWeekPrevPosts, threeWeekPrevPosts, oneMonthPrevPosts = getSentimentChangeData(source, stock, date, currentSentiment, totalPosts)
                        percentPosPosts = 0
                        if (negativePosts+positivePosts != 0):
                            percentPosPosts =  positivePosts / (negativePosts + positivePosts)
                    
                        if not date in SentimentData[source]:
                            SentimentData[source][date] = {}
                        SentimentData[source][date][stock] = {
                            'stock': stock,
                            'negative_score': row[3],
                            'neutral_score': row[4],
                            'positive_score': row[5],
                            'comp_score': currentSentiment,
                            'negative_posts': row[7],
                            'neutral_posts': row[8],
                            'positive_posts': positivePosts,
                            'total_posts': totalPosts,
                            'percent_pos_posts': percentPosPosts,
                            'one_day_sentiment_change': oneDaySentimentChange,
                            'three_day_sentiment_change': threeDaySentimentChange,
                            'five_day_sentiment_change': fiveDaySentimentChange,
                            'one_week_sentiment_change': oneWeekSentimentChange,
                            'two_week_sentiment_change': twoWeekSentimentChange,
                            'three_week_sentiment_change': threeWeekSentimentChange,
                            'one_month_sentiment_change': oneMonthSentimentChange,
                            'one_day_prev_posts': oneDayPrevPosts,
                            'three_day_prev_posts': threeDayPrevPosts,
                            'five_day_prev_posts': fiveDayPrevPosts,
                            'one_week_prev_posts': oneWeekPrevPosts,
                            'two_week_prev_posts': twoWeekPrevPosts,
                            'three_week_prev_posts': threeWeekPrevPosts,
                            'one_month_prev_posts': oneMonthPrevPosts
                            }
            csvFile.close()

def getPriceData():
    global SentimentData, PriceData, yfData, Dates, Top50Stocks
    startDate = min(Dates)

    #   Converts the oldest date in sentiment dictionary to a datetime in order to use time delta to subtract dates.
    startDateTime = datetime.strptime(startDate, '%Y-%m-%d')
    startDate = startDateTime - timedelta(weeks=5)
    endDate = max(Dates) 
    yfData = yf.download(Top50Stocks, start=startDate, end=endDate)
    prevPrice = {}

    for date in Dates:
        date_time = datetime.strptime(date, '%Y-%m-%d')
        for stock in SentimentData["twitter"][date]:
            currentPrice = 0
                
            try:
                currentPrice = float(yfData["Adj Close"][stock][date_time])
            except:
                continue
            
            oneDayPriceChange, threeDayPriceChange, fiveDayPriceChange, oneWeekPriceChange, twoWeekPriceChange, threeWeekPriceChange, oneMonthPriceChange = getPriceChangeData(stock, date_time)
                
            if not date in PriceData:
                PriceData[date] = {}
            try:
                PriceData[date][stock] = {
                    "stock": stock,
                    "open": yfData["Open"][stock][date_time],
                    "close": yfData["Close"][stock][date_time],
                    "adj_close": currentPrice,
                    "high": yfData["High"][stock][date_time],
                    "low": yfData["Low"][stock][date_time],
                    "volume": yfData["Volume"][stock][date_time],
                    "one_day_price_change": oneDayPriceChange,
                    "three_day_price_change": threeDayPriceChange,
                    "five_day_price_change": fiveDayPriceChange,
                    "one_week_price_change": oneWeekPriceChange,
                    "two_week_price_change": twoWeekPriceChange,
                    "three_week_price_change": oneWeekPriceChange,
                    "one_month_price_change": oneMonthPriceChange
                    }
            except Exception:
                pass

def createTop50DF():
    global SentimentData, PriceData

    print("Getting sentiment change data")
    getSentimentData()
    print("Finished getting sentiment change data")

    print("Getting price change data")
    getPriceData()
    print("Finished getting price change data")
    
    dfSchema = {"date": [],
        "stock": [],
        "reddit_negative_posts": [],
        "reddit_neutral_posts": [],
        "reddit_positive_posts": [],
        "reddit_negative_score": [],
        "reddit_neutral_score": [],
        "reddit_positive_score": [],
        "reddit_comp_score": [], 
        "reddit_total_posts": [],
        "reddit_percent_pos_posts": [],
        "one_day_reddit_sentiment_change": [],
        "three_day_reddit_sentiment_change": [],
        "five_day_reddit_sentiment_change": [],
        "one_week_reddit_sentiment_change": [],
        "two_week_reddit_sentiment_change": [],
        "three_week_reddit_sentiment_change": [],
        "one_month_reddit_sentiment_change": [],

        "twitter_negative_posts": [],
        "twitter_neutral_posts": [],
        "twitter_positive_posts": [],
        "twitter_negative_score": [],
        "twitter_neutral_score": [],
        "twitter_positive_score": [],
        "twitter_comp_score": [], 
        "twitter_total_posts": [],
        "twitter_percent_pos_posts": [],
        "one_day_twitter_sentiment_change": [],
        "three_day_twitter_sentiment_change": [],
        "five_day_twitter_sentiment_change": [],
        "one_week_twitter_sentiment_change": [],
        "two_week_twitter_sentiment_change": [],
        "three_week_twitter_sentiment_change": [],
        "one_month_twitter_sentiment_change": [],

        "one_day_twitter_prev_posts": [],
        "three_day_twitter_prev_posts": [],
        "five_day_twitter_prev_posts": [],
        "one_week_twitter_prev_posts": [],
        "two_week_twitter_prev_posts": [],
        "three_week_twitter_prev_posts": [],
        "one_month_twitter_prev_posts": [],
        
        "adj_close": [],
        "volume": [],
        "one_day_price_change": [], 
        "three_day_price_change": [],
        "five_day_price_change": [],
        "one_week_price_change": [],
        "two_week_price_change": [],
        "three_week_price_change": [],
        "one_month_price_change": []
       }
  
    df = pd.DataFrame(dfSchema)
  
    sentimentRedditDateSet = set(SentimentData["reddit"].keys())
    sentimentTwitterDateSet = set(SentimentData["twitter"].keys())
    priceDateSet = set(PriceData.keys())
    for date in priceDateSet.intersection(sentimentRedditDateSet, sentimentTwitterDateSet):
        sentimentRedditStockSet = set(SentimentData["reddit"][date].keys())
        sentimentTwitterStockSet = set(SentimentData["twitter"][date].keys())
        priceStockSet = set(PriceData[date].keys())
        for stock in priceStockSet.intersection(sentimentRedditStockSet, sentimentTwitterStockSet):

            reddit_negative_posts = float(SentimentData["reddit"][date][stock]['negative_posts'])
            reddit_neutral_posts = float(SentimentData["reddit"][date][stock]['neutral_posts'])
            reddit_positive_posts = float(SentimentData["reddit"][date][stock]['positive_posts'])
            reddit_negative_score = float(SentimentData["reddit"][date][stock]['negative_score'])
            reddit_neutral_score = float(SentimentData["reddit"][date][stock]['neutral_score'])
            reddit_positive_score = float(SentimentData["reddit"][date][stock]['positive_score'])
            reddit_comp_score = float(SentimentData["reddit"][date][stock]['comp_score'])
            reddit_total_posts = float(SentimentData["reddit"][date][stock]['total_posts'])
            reddit_percent_pos_posts = float(SentimentData["reddit"][date][stock]['percent_pos_posts'])
            one_day_reddit_sentiment_change = float(SentimentData["reddit"][date][stock]['one_day_sentiment_change'])
            three_day_reddit_sentiment_change = float(SentimentData["reddit"][date][stock]['three_day_sentiment_change'])
            five_day_reddit_sentiment_change = float(SentimentData["reddit"][date][stock]['five_day_sentiment_change'])
            one_week_reddit_sentiment_change = float(SentimentData["reddit"][date][stock]['one_week_sentiment_change'])
            two_week_reddit_sentiment_change = float(SentimentData["reddit"][date][stock]['two_week_sentiment_change'])
            three_week_reddit_sentiment_change = float(SentimentData["reddit"][date][stock]['three_week_sentiment_change'])
            one_month_reddit_sentiment_change = float(SentimentData["reddit"][date][stock]['one_month_sentiment_change'])

            twitter_negative_posts = float(SentimentData["twitter"][date][stock]['negative_posts'])
            twitter_neutral_posts = float(SentimentData["twitter"][date][stock]['neutral_posts'])
            twitter_positive_posts = float(SentimentData["twitter"][date][stock]['positive_posts'])
            twitter_negative_score = float(SentimentData["twitter"][date][stock]['negative_score'])
            twitter_neutral_score = float(SentimentData["twitter"][date][stock]['neutral_score'])
            twitter_positive_score = float(SentimentData["twitter"][date][stock]['positive_score'])
            twitter_comp_score = float(SentimentData["twitter"][date][stock]['comp_score'])
            twitter_total_posts = float(SentimentData["twitter"][date][stock]['total_posts'])
            twitter_percent_pos_posts = float(SentimentData["twitter"][date][stock]['percent_pos_posts'])
            one_day_twitter_sentiment_change = float(SentimentData["twitter"][date][stock]['one_day_sentiment_change'])
            three_day_twitter_sentiment_change = float(SentimentData["twitter"][date][stock]['three_day_sentiment_change'])
            five_day_twitter_sentiment_change = float(SentimentData["twitter"][date][stock]['five_day_sentiment_change'])
            one_week_twitter_sentiment_change = float(SentimentData["twitter"][date][stock]['one_week_sentiment_change'])
            two_week_twitter_sentiment_change = float(SentimentData["twitter"][date][stock]['two_week_sentiment_change'])
            three_week_twitter_sentiment_change = float(SentimentData["twitter"][date][stock]['three_week_sentiment_change'])
            one_month_twitter_sentiment_change = float(SentimentData["twitter"][date][stock]['one_month_sentiment_change'])
            one_day_twitter_prev_posts = float(SentimentData["twitter"][date][stock]['one_day_prev_posts'])
            three_day_twitter_prev_posts = float(SentimentData["twitter"][date][stock]['three_day_prev_posts'])
            five_day_twitter_prev_posts = float(SentimentData["twitter"][date][stock]['five_day_prev_posts'])
            one_week_twitter_prev_posts = float(SentimentData["twitter"][date][stock]['one_week_prev_posts'])
            two_week_twitter_prev_posts = float(SentimentData["twitter"][date][stock]['two_week_prev_posts'])
            three_week_twitter_prev_posts = float(SentimentData["twitter"][date][stock]['three_week_prev_posts'])
            one_month_twitter_prev_posts = float(SentimentData["twitter"][date][stock]['one_month_prev_posts'])

            adj_close = float(PriceData[date][stock]['adj_close'])
            volume = float(PriceData[date][stock]['volume'])
            one_day_price_change = float(PriceData[date][stock]['one_day_price_change'])
            three_day_price_change = float(PriceData[date][stock]['three_day_price_change'])
            five_day_price_change = float(PriceData[date][stock]['five_day_price_change'])
            one_week_price_change = float(PriceData[date][stock]['one_week_price_change'])
            two_week_price_change = float(PriceData[date][stock]['two_week_price_change'])
            three_week_price_change = float(PriceData[date][stock]['three_week_price_change'])
            one_month_price_change = float(PriceData[date][stock]['one_month_price_change'])

            df.loc[len(df.index)] = [date, stock, reddit_negative_posts, reddit_neutral_posts, reddit_positive_posts, reddit_negative_score, reddit_neutral_score, reddit_positive_score, reddit_comp_score, reddit_total_posts, reddit_percent_pos_posts, one_day_reddit_sentiment_change, three_day_reddit_sentiment_change, five_day_reddit_sentiment_change, one_week_reddit_sentiment_change, two_week_reddit_sentiment_change, three_week_reddit_sentiment_change, one_month_reddit_sentiment_change, twitter_negative_posts, twitter_neutral_posts, twitter_positive_posts, twitter_negative_score, twitter_neutral_score, twitter_positive_score, twitter_comp_score, twitter_total_posts, twitter_percent_pos_posts, one_day_twitter_sentiment_change, three_day_twitter_sentiment_change, five_day_twitter_sentiment_change, one_week_twitter_sentiment_change,two_week_twitter_sentiment_change, three_week_twitter_sentiment_change,one_month_twitter_sentiment_change, one_day_twitter_prev_posts, three_day_twitter_prev_posts, five_day_twitter_prev_posts, one_week_twitter_prev_posts,two_week_twitter_prev_posts, three_week_twitter_prev_posts,one_month_twitter_prev_posts, adj_close, volume, one_day_price_change, three_day_price_change, five_day_price_change, one_week_price_change, two_week_price_change, three_week_price_change, one_month_price_change] 
  
    print(df.to_string())
    df = df.dropna()
    df.to_csv('top50DF.csv')

if __name__ == '__main__':
    createTop50DF()
