import mysql.connector as mysql
import datetime
from datetime import timedelta

from statsmodels.tsa.arima.model import ARIMA 
from statsmodels.tsa.seasonal import seasonal_decompose

import numpy as np
import pandas as pd
import mysql.connector as mysql
import yfinance as yf

sentimentData = {"reddit": {}, "twitter": {}}
yfData = None

HOST = "35.222.225.4" 
DB = "Sentiment_DB"
USER = "root"
PASSWORD = "sentimentdata"

conn = mysql.connect(user=USER, password=PASSWORD, host=HOST, database=DB)

def getSentimentDataFromDB():
    global sentimentData

    sql = """SELECT * FROM sentimentdata"""
    cursor = conn.cursor(buffered=True)
    cursor.execute(sql)
    DBSentiment = cursor.fetchall()

    for item in DBSentiment:
        source = str(item[1])
        date = str(item[2])
        stock = str(item[3])
        if stock in sentimentData[source]:                                                     
            sentimentData[source][stock][date] = item[4:]
        else:
            sentimentData[source][stock] = {date: item[4:]} 

    return sentimentData

    
def getSentimentDf(asset, sentimentSource):
    global sentimentData
    stock = asset[:-3]
    stockSentimentData = sentimentData[sentimentSource][stock]

    #   BUG FIX FOR TUPLES WITH "-0.0"  FLOAT VALUES
    for date in stockSentimentData:
        stockSentimentData[date] = list(stockSentimentData[date])
        for index in range(len(stockSentimentData[date])):
            if stockSentimentData[date][index] == 0:
                stockSentimentData[date][index] = 0
            
    return stockSentimentData

def getLatestSentiment(asset, source):
    global sentimentData
    stock = asset[:-3]
    stockSentimentData = sentimentData[source][stock]
    latestDate = list(stockSentimentData)[-1]
    latestSentiment = sentimentData[source][stock][latestDate]

    return latestDate, latestSentiment


def getStockData(source, stock):
    startDate = datetime.datetime(2022, 1, 1)
    endDate = datetime.datetime.today()
    PosPosts, TotPosts = getPosPosts(source, stock)

    PriceData = getPriceData(stock, startDate)
    
    dfSchema = {"date": [],
        "stock": [],
        "percent_pos_posts": [],
        "total_posts": [],
        "one_day_price_change": [], 
       }
  
    df = pd.DataFrame(dfSchema)
  
    delta = endDate - startDate  # as timedelta
    days = [startDate + timedelta(days=i) for i in range(delta.days + 1)]

    for date_time in days:
        date = str(date_time.date())
        percent_pos_posts, total_posts = None, None
        try:           
            percent_pos_posts = float(PosPosts[date])
            total_posts = float(TotPosts[date])
        except:
            pass

        one_day_price_change = None
        try:
            one_day_price_change = float(PriceData[date])
        except:
            pass
                
        df.loc[len(df.index)] = [date, stock, percent_pos_posts, total_posts, one_day_price_change] 
  
    return df

def getPriceData(stock, startDate):
    global yfData
    PriceData = {}
    endDate = datetime.datetime.today()
    #   Converts the oldest date in sentiment dictionary to a datetime in order to use time delta to subtract dates.
    yfData = yf.download(stock, start=startDate, end=endDate)
    delta = endDate - startDate  # as timedelta
    days = [startDate + timedelta(days=i) for i in range(delta.days + 1)]
    
    for date_time in days:
        date = date_time.date()
        
        oneDayPriceChange = getPriceChangeData(date)
        date = str(date)   
        if oneDayPriceChange:
            PriceData[date] = oneDayPriceChange

    return PriceData


def getPriceChangeData(date):

    oneDayPrevDate = date - timedelta(days=1)
    oneDayAfterDate = date + timedelta(days=1)

    currentPrice = None
    prevPrice = None

    fridayPrice = None
    mondayPrice = None
    counter = 0

    if date.weekday() == 5: #  Saturday
        while fridayPrice is None:
            if counter > 5:
                return None
            try: 
                fridayPrice = float(yfData["Adj Close"][str(oneDayPrevDate)]) 
            except:
                oneDayPrevDate = oneDayPrevDate - timedelta(days = 1)
                counter = counter + 1
    
        counter = 0
        while mondayPrice is None:
            oneDayAfterDate = oneDayAfterDate + timedelta(days = 1)
            if counter > 5:
                return None
            try: 
                mondayPrice = float(yfData["Adj Close"][str(oneDayAfterDate)])
                
            except:
                counter = counter + 1

        saturdayPrice = (fridayPrice + mondayPrice) / 2
        prevPrice = fridayPrice
        currentPrice = saturdayPrice

    if date.weekday() == 6: #  Sunday
        while fridayPrice is None:
            oneDayPrevDate = oneDayPrevDate - timedelta(days = 1)
            if counter > 5:
                return None
            try: 
                fridayPrice = float(yfData["Adj Close"][str(oneDayPrevDate)])
            except:       
                counter = counter + 1
    
        counter = 0
        while mondayPrice is None:
            if counter > 5:
                return None
            try: 
                mondayPrice = float(yfData["Adj Close"][str(oneDayAfterDate)])
            except:
                oneDayAfterDate = oneDayAfterDate + timedelta(days = 1)
                counter = counter + 1       

        saturdayPrice = (fridayPrice + mondayPrice) / 2
        sundayPrice = (saturdayPrice + mondayPrice) / 2
        prevPrice = saturdayPrice
        currentPrice = sundayPrice
    
    else:
        while(currentPrice == None):
            if counter > 5: 
                return None
            try:
                currentPrice = float(yfData["Adj Close"][str(date)])
            except Exception: # Holiday
                date = date - timedelta(days=1)
                oneDayPrevDate = date - timedelta(days=1)
                counter = counter + 1
            
        counter = 0
        while(prevPrice == None):
            if counter > 5: 
                return None
            try:
                prevPrice = float(yfData["Adj Close"][str(oneDayPrevDate)])
            except Exception: # Holiday
                oneDayPrevDate = oneDayPrevDate - timedelta(days=1)
                counter = counter + 1
            
    oneDayPriceChange = 100*((currentPrice-prevPrice)/currentPrice)

    return oneDayPriceChange

def getPosPosts(source, stock):
    global sentimentData
    PosPosts = {}
    TotPosts = {}
    for date in sentimentData[source][stock]:            
        negativePosts = int(sentimentData[source][stock][date][4])
        positivePosts = int(sentimentData[source][stock][date][6])
        percentPosPosts = 0
        if (negativePosts+positivePosts != 0):
            percentPosPosts =  positivePosts / (negativePosts + positivePosts)
        PosPosts[date] = percentPosPosts
        TotPosts[date] = percentPosPosts
            
    return PosPosts, TotPosts


def singleStockARIMA(source, stock):
    stock = stock[:-3]
    df = getStockData(source, stock)

    df['date']=pd.to_datetime(df['date'])
    df = df.sort_values(by=['date'])
    df.set_index("date", inplace=True)
    
    newDF = df[["one_day_price_change", "percent_pos_posts", "total_posts"]]
    newDF = newDF.dropna()

    PriceTS = newDF["one_day_price_change"].astype(np.float64)
    SentimentTS, order = None, None
    if source == "reddit":
        SentimentTS = newDF["total_posts"].astype(np.float64)
        order = (3,0,5)
    else:
        SentimentTS = newDF["percent_pos_posts"].astype(np.float64)
        order = (3,0,0)

    decomposition = seasonal_decompose(PriceTS, period=7)
    decomposeTS = decomposition.resid 
    decomposeTS.dropna(inplace=True)

    for item in SentimentTS.index:
            if item not in decomposeTS.index:
                SentimentTS = SentimentTS.drop(item)

    model = ARIMA(decomposeTS, exog=SentimentTS, order=order, missing="drop")
    results_ARIMA = model.fit()

    # FORECAST NEXT
    prediction = results_ARIMA.forecast(1, exog = SentimentTS[-1]).values[0]

    prediction = ("%.2f" % prediction)

    if float(prediction) > 0:
        predictionColor = "green"
        prediction = "+" + prediction

    elif float(prediction) < 0:
        predictionColor = "red"
    else:
        predictionColor = "red"

    prediction = prediction + "%"

    return prediction, predictionColor

sentimentData = getSentimentDataFromDB()
