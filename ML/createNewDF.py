import pandas as pd
import yfinance as yf

from pathlib import Path
import csv
import dateutil.parser as dparser 
from datetime import date, datetime, timedelta


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


def getPriceChangeData(stock, date):
    global PriceData, yfData, Dates

    oneDayPrevDate = date - timedelta(days=1)
    twoDayPrevDate = date - timedelta(days=2)
    threeDayPrevDate = date - timedelta(days=3)
    oneDayAfterDate = date + timedelta(days=1)
    twoDayAfterDate = date + timedelta(days=2)
    threeDayAfterDate = date + timedelta(days=3)
    currentPrice = None
    prevPrice = None
    dailyPriceChange = None

    #print(date)
    #print(date.weekday())

    if date.weekday() == 5: #  Saturday
        try:
            fridayPrice = float(yfData["Adj Close"][stock][oneDayPrevDate])
        except: # Friday Holiday
            fridayPrice = float(yfData["Adj Close"][stock][twoDayPrevDate])

        try:
            mondayPrice = float(yfData["Adj Close"][stock][twoDayAfterDate])
        except: # Monday Holiday
            #print("here")
            if(threeDayAfterDate < (date.today()  - timedelta(days=1))):
                mondayPrice = float(yfData["Adj Close"][stock][threeDayAfterDate])
            else:
                mondayPrice = fridayPrice

        saturdayPrice = (fridayPrice + mondayPrice) / 2
        prevPrice = fridayPrice
        currentPrice = saturdayPrice
        dailyPriceChange = currentPrice - fridayPrice

    if date.weekday() == 6: #  Sunday
        try:
            fridayPrice = float(yfData["Adj Close"][stock][twoDayPrevDate])
        except Exception: # Friday Holiday
            fridayPrice = float(yfData["Adj Close"][stock][threeDayPrevDate])

        try:
            mondayPrice = float(yfData["Adj Close"][stock][oneDayAfterDate])
        except Exception: # Monday Holiday
            if(threeDayAfterDate < (date.today()  - timedelta(days=1))):
                mondayPrice = float(yfData["Adj Close"][stock][twoDayAfterDate])
            else:
                mondayPrice = fridayPrice
            

        saturdayPrice = (fridayPrice + mondayPrice) / 2
        sundayPrice = (saturdayPrice + mondayPrice) / 2
        prevPrice = saturdayPrice
        currentPrice = sundayPrice
        dailyPriceChange = currentPrice - saturdayPrice
    
    else:
        while(currentPrice == None):
            try:
                openPrice = float(yfData["Open"][stock][date])
                currentPrice = float(yfData["Adj Close"][stock][date])
                dailyPriceChange = currentPrice - openPrice
            except Exception: # Holiday
                pass
            date = date - timedelta(days=1)
            oneDayPrevDate = date - timedelta(days=1)
        while(prevPrice == None):
            try:
                prevPrice = float(yfData["Adj Close"][stock][oneDayPrevDate])
            except Exception: # Holiday
                pass
            oneDayPrevDate = oneDayPrevDate - timedelta(days=1)


    oneDayPriceChange = 100*((currentPrice-prevPrice)/currentPrice)

    return dailyPriceChange, oneDayPriceChange

def getSentimentData():
    global SentimentData, Dates
    prevSentiment = {'reddit': {}, 'twitter': {}}

    folderList = ["/Users/tymar/OneDrive/Documents/Capstone/Reddit/Sentiment Scores/", "/Users/tymar/OneDrive/Documents/Capstone/Twitter/Sentiment Scores/"]
    for folderName in folderList:
        for path in Path(folderName).iterdir():
            date = str(dparser.parse(str(path),fuzzy=True).date())
            if date not in Dates:
                Dates.append(date)
            with open(path, newline='') as csvFile:
                sentimentCSVReader = csv.reader(csvFile, delimiter=',')
                next(sentimentCSVReader)
                for row in sentimentCSVReader:
                    if row:             #   Prevents blank rows
                        source = row[0]
                        stock = row[2]
                        negativePosts = int(row[7])
                        positivePosts = int(row[9])
                        totalPosts = int(row[10])
                        percentPosPosts = 0
                        if (negativePosts+positivePosts != 0):
                            percentPosPosts =  positivePosts / (negativePosts + positivePosts)
                            #percentPosPosts =  positivePosts / totalPosts

                        if not date in SentimentData[source]:
                            SentimentData[source][date] = {}
                        SentimentData[source][date][stock] = {
                            'stock': stock,
                            'date': date,
                            'total_posts': totalPosts,
                            'percent_pos_posts': percentPosPosts
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

    for date in Dates:
        date_time = datetime.strptime(date, '%Y-%m-%d')
        for stock in Top50Stocks:
            
            dailyPriceChange, oneDayPriceChange = getPriceChangeData(stock, date_time)
                
            if not date in PriceData:
                PriceData[date] = {}
            try:
                PriceData[date][stock] = {
                    "stock": stock,
                    "daily_price_change": dailyPriceChange,
                    "one_day_price_change": oneDayPriceChange
                    }
            except Exception:
                pass

def createTop50DF():
    global SentimentData, PriceData, Dates, Top50Stocks

    print("Getting sentiment data")
    getSentimentData()
    print("Finished getting sentiment data")

    print("Getting price data")
    getPriceData()
    print("Finished getting price data")
    
    dfSchema = {"date": [],
        "stock": [],
        "reddit_percent_pos_posts": [],
        "reddit_total_posts": [],

        "twitter_percent_pos_posts": [],  
        "twitter_total_posts": [],  

        "daily_price_change": [],
        "one_day_price_change": [], 
       }
  
    df = pd.DataFrame(dfSchema)
  
    for date in Dates:

        for stock in Top50Stocks:

            reddit_total_posts, reddit_percent_pos_posts, twitter_total_posts, twitter_percent_pos_posts = 0, 0, 0, 0
            try:           
                reddit_total_posts = float(SentimentData["reddit"][date][stock]['total_posts'])
            except:
                print("no reddit post data for: " + str(stock) + " for " + str(date))
                pass
            try:           
                reddit_percent_pos_posts = float(SentimentData["reddit"][date][stock]['percent_pos_posts'])
            except:
                print("no reddit post data for: " + str(stock) + " for " + str(date))
                pass
            try:           
                twitter_total_posts = float(SentimentData["twitter"][date][stock]['total_posts'])
            except:
                print("no twitter post data for: " + str(stock) + " for " + str(date))
                pass
            try:           
                twitter_percent_pos_posts = float(SentimentData["twitter"][date][stock]['percent_pos_posts'])
            except:
                print("no twitter post data for: " + str(stock) + " for " + str(date))
                pass

            daily_price_change, one_day_price_change = 0, 0
            try:
                daily_price_change = float(PriceData[date][stock]['daily_price_change'])
                one_day_price_change = float(PriceData[date][stock]['one_day_price_change'])
            except:
                print("no price data")
                pass
                
            df.loc[len(df.index)] = [date, stock, reddit_percent_pos_posts, reddit_total_posts, twitter_percent_pos_posts, twitter_total_posts, daily_price_change, one_day_price_change] 
  
    print(df.to_string())
    df.to_csv('top50ReducedDF.csv')

if __name__ == '__main__':
    createTop50DF()
