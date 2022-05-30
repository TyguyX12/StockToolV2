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

#https://cmdlinetips.com/2020/12/canonical-correlation-analysis-in-python/
def example():
    link2data = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
    df = pd.read_csv(link2data)
    df =df.dropna()
    #print(df.head())

    X = df[['bill_length_mm','bill_depth_mm']]
    #print(X.head())

    #bill_length_mm  bill_depth_mm
    #0   39.1    18.7
    #1   39.5    17.4
    #2   40.3    18.0
    #4   36.7    19.3
    #5   39.3    20.6

    #print(X.head())
    X_mc = (X-X.mean())/(X.std())
    #print(X_mc.head())
 
    #    bill_length_mm  bill_depth_mm
    #0   -0.894695   0.779559
    #1   -0.821552   0.119404
    #2   -0.675264   0.424091
    #4   -1.333559   1.084246
    #5   -0.858123   1.744400

    Y = df[['flipper_length_mm','body_mass_g']]
    #print(Y.head())

    Y_mc = (Y-Y.mean())/(Y.std())
    #print(Y_mc.head())
    #    flipper_length_mm   body_mass_g
    #0   -1.424608   -0.567621
    #1   -1.067867   -0.505525
    #2   -0.425733   -1.188572
    #4   -0.568429   -0.940192
    #5   -0.782474   -0.691811

    ca = CCA()
    ca.fit(X_mc, Y_mc)
    X_c, Y_c = ca.transform(X_mc, Y_mc)

    cc_res = pd.DataFrame({"CCX_1":X_c[:, 0],
                           "CCY_1":Y_c[:, 0],
                           "CCX_2":X_c[:, 1],
                           "CCY_2":Y_c[:, 1],
                           "Species":df.species.tolist(),
                          "Island":df.island.tolist(),
                          "sex":df.sex.tolist()})

    #print(cc_res.head())
    #    CCX_1   CCY_1   CCX_2   CCY_2   Species Island  sex
    #0   -1.186252   -1.408795   -0.010367   0.682866    Adelie  Torgersen   MALE
    #1   -0.709573   -1.053857   -0.456036   0.429879    Adelie  Torgersen   FEMALE
    #2   -0.790732   -0.393550   -0.130809   -0.839620   Adelie  Torgersen   FEMALE
    #3   -1.718663   -0.542888   -0.073623   -0.458571   Adelie  Torgersen   FEMALE
    #4   -1.772295   -0.763548   0.736248    -0.014204   Adelie  Torgersen   MALE

    #print(np.corrcoef(X_c[:, 0], Y_c[:, 0]))
    #array([[1.        , 0.78763151],
    #       [0.78763151, 1.        ]])

    #print(np.corrcoef(X_c[:, 1], Y_c[:, 1]))
 
    #array([[1.        , 0.08638695],
    #       [0.08638695, 1.        ]])


    sns.set_context("talk", font_scale=1.2)
    plt.figure(figsize=(10,8))
    sns.scatterplot(x="CCX_1",
                    y="CCY_1", 
                    data=cc_res)
    plt.title('Comp. 1, corr = %.2f' %
             np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1])
    #plt.show()



    plt.figure(figsize=(10,8))
    sns.boxplot(x="Species",
                    y="CCX_1", 
                   data=cc_res)
    sns.stripplot(x="Species",
                    y="CCX_1", 
                     data=cc_res)
    #plt.show()


    plt.figure(figsize=(10,8))
    sns.boxplot(x="Species",
                    y="CCY_1", 
                     data=cc_res)
    sns.stripplot(x="Species",
                    y="CCY_1", 
                     data=cc_res)
    #plt.show()


    plt.figure(figsize=(10,8))
    sns.scatterplot(x="CCX_1",
                    y="CCY_1", 
                    hue="Species", data=cc_res)
    plt.title('First Pair of Canonical Covariate, corr = %.2f' %
             np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1])
    #plt.show()

#   Outline of New CCA:
#   For the top 50 most mentioned stocks:
#   For Twitter, Reddit, and Combined:
#   Random sample (Or exhaustive, permitting) using days & weeks of sentiment/price change
def StockTool():
    
    df = createDF("AAPL")
    df = df.dropna()

    #print(df.head())

    #X is the dataset referring to sentiment
    SentimentDF = df[['comp_scores', 'total_posts']]

    #Standardize variables by subtracting with mean and dividing by standard deviation.
    Sentiment_mc = (SentimentDF-SentimentDF.mean())/(SentimentDF.std())
    #print(Sentiment_mc.head())

    #Y is the dataset referring to price change
    PriceDF = df[['price_change_dollars','price_change_percent']]
    #print(PriceDF.head())

    #Standardize variables by subtracting with mean and dividing by standard deviation.
    Price_mc = (PriceDF-PriceDF.mean())/(PriceDF.std())
    #print(Price_mc.head())

    

    #Instantiate CCA object and use fit() and transform() functions with the two standardized matrices to perform CCA.
    ca = CCA()
    ca.fit(Sentiment_mc, Price_mc)
    Sentiment_c, Price_c = ca.transform(Sentiment_mc, Price_mc)
    #Metadata dataframe for CCA

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
    #print(np.corrcoef(Sentiment_c[:, 0], Price_c[:, 0]))

    #Correlation between second pair of covariates
    #print(np.corrcoef(Sentiment_c[:, 1], Price_c[:, 1]))

    #Scatter plot 
    sns.set_context("talk", font_scale=1.2)
    plt.figure(figsize=(10,8))
    sns.scatterplot(x="CCSentiment_1",
                    y="CCPrice_1", 
                    data=cc_res)
    plt.title('Comp. 1, corr = %.2f' %
             np.corrcoef(Sentiment_c[:, 0], Price_c[:, 0])[0, 1])
    plt.show()

#   Runs through price change and sentiment data for a given stock, will be done for the top most mentioned stocks
#   Outline of new DF:
#   stock, date, compound_scores, total_posts, price_change_dollars, price_change_percent
#   OTHER NOTES
    #   Try with negative_posts, neutral_posts, positive_posts, volume, etc.
def createDF(stock):
    StockList, DateList, CompoundScoreList, TotalPostList, PriceChangeDollarsList, PriceChangePercentList = [], [], [], [], [], []
    SentimentData = {}
    PriceData = {}

    folderList = ["/Users/tymar/OneDrive/Documents/Capstone/Reddit/Sentiment Scores/", "/Users/tymar/OneDrive/Documents/Capstone/Twitter/Sentiment Scores/"]
    for folderName in folderList:
        for path in Path(folderName).iterdir():
            date = str(dparser.parse(str(path),fuzzy=True).date())
            with open(path, newline='') as csvFile:
                sentimentCSVReader = csv.reader(csvFile, delimiter=',')
                next(sentimentCSVReader)
                for row in sentimentCSVReader:
                    if row != []:
                        SentimentData[date] = {
                            'negative_score': row[3],
                            'neutral_score': row[4],
                            'positive_score': row[5],
                            'comp_scores': row[6],
                            'negative_posts': row[7],
                            'neutral_posts': row[8],
                            'positive_posts': row[9],
                            'total_posts': row[10]
                            }
                csvFile.close()

    startDate = min(SentimentData.keys())
    
    #   Converts the oldest date in sentiment dictionary to a datetime in order to use time delta to subtract dates.
    startDateTime = datetime.strptime(startDate, '%Y-%m-%d')
    startDate = startDateTime - timedelta(days=5)
    
    endDate = max(SentimentData.keys()) 
    data = yf.download(stock, start=startDate, end=endDate)
    data['ticker'] = stock  # add this column because the dataframe doesn't contain a column with the ticker
    prevPrice = 0
    for row in data.itertuples():
        #print("Prev Price: " + str(prevPrice))
        #print("Current Price: " + str(row.Close))

        date = row.Index.strftime("%Y-%m-%d")

        priceChange = row.Close - prevPrice
        priceChangePercent = 100*((row.Close-prevPrice)/float(row.Close))
        #print("Price Change: " + str(priceChange))
        #print("Price Change %: " + str(priceChangePercent))
        prevPrice = row.Close
  
        PriceData[date] = {
            'open': row.Open,
            'close': row.Close,
            'volume': row.Volume,
            'price_change_dollars': priceChange,
            'price_change_percent': priceChangePercent
            }

    sentimentSet = set(SentimentData.keys())
    priceSet = set(PriceData.keys())

    for date in sentimentSet.intersection(priceSet):
        StockList.append(stock)
        DateList.append(date)
        CompoundScoreList.append(float(SentimentData[date]['comp_scores']))
        TotalPostList.append(float(SentimentData[date]['total_posts']))
        PriceChangeDollarsList.append(float(PriceData[date]['price_change_dollars']))
        PriceChangePercentList.append(float(PriceData[date]['price_change_percent']))
    data = {
        "stock": StockList,
        "date": DateList,
        "comp_scores": CompoundScoreList, 
        "total_posts": TotalPostList, 
        "price_change_dollars": PriceChangeDollarsList,
        "price_change_percent": PriceChangePercentList
        }   
    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    #example()
    StockTool()