import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf

from pathlib import Path
import csv
import dateutil.parser as dparser 
from datetime import datetime, timedelta
from sklearn.cross_decomposition import CCA


def StockTool(df):
    
    #print(df.head())

    SentimentDF = df[['reddit_negative_posts', 'reddit_neutral_posts', 'reddit_positive_posts', 'reddit_negative_score', 'reddit_neutral_score', 'reddit_positive_score', 'reddit_comp_score', 'reddit_total_posts', 'reddit_sentiment_change', 'twitter_negative_posts', 'twitter_neutral_posts', 'twitter_positive_posts', 'twitter_negative_score', 'twitter_neutral_score', 'twitter_positive_score', 'twitter_comp_score', 'twitter_total_posts', 'twitter_sentiment_change']]
    #SentimentDF = df[['reddit_total_posts', 'reddit_comp_score', 'reddit_sentiment_change', 'twitter_total_posts', 'twitter_comp_score', 'twitter_sentiment_change']]

    #Standardize variables by subtracting with mean and dividing by standard deviation.
    Sentiment_mc = (SentimentDF-SentimentDF.mean())/(SentimentDF.std())
    #print(Sentiment_mc.head())

    PriceDF = df[['open','close', 'adj_close', 'high', 'low', 'volume', 'price_change_percent']]
    #PriceDF = df[['adj_close', 'volume', 'price_change_percent']]
    #print(PriceDF.head())

    #Standardize variables by subtracting with mean and dividing by standard deviation.
    Price_mc = (PriceDF-PriceDF.mean())/(PriceDF.std())
    #print(Price_mc.head())


    #Instantiate CCA object and use fit() and transform() functions with the two standardized matrices to perform CCA.
    ca = CCA()
    ca.fit(Sentiment_mc, Price_mc)
    Sentiment_c, Price_c = ca.transform(Sentiment_mc, Price_mc)
    #Metadata dataframe for CCA
    #print(Sentiment_c.shape)
    #print(Price_c.shape)

    cc_res = pd.DataFrame({
        "CCSentiment_1" : Sentiment_c[:, 0],
        "CCPrice_1" : Price_c[:, 0],
        "CCSentiment_2" : Sentiment_c[:, 1],
        "CCPrice_2" : Price_c[:, 1],
        "Stock" : df.stock.tolist(),
        "Date" : df.date.tolist()})


    #print(cc_res.head())

    #Correlation of first pair of canonical covariates. 
    #Uses NumPy’s corrcoef() function to compute correlation.
    print(np.corrcoef(Sentiment_c[:, 0], Price_c[:, 0]))

    #Correlation between second pair of covariates
    print(np.corrcoef(Sentiment_c[:, 1], Price_c[:, 1]))

    plt.figure(figsize=(10,8))
    sns.scatterplot(x="CCSentiment_1", y="CCPrice_1", hue="Stock", data=cc_res)
    plt.title('First Pair of Canonical Covariate, corr = %.2f' % np.corrcoef(Sentiment_c[:, 0], Price_c[:, 0])[0, 1])
    plt.show()


    ccSentiment_df = pd.DataFrame({
        "CCSentiment_1":Sentiment_c[:, 0],
        "CCSentiment_2":Sentiment_c[:, 1],
        "Stock":df.stock.astype('category').cat.codes,
        "Date":df.date.astype('category').cat.codes,

        "Negative Reddit Posts": Sentiment_mc.reddit_negative_posts, 
        "Neutral Reddit Posts": Sentiment_mc.reddit_neutral_posts, 
        "Positive Reddit Posts": Sentiment_mc.reddit_positive_posts,
        "Negative Reddit Score": Sentiment_mc.reddit_negative_score,
        "Neutral Reddit Score": Sentiment_mc.reddit_neutral_score,
        "Positive Reddit Score": Sentiment_mc.reddit_positive_score,
        "Compound Reddit Score": Sentiment_mc.reddit_comp_score,
        "Total Reddit Posts": Sentiment_mc.reddit_total_posts,
        "Reddit Sentiment Change": Sentiment_mc.reddit_sentiment_change,

        "Negative Twitter Posts": Sentiment_mc.twitter_negative_posts, 
        "Neutral Twitter Posts": Sentiment_mc.twitter_neutral_posts, 
        "Positive Twitter Posts": Sentiment_mc.twitter_positive_posts,
        "Negative Twitter Score": Sentiment_mc.twitter_negative_score,
        "Neutral Twitter Score": Sentiment_mc.twitter_neutral_score,
        "Positive Twitter Score": Sentiment_mc.twitter_positive_score,
        "Compound Twitter Score": Sentiment_mc.twitter_comp_score,
        "Total Twitter Posts": Sentiment_mc.twitter_total_posts,
        "Twitter Sentiment Change": Sentiment_mc.twitter_sentiment_change
        })
    
    corr_Sentiment_df= ccSentiment_df.corr(method='pearson')
    #print(corr_Sentiment_df.head())

    plt.figure(figsize=(10,8))
    Sentiment_df_lt = corr_Sentiment_df.where(np.tril(np.ones(corr_Sentiment_df.shape)).astype(bool))
    sns.heatmap(Sentiment_df_lt,cmap="coolwarm",annot=True,fmt='.1g')
    plt.tight_layout()


    ccPrice_df = pd.DataFrame({
        "CCPrice_1":Price_c[:, 0],
        "CCPrice_2":Price_c[:, 1],
        "Stock":df.stock.astype('category').cat.codes,
        "Date":df.date.astype('category').cat.codes,

        "Open":Price_mc.open,
        "Close":Price_mc.close,
        "Adj Close":Price_mc.adj_close,
        "High":Price_mc.high,
        "Low":Price_mc.low,
        "Volume":Price_mc.volume,
        "Price Change %":Price_mc.price_change_percent

        })

    plt.show()
    
    corr_Price_df= ccPrice_df.corr(method='pearson')
    #print(corr_Price_df.head())

    plt.figure(figsize=(10,8))
    Price_df_lt = corr_Price_df.where(np.tril(np.ones(corr_Price_df.shape)).astype(bool))
    sns.heatmap(Price_df_lt,cmap="coolwarm",annot=True,fmt='.1g')
    plt.tight_layout()

    plt.show()

#   Outline of New CCA:
#   For the top 50 most mentioned stocks:
#   For Twitter, Reddit, and Combined:
#   Random sample (Or exhaustive, permitting) using days & weeks of sentiment/price change

#   Runs through price change and sentiment data for a given stock, will be done for the top most mentioned stocks
#   Outline of new DF:
#   stock, date, compound_scores, total_posts, price_change_dollars, price_change_percent
#   OTHER NOTES
    #   Try with negative_posts, neutral_posts, positive_posts, volume, etc.
def createTop50DF():
    Top50Stocks = ['BTC', 'TSLA', 'ETH', 'GME', 'TWTR', 'AAPL', 'FB', 'AMZN', 'NFLX', 'NVDA', 'AMD', 'NIO', 'BABA', 'PLTR', 'MSFT', 'ROKU', 'PYPL', 'DKNG', 'UPST', 'MRNA', 'SQ', 'GOOGL', 'TLRY', 'GOOG', 'WMT', 'TGT', 'PTON', 'TDOC', 'XOM', 'UBER', 'JPM', 'BAC', 'SE', 'CVX', 'ZM', 'BYND', 'SBUX', 'OXY', 'ABNB', 'INTC', 'HYMC', 'BBBY', 'MU', 'TWLO', 'LYFT', 'LMT', 'FUBO', 'GM', 'JD', 'ETSY']
    StockList, DateList, RedditNegativePostList, RedditNeutralPostList, RedditPositivePostList, RedditNegativeScoreList, RedditNeutralScoreList, RedditPositiveScoreList, RedditCompoundScoreList, RedditTotalPostList, RedditSentimentChangeList, TwitterNegativePostList, TwitterNeutralPostList, TwitterPositivePostList, TwitterNegativeScoreList, TwitterNeutralScoreList, TwitterPositiveScoreList, TwitterCompoundScoreList, TwitterTotalPostList, TwitterSentimentChangeList, OpenCostList, CloseCostList, AdjCloseCostList, HighCostList, LowCostList, VolumeList, PriceChangePercentList = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []

    SentimentData = {"reddit": {}, "twitter": {}}
    PriceData = {}
    Dates = []
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
                    if row != []:
                        source = row[0]
                        stock = row[2]
                        sentimentChange = 0
                        if (stock in Top50Stocks):             
                            currentSentiment = float(row[6])
                            if not stock in prevSentiment[source]:
                                sentimentChange = 0
                            else:
                                sentimentChange = currentSentiment-prevSentiment[source][stock]

                            prevSentiment[source][stock] = currentSentiment
                
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
                                'positive_posts': row[9],
                                'total_posts': row[10],
                                'sentiment_change': sentimentChange
                                }
                csvFile.close() 
    
    startDate = min(Dates)

    #   Converts the oldest date in sentiment dictionary to a datetime in order to use time delta to subtract dates.
    startDateTime = datetime.strptime(startDate, '%Y-%m-%d')
    startDate = startDateTime - timedelta(days=5)
    endDate = max(Dates) 

    data = yf.download(Top50Stocks, start=startDate, end=endDate)
    prevPrice = {}



    for source in SentimentData:
        for date in SentimentData[source]:
            date_time = datetime.strptime(date, '%Y-%m-%d')

            for stock in SentimentData[source][date]:
                priceChangePercent = 0
                currentPrice = 0
                try:
                    currentPrice = float(data["Adj Close"][stock][date_time])
                except:
                    continue
            
                if not stock in prevPrice:
                    priceChangePercent = 0
                else:
                    priceChangePercent = 100*((currentPrice-prevPrice[stock])/currentPrice)

                prevPrice[stock] = currentPrice
                
                if not date in PriceData:
                    PriceData[date] = {}
                try:
                    PriceData[date][stock] = {
                        "stock": stock,
                        "open": data["Open"][stock][date_time],
                        "close": data["Close"][stock][date_time],
                        "adj_close": data["Adj Close"][stock][date_time],
                        "high": data["High"][stock][date_time],
                        "low": data["Low"][stock][date_time],
                        "volume": data["Volume"][stock][date_time],
                        "price_change_percent": priceChangePercent
                        }
                except Exception:
                    pass


    sentimentRedditDateSet = set(SentimentData["reddit"].keys())
    sentimentTwitterDateSet = set(SentimentData["twitter"].keys())
    priceDateSet = set(PriceData.keys())

    for date in priceDateSet.intersection(sentimentRedditDateSet, sentimentTwitterDateSet):
        sentimentRedditStockSet = set(SentimentData["reddit"][date].keys())
        sentimentTwitterStockSet = set(SentimentData["twitter"][date].keys())
        priceStockSet = set(PriceData[date].keys())

        for stock in priceStockSet.intersection(sentimentRedditStockSet, sentimentTwitterStockSet):

            StockList.append(stock)
            DateList.append(date)
            RedditNegativePostList.append(float(SentimentData["reddit"][date][stock]['negative_posts']))
            RedditNeutralPostList.append(float(SentimentData["reddit"][date][stock]['neutral_posts']))
            RedditPositivePostList.append(float(SentimentData["reddit"][date][stock]['positive_posts']))
            RedditNegativeScoreList.append(float(SentimentData["reddit"][date][stock]['negative_score']))
            RedditNeutralScoreList.append(float(SentimentData["reddit"][date][stock]['neutral_score']))
            RedditPositiveScoreList.append(float(SentimentData["reddit"][date][stock]['positive_score']))
            RedditCompoundScoreList.append(float(SentimentData["reddit"][date][stock]['comp_score']))
            RedditTotalPostList.append(float(SentimentData["reddit"][date][stock]['total_posts']))
            RedditSentimentChangeList.append(float(SentimentData["reddit"][date][stock]['sentiment_change']))

            TwitterNegativePostList.append(float(SentimentData["twitter"][date][stock]['negative_posts']))
            TwitterNeutralPostList.append(float(SentimentData["twitter"][date][stock]['neutral_posts']))
            TwitterPositivePostList.append(float(SentimentData["twitter"][date][stock]['positive_posts']))
            TwitterNegativeScoreList.append(float(SentimentData["twitter"][date][stock]['negative_score']))
            TwitterNeutralScoreList.append(float(SentimentData["twitter"][date][stock]['neutral_score']))
            TwitterPositiveScoreList.append(float(SentimentData["twitter"][date][stock]['positive_score']))
            TwitterCompoundScoreList.append(float(SentimentData["twitter"][date][stock]['comp_score']))
            TwitterTotalPostList.append(float(SentimentData["twitter"][date][stock]['total_posts']))
            TwitterSentimentChangeList.append(float(SentimentData["twitter"][date][stock]['sentiment_change']))

            OpenCostList.append(float(PriceData[date][stock]['open']))
            CloseCostList.append(float(PriceData[date][stock]['close']))
            AdjCloseCostList.append(float(PriceData[date][stock]['adj_close']))
            HighCostList.append(float(PriceData[date][stock]['high']))
            LowCostList.append(float(PriceData[date][stock]['low']))
            VolumeList.append(float(PriceData[date][stock]['volume']))
            PriceChangePercentList.append(float(PriceData[date][stock]['price_change_percent']))

    data = {
        "date": DateList,
        "stock": StockList,
        "reddit_negative_posts": RedditNegativePostList,
        "reddit_neutral_posts": RedditNeutralPostList,
        "reddit_positive_posts": RedditPositivePostList,
        "reddit_negative_score": RedditNegativeScoreList,
        "reddit_neutral_score": RedditNeutralScoreList,
        "reddit_positive_score": RedditPositiveScoreList,
        "reddit_comp_score": RedditCompoundScoreList, 
        "reddit_total_posts": RedditTotalPostList,
        "reddit_sentiment_change": RedditSentimentChangeList,

        "twitter_negative_posts": TwitterNegativePostList,
        "twitter_neutral_posts": TwitterNeutralPostList,
        "twitter_positive_posts": TwitterPositivePostList,
        "twitter_negative_score": TwitterNegativeScoreList,
        "twitter_neutral_score": TwitterNeutralScoreList,
        "twitter_positive_score": TwitterPositiveScoreList,
        "twitter_comp_score": TwitterCompoundScoreList, 
        "twitter_total_posts": TwitterTotalPostList,
        "twitter_sentiment_change": TwitterSentimentChangeList,
        
        "open": OpenCostList,
        "close": CloseCostList,
        "adj_close": AdjCloseCostList,
        "high": HighCostList,
        "low": LowCostList,
        "volume": VolumeList,
        "price_change_percent": PriceChangePercentList
        }   
    

    df = pd.DataFrame(data)

    print(df.to_string())
    df = df.dropna()
    df.to_csv('top50DF.csv')
    return df

def readTop50DF():
    return pd.read_csv('top50DF.csv')

if __name__ == '__main__':
    #df = createTop50DF()
    df = readTop50DF()
    StockTool(df)
