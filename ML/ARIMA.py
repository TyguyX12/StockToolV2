import pandas as pd
from datetime import  datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults 
from statsmodels.tsa.seasonal import seasonal_decompose
from pmdarima.arima import auto_arima

import csv

plt.rcParams.update({'font.size': 13})

df = []
Top50Stocks = ['AAPL', 'BTC', 'TSLA', 'GME', 'TWTR', 'FB', 'AMZN', 'NFLX', 'NVDA', 'AMD', 'NIO', 'BABA', 'PLTR', 'MSFT', 'ROKU', 'PYPL', 'DKNG', 'UPST', 'MRNA', 'SQ', 'GOOGL', 'TLRY', 'GOOG', 'WMT', 'TGT', 'PTON', 'TDOC', 'XOM', 'UBER', 'JPM', 'BAC', 'SE', 'CVX', 'ZM', 'BYND', 'SBUX', 'OXY', 'ABNB', 'INTC', 'HYMC', 'BBBY', 'MU', 'TWLO', 'LYFT', 'LMT', 'FUBO', 'GM', 'JD', 'ETSY']

def readTop50DF():
    global df
    df = pd.read_csv('top50ReducedDF.csv')

def getStockDF(stock, source):
    global df
    stockDF = df[df['stock'] == stock]
    stockDF = stockDF[['stock', 'date', 'reddit_percent_pos_posts', 'reddit_total_posts', 'twitter_percent_pos_posts', 'twitter_total_posts', 'daily_price_change', 'one_day_price_change']]

    stockDF = stockDF.sort_values(by=['date'])
    stockDF.set_index("date", inplace=True)
    dfSchema  = {"date": [],
        "stock": [],
        "daily_pos_percent": [],  
        "two_day_agg_percent_pos": [],  
        "three_day_agg_percent_pos": [],  
        "four_day_agg_percent_pos": [],
        "five_day_agg_percent_pos": [],
        "six_day_agg_percent_pos": [],
        "daily_price_change": [],
        "one_day_price_change": [],
        "daily_posts": []
       }
    #print(stockDF.to_string())

    newDF = pd.DataFrame(dfSchema)
    totalPosts = 0
   
    for date, row in stockDF.iterrows():
        try:
            #print(date, row['stock'])
            date = datetime.strptime(date, '%Y-%m-%d').date()
            oneDayPrevDate = str(date - timedelta(days=1))
            twoDayPrevDate = str(date - timedelta(days=2))
            threeDayPrevDate = str(date - timedelta(days=3))
            fourDayPrevDate = str(date - timedelta(days=4))
            fiveDayPrevDate = str(date - timedelta(days=5))
            dailyPosts = None
            if source == "twitter":
                totalPosts = totalPosts + int(row["twitter_total_posts"])
                dailyPosts = int(row["twitter_total_posts"])
                percentPosPost = row["twitter_percent_pos_posts"]
                oneDayPrevPosPercent = stockDF.loc[oneDayPrevDate, "twitter_percent_pos_posts"]
                twoDayPrevPosPercent = stockDF.loc[twoDayPrevDate, "twitter_percent_pos_posts"]
                threeDayPrevPosPercent = stockDF.loc[threeDayPrevDate, "twitter_percent_pos_posts"]
                fourDayPrevPosPercent = stockDF.loc[fourDayPrevDate, "twitter_percent_pos_posts"]
                fiveDayPrevPosPercent = stockDF.loc[fiveDayPrevDate, "twitter_percent_pos_posts"]
            if source == "reddit":
                totalPosts = totalPosts + int(row["reddit_total_posts"])
                dailyPosts = int(row["reddit_total_posts"])
                percentPosPost = row["reddit_percent_pos_posts"]
                oneDayPrevPosPercent = stockDF.loc[oneDayPrevDate, "reddit_percent_pos_posts"]
                twoDayPrevPosPercent = stockDF.loc[twoDayPrevDate, "reddit_percent_pos_posts"]
                threeDayPrevPosPercent = stockDF.loc[threeDayPrevDate, "reddit_percent_pos_posts"]
                fourDayPrevPosPercent = stockDF.loc[fourDayPrevDate, "reddit_percent_pos_posts"]
                fiveDayPrevPosPercent = stockDF.loc[fiveDayPrevDate, "reddit_percent_pos_posts"]
            aggSentimentPercentTwoDay = (percentPosPost + oneDayPrevPosPercent) / 2
            aggSentimentPercentThreeDay = (percentPosPost + oneDayPrevPosPercent + twoDayPrevPosPercent) / 3
            aggSentimentPercentFourDay = (percentPosPost + oneDayPrevPosPercent + twoDayPrevPosPercent + threeDayPrevPosPercent) / 4
            aggSentimentPercentFiveDay = (percentPosPost + oneDayPrevPosPercent + twoDayPrevPosPercent + threeDayPrevPosPercent + fourDayPrevPosPercent) / 5
            aggSentimentPercentSixDay = (percentPosPost + oneDayPrevPosPercent + twoDayPrevPosPercent + threeDayPrevPosPercent + fiveDayPrevPosPercent) / 6
            newDF.loc[len(newDF.index)] = [date, stock, percentPosPost, aggSentimentPercentTwoDay, aggSentimentPercentThreeDay, aggSentimentPercentFourDay, aggSentimentPercentFiveDay, aggSentimentPercentSixDay, row["daily_price_change"], row["one_day_price_change"], dailyPosts] 
        except:
            continue

    newDF['date']=pd.to_datetime(newDF['date'])
    newDF.set_index("date", inplace=True)

    #print(newDF)     
    
    newDF = newDF.dropna()

    return newDF, totalPosts


#   Tests that data is stationary
def test_stationarity(ts):
    #Determing rolling statistics
    #print(ts)
    rolmean = ts.rolling(7).mean()
    rolstd = ts.rolling(7).std()
    #Plot rolling statistics:
    plt.plot(ts, color='blue',label='Original')
    plt.plot(rolmean, color='red', label='Rolling Mean')
    plt.plot(rolstd, color='black', label = 'Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show()
    #Perform Dickey-Fuller test:
    print("Results of Dickey Fuller Test:")
    dftest = adfuller(ts, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
        print(dfoutput)

#   Tests data for trends, residuals, etc.
def decompose(ts):
    #ts.index = pd.DatetimeIndex(ts.index).to_period('D')
    decomposition = seasonal_decompose(ts, period=7)
    
    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid 

    plt.subplot(411)
    plt.plot(ts, label='Original')
    plt.legend(loc='best')
    plt.subplot(412)
    plt.plot(trend, label='Trend')
    plt.legend(loc='best')
    plt.subplot(413)
    plt.plot(seasonal, label='Seasonality')
    plt.legend(loc='best')
    plt.subplot(414)
    plt.plot(residual, label='Residuals')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()


def ACF_PACF(ts):
    ts_diff = ts - ts.shift()
    ts_diff = ts_diff.dropna()

    lag_acf = acf(ts_diff, nlags=7)
    lag_pacf = pacf(ts_diff, nlags=7, method="ols")

        #Plot ACF
    plt.subplot(121)
    plt.plot(lag_acf) 
    plt.axhline(y=0, linestyle='--', color = 'gray')
    plt.axhline(y=-1.96/np.sqrt(len(ts_diff)),linestyle='--', color='gray')
    plt.axhline(y=1.96/np.sqrt(len(ts_diff)),linestyle='--', color='gray')
    plt.title('Autocorrelation Function')

        #Plot PACF
    plt.subplot(122)
    plt.plot(lag_pacf) 
    plt.axhline(y=0, linestyle='--', color = 'gray')
    plt.axhline(y=-1.96/np.sqrt(len(ts_diff)),linestyle='--', color='gray')
    plt.axhline(y=1.96/np.sqrt(len(ts_diff)),linestyle='--',  color='gray')
    plt.title('Partial Autocorrelation Function')
    plt.tight_layout()
    plt.show()


def write_ARIMA(source, p, d, q):
    filePath=("ARIMA_Results\Top50ARIMA"+source+"("+str(p)+"," + str(d) + "," + str(q)+").csv")

    with open(filePath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Stock', '# of Posts', 'RSME (No Sentiment)', 'RSME (W/ Sentiment)', 'Accuracy (No Sentiment)', 'Accuracy (W/ Sentiment)'])
            csvfile.close()

    for stock in Top50Stocks:
        stockDF, totalPosts = getStockDF(stock, source)
        #ts = {}
        ts = stockDF['daily_price_change']
        
        exog = stockDF['daily_pos_percent'].dropna()
        
        for date in exog.index:
            if exog.loc[date] == 0:
                exog = exog.drop(date)

        #plt.title("Numposts")
        #plt.plot(numposts)
        #plt.figure()

        #plt.title("Sentiment")
        #plt.plot(exog)
        #plt.figure()
        
        #exog = stockDF[['daily_pos_percent', 'twitter_total_posts']]
        
        #ts_log = np.log(ts)         # DOES NOT WORK WITH NEGATIVES
        #ts_log = ts_log.dropna()

        ts_diff = ts - ts.shift()
        ts_diff = ts_diff.dropna()

        exog = exog - exog.shift()
        exog = exog.dropna()

        decomposition = seasonal_decompose(ts, period=7)
        ts_decompose = decomposition.resid 
        ts_decompose.dropna(inplace=True)

        try:
            decomposition = seasonal_decompose(exog, period=7)
            #exog_decompose = decomposition.resid 
            #exog_decompose.dropna(inplace=True)
        except:
            continue
        
        for item in ts_decompose.index:
            if item not in exog.index:
                ts_decompose = ts_decompose.drop(item)
        for item in ts.index:
            if item not in ts_decompose.index:
                ts = ts.drop(item)
        for item in exog.index:
            if item not in ts_decompose.index:
                exog = exog.drop(item)

        #test_stationarity(ts)
        #test_stationarity(ts_decompose)
        #decompose(exog)
        #ACF_PACF(ts_decompose)

        try:
            RMSEns, RMSEws, Accns, Accws = ARIMA_TEST(ts, ts_decompose, exog, p, d, q) # 3, 0, 4 working best for daily sampling
        except:
            continue
        with open(filePath, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            newRow = [stock, totalPosts, RMSEns, RMSEws, Accns, Accws]
            #print(newRow)
            writer.writerow(newRow)
            csvfile.close()
    

def ARIMA_TEST(tsOrig, ts, exog, p, d, q):
    ts_diff = ts - ts.shift()
    ts_diff = ts_diff.dropna()

    
    #tsOrig = tsOrig.resample('W').mean() 
    #ts = ts.resample('W').mean() 
    #ts_diff = ts_diff.resample('W').mean() 
    #exog = exog.resample('W').mean() 

    #ARIMA MODEL
    #model = ARIMA(ts, exog=exog, order=(p,d,q))
    model = ARIMA(ts, order=(p,d,q), missing="drop")
    modelExog = ARIMA(ts, exog=exog, order=(p,d,q), missing="drop")
    
    try:
        results_ARIMA = model.fit()
        results_ARIMA_exog = modelExog.fit()
    except:
        return

    #   Predictions

    predictions_ARIMA_diff = pd.Series(results_ARIMA.fittedvalues, copy=True)
    predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()
    predictions_ARIMA = pd.Series(tsOrig.iloc[0], index=tsOrig.index)
    predictions_ARIMA = predictions_ARIMA.add(predictions_ARIMA_diff_cumsum, fill_value=0)

    predictions_ARIMA_exog_diff = pd.Series(results_ARIMA_exog.fittedvalues, copy=True)
    predictions_ARIMA_exog_diff_cumsum = predictions_ARIMA_exog_diff.cumsum()
    predictions_ARIMA_exog = pd.Series(tsOrig.iloc[0], index=tsOrig.index)
    predictions_ARIMA_exog = predictions_ARIMA_exog.add(predictions_ARIMA_exog_diff_cumsum, fill_value=0)

    for item in tsOrig.index:
        if item not in predictions_ARIMA.index:
            del tsOrig[item]

    RMSE = np.sqrt(sum((predictions_ARIMA-tsOrig)**2)/len(tsOrig))
    RMSEexog = np.sqrt(sum((predictions_ARIMA_exog-tsOrig)**2)/len(tsOrig))

    accuracy = getAccuracy(tsOrig, predictions_ARIMA)
    accuracyExog = getAccuracy(tsOrig, predictions_ARIMA_exog)

    return(RMSE, RMSEexog, accuracy, accuracyExog)

def compare(filePath, newFilePath):
    totalStocks = 0
    RMSEWins, RMSELosses, RMSETies, AccWins, AccTies, AccLosses = 0, 0, 0, 0, 0, 0
    AvgRMSEns, AvgRMSEws, AvgAccns, AvgAccws = 0, 0, 0, 0
    
    with open(newFilePath, 'w', newline='') as newFile:
        with open(filePath, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if row[0] != 'Stock':
                    RMSEns = float(row[2])
                    RMSEws = float(row[3])
                    Accns = float(row[4])
                    Accws = float(row[5])
                    print("RMSE: " + str(RMSEns) + " | " + str(RMSEws))
                    print("Acc: " + str(Accns) + " | " + str(Accws))
                    if RMSEns > RMSEws:
                        RMSELosses = RMSELosses + 1
                    if RMSEns < RMSEws:
                        RMSEWins = RMSEWins + 1
                    if RMSEns == RMSEws:
                        RMSETies = RMSETies + 1

                    if Accns > Accws:
                        AccLosses = AccLosses + 1
                    if Accns < Accws:
                        AccWins = AccWins + 1
                    if Accns == Accws:
                        AccTies = AccTies + 1

                    AvgRMSEns = AvgRMSEns + RMSEns
                    print("T: " + str(AvgAccns))
                    AvgRMSEws = AvgRMSEws + RMSEws
                    AvgAccns = AvgAccns + Accns
                    AvgAccws = AvgAccws + Accws

                    totalStocks = totalStocks + 1
            print(totalStocks)
            print(AvgAccns)
            AvgRMSEns = AvgRMSEns / totalStocks
            AvgRMSEws = AvgRMSEws / totalStocks
            AvgAccns = AvgAccns / totalStocks
            AvgAccws = AvgAccws / totalStocks
        csvfile.close()
        

        Results = (
            "Stocks Observed: " + str(totalStocks) +
            "\nLower RMSE w/out Sentiment: " + str(RMSELosses) + 
            "\nLower RMSE w/ Sentiment: " + str(RMSEWins) + 
            "\nRMSE Ties: " + str(RMSETies) + 
            "\nAverage RMSE w/out Sentiment: " + str(AvgRMSEns) + 
            "\nAverage RMSE w/ Sentiment " + str(AvgRMSEws) + 
            "\nHigher Accuracy w/out Sentiment: " + str(AccLosses) + 
            "\nHigher Accuracy w/ Sentiment: " + str(AccWins) + 
            "\nAccuracy Ties: " + str(AccTies) +
            "\nAverage Accuracy w/out Sentiment: " + str(AvgAccns) + 
            "\nAverage Accuracy w/ Sentiment " +  str(AvgAccws)
            )

        print(Results)
        newFile.write(Results)
    newFile.close()

def plot_ARIMA(stock, tsOrig, ts, exog, p, d, q):

    ts_diff = ts - ts.shift()
    ts_diff = ts_diff.dropna()

    
    #tsOrig = tsOrig.resample('W').mean() 
    #ts = ts.resample('W').mean() 
    #ts_diff = ts_diff.resample('W').mean() 
    #exog = exog.resample('W').mean() 

    print(ts.to_string())
    print(exog.to_string())

    #ARIMA MODEL
    #model = ARIMA(ts, exog=exog, order=(p,d,q))
    model = ARIMA(ts, order=(p,d,q), missing="drop")
    modelExog = ARIMA(ts, exog=exog, order=(p,d,q), missing="drop")

    results_ARIMA = model.fit()
    fittedValues = results_ARIMA.fittedvalues[1:]
    results_ARIMA_exog = modelExog.fit()
    fittedValuesExog = results_ARIMA_exog.fittedvalues[1:]

    plt.axhline(0, alpha = 0.25)
    plt.plot(ts_diff, color="blue", label = "Expected Value")
    plt.plot(results_ARIMA.fittedvalues, color='orange', label = "Without sentiment")
    plt.plot(results_ARIMA_exog.fittedvalues, color='green', label = "With sentiment")
    
    # GATHER CURRENT SENTIMENT
    #currentSentiment()
    # FORECAST NEXT
    a = results_ARIMA_exog.forecast(1, exog = [0.2])

    print(str(a))
    
    plt.legend()

    RSS = sum((fittedValues-ts_diff)**2)
    RSSExog = sum((fittedValuesExog-ts_diff)**2)
    label = ('Stock: ' + stock + '\nRSS (without sentiment): %.4f'%RSS + '\nRSS (with sentiment): %.4f'%RSSExog )
    plt.title(label)

    #print(results_ARIMA.summary())

    plt.figure()

    #   Predictions

    predictions_ARIMA_diff = pd.Series(results_ARIMA.fittedvalues, copy=True)
    predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()
    predictions_ARIMA = pd.Series(tsOrig.iloc[0], index=tsOrig.index)
    predictions_ARIMA = predictions_ARIMA.add(predictions_ARIMA_diff_cumsum, fill_value=0)

    predictions_ARIMA_exog_diff = pd.Series(results_ARIMA_exog.fittedvalues, copy=True)
    predictions_ARIMA_exog_diff_cumsum = predictions_ARIMA_exog_diff.cumsum()
    predictions_ARIMA_exog = pd.Series(tsOrig.iloc[0], index=tsOrig.index)
    predictions_ARIMA_exog = predictions_ARIMA_exog.add(predictions_ARIMA_exog_diff_cumsum, fill_value=0)

    for item in tsOrig.index:
        if item not in predictions_ARIMA.index:
            del tsOrig[item]

    plt.axhline(0, alpha = 0.25)
    plt.plot(tsOrig, color="blue", label = "True Price")
    plt.plot(predictions_ARIMA, color="orange", label = "Predicted Price Change (Without Sentiment)")
    plt.plot(predictions_ARIMA_exog, color="green", label = "Predicted Price Change (With Sentiment)")
    plt.legend()

    RMSE = np.sqrt(sum((predictions_ARIMA-tsOrig)**2)/len(tsOrig))
    RMSEexog = np.sqrt(sum((predictions_ARIMA_exog-tsOrig)**2)/len(tsOrig))
    label = ('Stock: ' + stock + '\nRMSE (Without sentiment): %.4f'%RMSE + '\nRMSE (With sentiment): %.4f'%RMSEexog)
    plt.title(label)
    plt.ylabel("Price change %")
    plt.xlabel("Date")
    plt.figure()

    accuracy = getAccuracy(tsOrig, predictions_ARIMA)
    accuracyExog = getAccuracy(tsOrig, predictions_ARIMA_exog)
 
    plt.ylim(0, 1)
    plt.ylabel("Accuracy")
    plt.bar(x="No Sentiment", height=accuracy, color="orange")
    plt.bar(x="With Sentiment", height=accuracyExog, color="green")
    label = ('Stock: ' + stock + '\nAccuracy (without sentiment): %.4f'%accuracy + '\nAccuracy (with sentiment): %.4f'%accuracyExog)
    plt.title(label)
    plt.show()

def getAccuracy(tsOrig, ts):
    correct = 0
    total = 0
    for item in tsOrig.index:
        if item not in ts.index:
            del tsOrig[item]
        if tsOrig[item] > 0 and ts[item] > 0:
            correct = correct + 1
        if tsOrig[item] < 0 and ts[item] < 0:
            correct = correct + 1
        total = total + 1

    accuracy = correct / total
    
    return accuracy
     
def quick_ARIMA(stock, ts, exog, p, d, q):

    model = ARIMA(ts, exog=exog, order=(p,d,q), missing="drop")

    results_ARIMA = model.fit()
   
    # LATEST DATE
    #print(exog.index[-1])

    # FORECAST NEXT
    a = results_ARIMA.forecast(1, exog = exog[-1])

    # PREDICTED VALUE
    #print(a.values[0])

def autoARIMA(stock, endog, exog):
    endog = endog.to_frame()
    exog = exog.to_frame()
    print(endog)
    print(exog)
    model = auto_arima(endog, X=exog, start_p=1, start_q=1,
        max_p=5, max_q=5,
        m=7,             
        stationary=True,
        seasonal=True,   
        start_P=0, 
        trace=True,
        error_action='ignore',  
        suppress_warnings=True, 
        stepwise=False)


def find_ARIMA(tsOrig, ts, exog):
    bestRMSENS = 100000
    bestRMSEWS = 100000
    bestAccNS = 0
    bestAccWS = 0
    bestPDQNS = None
    bestPDQWS = None

    for p in range(0,5):
        for q in range(0,5):
            ts_diff = ts - ts.shift()
            ts_diff = ts_diff.dropna()

            model = ARIMA(ts, order=(p,0,q), missing="drop")
            modelExog = ARIMA(ts, exog=exog, order=(p,0,q), missing="drop")

            results_ARIMA = model.fit()
            results_ARIMA_exog = modelExog.fit()

            predictions_ARIMA_diff = pd.Series(results_ARIMA.fittedvalues, copy=True)
            predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()
            predictions_ARIMA = pd.Series(tsOrig.iloc[0], index=tsOrig.index)
            predictions_ARIMA = predictions_ARIMA.add(predictions_ARIMA_diff_cumsum, fill_value=0)

            predictions_ARIMA_exog_diff = pd.Series(results_ARIMA_exog.fittedvalues, copy=True)
            predictions_ARIMA_exog_diff_cumsum = predictions_ARIMA_exog_diff.cumsum()
            predictions_ARIMA_exog = pd.Series(tsOrig.iloc[0], index=tsOrig.index)
            predictions_ARIMA_exog = predictions_ARIMA_exog.add(predictions_ARIMA_exog_diff_cumsum, fill_value=0)

            for item in tsOrig.index:
                if item not in predictions_ARIMA.index:
                    del tsOrig[item]

            RMSE = np.sqrt(sum((predictions_ARIMA-tsOrig)**2)/len(tsOrig))
            RMSEexog = np.sqrt(sum((predictions_ARIMA_exog-tsOrig)**2)/len(tsOrig))

            accuracy = getAccuracy(tsOrig, predictions_ARIMA)      
            accuracyExog = getAccuracy(tsOrig, predictions_ARIMA_exog)

            if RMSE < bestRMSENS:
                bestRMSENS = RMSE
                bestPDQNS = (p, 0, q)
            
            if RMSEexog < bestRMSEWS:
                bestRMSEWS = RMSEexog
                bestPDQWS = (p, 0, q)

            if accuracy > bestAccNS:
                bestAccNS = accuracy

            if accuracyExog > bestAccWS:
                bestAccWS = accuracyExog

    print("Best (p,d,q) w/out sentiment = " + str(bestPDQNS) + "\nBest (p,d,q) with sentiment = " + str(bestPDQWS))
    print("Best RMSE w/out sentiment = " + str(bestRMSENS) + "\nBest RMSE with sentiment = " + str(bestRMSEWS))
    print("Best Acc w/out sentiment = " + str(bestAccNS) + "\nBest Acc with sentiment = " + str(bestAccWS))
 

def ARIMATop50(source):
    for p in range(2,4):
        for q in range(0,4):
            filePath = "ARIMA_Results\Top50ARIMA" +source + "(" +str(p) +",0," + str(q) + ").csv"
            newFilePath = "ARIMA_Results\Summary\Top50ARIMA" +source + "(" +str(p) +",0," + str(q) + ")_SUMMARY.txt"
            write_ARIMA(source, p, 0, q)
            compare(filePath, newFilePath)          

if __name__ == '__main__':
    readTop50DF()
    #ARIMATop50("twitter")
    
    stockDF, totalPosts = getStockDF("NVDA", "twitter")
    #   [daily_price_change, one_day_price_change]
    ts = stockDF['one_day_price_change']
    #   [daily_posts, daily_pos_percent]
    exog = stockDF['daily_pos_percent'].dropna()

    decomposition = seasonal_decompose(ts, period=7)
    ts_decompose = decomposition.resid 
    ts_decompose.dropna(inplace=True)

    decomposition = seasonal_decompose(exog, period=7)
    exog_decompose = decomposition.resid 
    exog_decompose.dropna(inplace=True)

    for item in ts.index:
        if item not in ts_decompose.index:
            ts = ts.drop(item)
    for item in exog.index:
        if item not in ts_decompose.index:
            exog = exog.drop(item)
    for item in exog_decompose.index:
        if item not in ts_decompose.index:
            exog_decompose = exog_decompose.drop(item)

    
    find_ARIMA(ts, ts_decompose, exog_decompose)
    #autoARIMA("AAPL", ts_decompose, exog_decompose)

   # quick_ARIMA("AAPL", ts, exog, 3, 0, 3)
    
    
    
        

