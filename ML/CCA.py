from matplotlib import colors
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys

from pathlib import Path
import dateutil.parser as dparser 
from sklearn.cross_decomposition import CCA

np.set_printoptions(threshold=sys.maxsize)
plt.rcParams.update({'font.size': 15})

def initialCCA(df):
    
    #print(df.head())

    df = df[['reddit_negative_posts', 'reddit_neutral_posts', 'reddit_positive_posts', 'reddit_negative_score', 'reddit_neutral_score', 'reddit_positive_score', 'reddit_comp_score', 'reddit_total_posts', 'one_day_reddit_sentiment_change', 'three_day_reddit_sentiment_change', 'five_day_reddit_sentiment_change', 'one_week_reddit_sentiment_change',  'two_week_reddit_sentiment_change', 'three_week_reddit_sentiment_change', 'one_month_reddit_sentiment_change', 'twitter_negative_posts', 'twitter_neutral_posts', 'twitter_positive_posts', 'twitter_negative_score', 'twitter_neutral_score', 'twitter_positive_score', 'twitter_comp_score', 'twitter_total_posts', 'one_day_twitter_sentiment_change', 'three_day_twitter_sentiment_change', 'five_day_twitter_sentiment_change', 'one_week_twitter_sentiment_change',  'two_week_twitter_sentiment_change', 'three_week_twitter_sentiment_change', 'one_month_twitter_sentiment_change', 'one_day_twitter_prev_posts', 'three_day_twitter_prev_posts', 'five_day_twitter_prev_posts', 'one_week_twitter_prev_posts',  'two_week_twitter_prev_posts', 'three_week_twitter_prev_posts', 'one_month_twitter_prev_posts','adj_close', 'volume', 'one_day_price_change', 'three_day_price_change', 'five_day_price_change', 'one_week_price_change', 'two_week_price_change', 'three_week_price_change', 'one_month_price_change', 'stock', 'date']]
    #df = df[['reddit_comp_score', 'reddit_total_posts', 'one_day_reddit_sentiment_change', 'three_day_reddit_sentiment_change', 'five_day_reddit_sentiment_change', 'one_week_reddit_sentiment_change',  'two_week_reddit_sentiment_change', 'three_week_reddit_sentiment_change', 'one_month_reddit_sentiment_change', 'twitter_comp_score', 'twitter_total_posts', 'one_day_twitter_sentiment_change', 'three_day_twitter_sentiment_change', 'five_day_twitter_sentiment_change', 'one_week_twitter_sentiment_change',  'two_week_twitter_sentiment_change', 'three_week_twitter_sentiment_change', 'one_month_twitter_sentiment_change', 'one_day_twitter_prev_posts', 'three_day_twitter_prev_posts', 'five_day_twitter_prev_posts', 'one_week_twitter_prev_posts',  'two_week_twitter_prev_posts', 'three_week_twitter_prev_posts', 'one_month_twitter_prev_posts', 'adj_close', 'volume', 'one_day_price_change', 'three_day_price_change', 'five_day_price_change', 'one_week_price_change', 'two_week_price_change', 'three_week_price_change', 'one_month_price_change', 'stock', 'date']]
    SentimentDF = df[['twitter_comp_score', 'one_day_twitter_sentiment_change', 'two_day_twitter_sentiment_change', 'three_day_twitter_sentiment_change', 'four_day_twitter_sentiment_change',  'five_day_twitter_sentiment_change', 'three_week_twitter_sentiment_change', 'one_month_twitter_sentiment_change']]
    #SentimentDF = df[['reddit_negative_posts', 'reddit_neutral_posts', 'reddit_positive_posts', 'reddit_negative_score', 'reddit_neutral_score', 'reddit_positive_score', 'reddit_comp_score', 'reddit_total_posts', 'one_day_reddit_sentiment_change', 'three_day_reddit_sentiment_change', 'five_day_reddit_sentiment_change', 'one_week_reddit_sentiment_change',  'two_week_reddit_sentiment_change', 'three_week_reddit_sentiment_change', 'one_month_reddit_sentiment_change', 'twitter_negative_posts', 'twitter_neutral_posts', 'twitter_positive_posts', 'twitter_negative_score', 'twitter_neutral_score', 'twitter_positive_score', 'twitter_comp_score', 'twitter_total_posts', 'one_day_twitter_sentiment_change', 'three_day_twitter_sentiment_change', 'five_day_twitter_sentiment_change', 'one_week_twitter_sentiment_change',  'two_week_twitter_sentiment_change', 'three_week_twitter_sentiment_change', 'one_month_twitter_sentiment_change', 'one_day_twitter_prev_posts', 'three_day_twitter_prev_posts', 'five_day_twitter_prev_posts', 'one_week_twitter_prev_posts',  'two_week_twitter_prev_posts', 'three_week_twitter_prev_posts', 'one_month_twitter_prev_posts']]

    #Standardize variables by subtracting with mean and dividing by standard deviation.
    Sentiment_mc = (SentimentDF-SentimentDF.mean())/(SentimentDF.std())
    #print(Sentiment_mc.head())

    PriceDF = df[['one_day_price_change', 'three_day_price_change', 'five_day_price_change', 'one_week_price_change','two_week_price_change', 'three_week_price_change', 'one_month_price_change']]
    #PriceDF = df[['adj_close', 'volume', 'one_day_price_change']]

    #print(PriceDF.head())

    #Standardize variables by subtracting with mean and dividing by standard deviation.
    Price_mc = (PriceDF-PriceDF.mean())/(PriceDF.std())
    #print(Price_mc.head())


    #Instantiate CCA object and use fit() and transform() functions with the two standardized matrices to perform CCA.
    ca = CCA()
    ca.fit(Sentiment_mc, Price_mc)

    Sentiment_c, Price_c = ca.transform(Sentiment_mc, Price_mc)

    corrOne = np.corrcoef(Sentiment_c[:, 0], Price_c[:, 0])[0, 1]
    print("Correlation of first pair of canonical covariates: " + str(corrOne))

    #Correlation between second pair of covariates
    corrTwo = np.corrcoef(Sentiment_c[:, 1], Price_c[:, 1])[0, 1]
    print("Correlation of second pair of canonical covariates: " + str(corrTwo))

    cc_res = pd.DataFrame({
        "CCSentiment_1" : Sentiment_c[:, 0],
        "CCPrice_1" : Price_c[:, 0],
        "CCSentiment_2" : Sentiment_c[:, 1],
        "CCPrice_2" : Price_c[:, 1],
        "Stock" : df.stock.tolist(),
        "Date" : df.date.tolist()})

    plt.figure(figsize=(10,8))
    sns.scatterplot(x="CCSentiment_1", y="CCPrice_1", hue="Stock", data=cc_res)
    plt.title('First Pair of Canonical Covariate, corr = %.2f' % np.corrcoef(Sentiment_c[:, 0], Price_c[:, 0])[0, 1])
    plt.show()

    ccSentiment_df = pd.DataFrame({
        "CCSentiment_1":Sentiment_c[:, 0],
        "CCSentiment_2":Sentiment_c[:, 1],
        #"Stock":df.stock.astype('category').cat.codes,
        #"Date":df.date.astype('category').cat.codes,

        #"Negative Reddit Posts": Sentiment_mc.reddit_negative_posts, 
        #"Neutral Reddit Posts": Sentiment_mc.reddit_neutral_posts, 
        #"Positive Reddit Posts": Sentiment_mc.reddit_positive_posts,
        #"Negative Reddit Score": Sentiment_mc.reddit_negative_score,
        #"Neutral Reddit Score": Sentiment_mc.reddit_neutral_score,
        #"Positive Reddit Score": Sentiment_mc.reddit_positive_score,
        #"Compound Reddit Score": Sentiment_mc.reddit_comp_score,
        #"Total Reddit Posts": Sentiment_mc.reddit_total_posts,
        #"One Day Reddit Sentiment Change": Sentiment_mc.one_day_reddit_sentiment_change,
        #"Three Day Reddit Sentiment Change": Sentiment_mc.three_day_reddit_sentiment_change,
        #"Five Day Reddit Sentiment Change": Sentiment_mc.five_day_reddit_sentiment_change,
        #"One Week Reddit Sentiment Change": Sentiment_mc.one_week_reddit_sentiment_change,

        #"Negative Twitter Posts": Sentiment_mc.twitter_negative_posts, 
        #"Neutral Twitter Posts": Sentiment_mc.twitter_neutral_posts, 
        #"Positive Twitter Posts": Sentiment_mc.twitter_positive_posts,
        #"Negative Twitter Score": Sentiment_mc.twitter_negative_score,
        #"Neutral Twitter Score": Sentiment_mc.twitter_neutral_score,
        #"Positive Twitter Score": Sentiment_mc.twitter_positive_score,
        "Compound Twitter Score": Sentiment_mc.twitter_comp_score,
        #"Total Twitter Posts": Sentiment_mc.twitter_total_posts,
        "One Day Twitter Sentiment Change": Sentiment_mc.one_day_twitter_sentiment_change,
        "Three Day Twitter Sentiment Change": Sentiment_mc.three_day_twitter_sentiment_change,
        "Five Day Twitter Sentiment Change": Sentiment_mc.five_day_twitter_sentiment_change,
        "One Week Twitter Sentiment Change": Sentiment_mc.one_week_twitter_sentiment_change,
        "Two Week Twitter Sentiment Change": Sentiment_mc.two_week_twitter_sentiment_change,
        "Three Week Twitter Sentiment Change": Sentiment_mc.three_week_twitter_sentiment_change,
        "One Month Twitter Sentiment Change": Sentiment_mc.one_month_twitter_sentiment_change,
        #"One Day Twitter Prev Posts": Sentiment_mc.one_day_twitter_prev_posts,
        #"Three Day Twitter Prev Posts": Sentiment_mc.three_day_twitter_prev_posts,
        #"Five Day Twitter Prev Posts": Sentiment_mc.five_day_twitter_prev_posts,
        #"One Week Twitter Prev Posts": Sentiment_mc.one_week_twitter_prev_posts,
        #"Two Week Twitter Prev Posts": Sentiment_mc.two_week_twitter_prev_posts,
        #"Three Week Twitter Prev Posts": Sentiment_mc.three_week_twitter_prev_posts,
        #"One Month Twitter Prev Posts": Sentiment_mc.one_month_twitter_prev_posts,
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

        #"Adj Close":Price_mc.adj_close,
        #"Volume":Price_mc.volume,
        "One Day Price Change %":Price_mc.one_day_price_change,
        "Three Day Price Change %":Price_mc.three_day_price_change,
        "Five Day Price Change %":Price_mc.five_day_price_change,
        "One Week Price Change %":Price_mc.one_week_price_change,
        "Two Week Price Change %":Price_mc.two_week_price_change,
        "Three Week Price Change %":Price_mc.three_week_price_change,
        "One Month Price Change %":Price_mc.one_month_price_change
        })

    
    corr_Price_df= ccPrice_df.corr(method='pearson')
    #print(corr_Price_df.head())

    plt.figure(figsize=(10,8))
    Price_df_lt = corr_Price_df.where(np.tril(np.ones(corr_Price_df.shape)).astype(bool))
    sns.heatmap(Price_df_lt,cmap="coolwarm",annot=True,fmt='.1g')
    plt.tight_layout()

    ccAll_df = pd.DataFrame({
        "CCSentiment_1":Sentiment_c[:, 0],
        "CCPrice_1":Price_c[:, 1],
        "Stock":df.stock.astype('category').cat.codes,
        "Date":df.date.astype('category').cat.codes,

        #"Negative Reddit Posts": Sentiment_mc.reddit_negative_posts, 
        #"Neutral Reddit Posts": Sentiment_mc.reddit_neutral_posts, 
        #"Positive Reddit Posts": Sentiment_mc.reddit_positive_posts,
        #"Negative Reddit Score": Sentiment_mc.reddit_negative_score,
        #"Neutral Reddit Score": Sentiment_mc.reddit_neutral_score,
        #"Positive Reddit Score": Sentiment_mc.reddit_positive_score,
        #"Compound Reddit Score": Sentiment_mc.reddit_comp_score,
        #"Total Reddit Posts": Sentiment_mc.reddit_total_posts,
        #"One Day Reddit Sentiment Change": Sentiment_mc.one_day_reddit_sentiment_change,
        #"Three Day Reddit Sentiment Change": Sentiment_mc.three_day_reddit_sentiment_change,
        #"Five Day Reddit Sentiment Change": Sentiment_mc.five_day_reddit_sentiment_change,
        #"One Week Reddit Sentiment Change": Sentiment_mc.one_week_reddit_sentiment_change,
        #"Two Week Reddit Sentiment Change": Sentiment_mc.two_week_reddit_sentiment_change,
        #"Three Week Reddit Sentiment Change": Sentiment_mc.three_week_reddit_sentiment_change,
        #"One Month Reddit Sentiment Change": Sentiment_mc.one_month_reddit_sentiment_change,

        #"Negative Twitter Posts": Sentiment_mc.twitter_negative_posts, 
        #"Neutral Twitter Posts": Sentiment_mc.twitter_neutral_posts, 
        #"Positive Twitter Posts": Sentiment_mc.twitter_positive_posts,
        #"Negative Twitter Score": Sentiment_mc.twitter_negative_score,
        #"Neutral Twitter Score": Sentiment_mc.twitter_neutral_score,
        #"Positive Twitter Score": Sentiment_mc.twitter_positive_score,
        "Compound Twitter Score": Sentiment_mc.twitter_comp_score,
        #"Total Twitter Posts": Sentiment_mc.twitter_total_posts,
        "One Day Twitter Sentiment Change": Sentiment_mc.one_day_twitter_sentiment_change,
        "Three Day Twitter Sentiment Change": Sentiment_mc.three_day_twitter_sentiment_change,
        "Five Day Twitter Sentiment Change": Sentiment_mc.five_day_twitter_sentiment_change,
        "One Week Twitter Sentiment Change": Sentiment_mc.one_week_twitter_sentiment_change,
        "Two Week Twitter Sentiment Change": Sentiment_mc.two_week_twitter_sentiment_change,
        "Three Week Twitter Sentiment Change": Sentiment_mc.three_week_twitter_sentiment_change,
        "One Month Twitter Sentiment Change": Sentiment_mc.one_month_twitter_sentiment_change,
        #"One Day Twitter Prev Posts": Sentiment_mc.one_day_twitter_prev_posts,
        #"Three Day Twitter Prev Posts": Sentiment_mc.three_day_twitter_prev_posts,
        #"Five Day Twitter Prev Posts": Sentiment_mc.five_day_twitter_prev_posts,
        #"One Week Twitter Prev Posts": Sentiment_mc.one_week_twitter_prev_posts,
        #"Two Week Twitter Prev Posts": Sentiment_mc.two_week_twitter_prev_posts,
        #"Three Week Twitter Prev Posts": Sentiment_mc.three_week_twitter_prev_posts,
        #"One Month Twitter Prev Posts": Sentiment_mc.one_month_twitter_prev_posts,
        
        #"Adj Close": Price_mc.adj_close,
        "One Day Price Change": Price_mc.one_day_price_change,
        "Three Day Price Change": Price_mc.three_day_price_change,
        "Five Day Price Change": Price_mc.five_day_price_change,
        "One Week Price Change": Price_mc.one_week_price_change,
        "Two Week Price Change": Price_mc.two_week_price_change,
        "Three Week Price Change": Price_mc.three_week_price_change,
        "One Month Price Change": Price_mc.one_month_price_change
        })
    corr_df= ccAll_df.corr(method='pearson')
    #print(corr_Sentiment_df.head())

    plt.figure(figsize=(10,8))
    All_df_lt = corr_df.where(np.tril(np.ones(corr_df.shape)).astype(bool))
    sns.heatmap(All_df_lt,cmap="coolwarm",annot=True,fmt='.1g')
    plt.tight_layout()

    plt.show()
    #Correlation of first pair of canonical covariates. 
    #Uses NumPy’s corrcoef() function to compute correlation.


    # Obtain the rotation matrices
    xrot = ca.x_rotations_
    yrot = ca.y_rotations_

    print("x rotations: " + str(ca.x_rotations_))
    print("y rotations: " + str(ca.y_rotations_))

    # Put them together in a numpy matrix
    xyrot = np.vstack((xrot,yrot))

    print(xyrot.shape)

    nvariables = xyrot.shape[0]
        
    plt.figure(figsize=(10, 10))
    plt.xlim((-1,1))
    plt.ylim((-1,1))

    # Plot an arrow and a text label for each variable
    for var_i in range(nvariables):
      x = xyrot[var_i,0]
      y = xyrot[var_i,1]
          
      plt.arrow(0,0,x,y)
      if(var_i >= SentimentDF.shape[1]):
        plt.text(x,y,PriceDF.columns[var_i-SentimentDF.shape[1]], color='red')
      else:
        plt.text(x,y,SentimentDF.columns[var_i], color='blue')
      
    plt.title('Sentiment/Price Rotations')

    xwts = ca.x_weights_
    ywts = ca.y_weights_

    print("x weights: " + str(ca.x_weights_))
    print("y weights: " + str(ca.y_weights_))

    xywts = np.vstack((xwts,ywts))        

    plt.figure(figsize=(10, 10))
    plt.xlim((-1,1))
    plt.ylim((-1,1))

    # Plot an arrow and a text label for each variable
    for var_i in range(nvariables):
      x = xywts[var_i,0]
      y = xywts[var_i,1]
          
      plt.arrow(0,0,x,y)
      if(var_i >= SentimentDF.shape[1]):
        plt.text(x,y,PriceDF.columns[var_i-SentimentDF.shape[1]], color='red')
      else:
        plt.text(x,y,SentimentDF.columns[var_i], color='blue')

    plt.title('Sentiment/Price Weights')


    xlds = ca.x_loadings_
    ylds = ca.y_loadings_

    print("x loadings: " + str(ca.x_loadings_))
    print("y loadings: " + str(ca.y_loadings_))


    xylds = np.vstack((xlds,ylds))        

    plt.figure(figsize=(10, 10))
    plt.xlim((-1,1))
    plt.ylim((-1,1))


    # Plot an arrow and a text label for each variable
    for var_i in range(nvariables):
      x = xylds[var_i,0]
      y = xylds[var_i,1]
          
      plt.arrow(0,0,x,y)
      if(var_i >= SentimentDF.shape[1]):
        plt.text(x,y,PriceDF.columns[var_i-SentimentDF.shape[1]], color='red')
      else:
        plt.text(x,y,SentimentDF.columns[var_i], color='blue')

    plt.title('Sentiment/Price Loadings')
    plt.show()


    #Metadata dataframe for CCA
    #print(Sentiment_c.shape)
    #print(Price_c.shape)



    #print(cc_res.head())

    
def test(df):
    df = df[df.stock.isin(['MSFT'])]
    
    #print(df.to_string())
    df = df[['date', 'reddit_percent_pos_posts', 'reddit_total_posts', 'twitter_percent_pos_posts', 'twitter_total_posts', 'daily_price_change', 'one_day_price_change']]

    SentimentDF = df[['reddit_percent_pos_posts', 'reddit_total_posts', 'twitter_percent_pos_posts', 'twitter_total_posts']]
    Sentiment_mc = (SentimentDF-SentimentDF.mean())/(SentimentDF.std())
    #print(Sentiment_mc.head())

    PriceDF = df[['daily_price_change', 'one_day_price_change']]
    #PriceDF = df[['adj_close', 'volume', 'one_day_price_change']]

    #print(PriceDF.head())

    #Standardize variables by subtracting with mean and dividing by standard deviation.
    Price_mc = (PriceDF-PriceDF.mean())/(PriceDF.std())
    #print(Price_mc.head())

    #Instantiate CCA object and use fit() and transform() functions with the two standardized matrices to perform CCA.
    ca = CCA()
    ca.fit(Sentiment_mc, Price_mc)

    Sentiment_c, Price_c = ca.transform(Sentiment_mc, Price_mc)

    corrOne = np.corrcoef(Sentiment_c[:, 0], Price_c[:, 0])[0, 1]
    print("Correlation of first pair of canonical covariates: " + str(corrOne))

    #Correlation between second pair of covariates
    corrTwo = np.corrcoef(Sentiment_c[:, 1], Price_c[:, 1])[0, 1]
    print("Correlation of second pair of canonical covariates: " + str(corrTwo))
    
    xwt = ca.x_rotations_
    ywt = ca.y_rotations_
    xywt = np.vstack((xwt,ywt))

    nvariables = xywt.shape[0]

    plt.figure(figsize=(8, 8))

    fig = plt.gcf()
    ax = fig.gca()

    circle1 = plt.Circle((0, 0), 0.6, fill=False)
    circle2 = plt.Circle((0, 0), 1.1, fill=False)
    
    ax.add_patch(circle1)
    ax.add_patch(circle2)

    plt.axhline(0, c = "black")
    plt.axvline(0, c = "black")
    plt.xlim((-1.3,1.3))
    plt.ylim((-1.3,1.3))

    plt.title("Canonical Rotations For MSFT\n Correlation = %.2f" % np.corrcoef(Sentiment_c[:, 0], Price_c[:, 0])[0, 1])

    plt.xlabel("X Rotation")
    plt.ylabel("Y Rotation")

    # Plot an arrow and a text label for each variable
    for var_i in range(nvariables):
      x = xywt[var_i,0]
      y = xywt[var_i,1]

      plt.arrow(0,0,x,y, alpha=(0.5))
      if(var_i >= SentimentDF.shape[1]):
        plt.scatter(x,y, color='red')
        plt.text(x,y,PriceDF.columns[var_i-SentimentDF.shape[1]], color='red')
      else:
        plt.scatter(x,y, color='blue')
        plt.text(x,y,SentimentDF.columns[var_i], color='blue')

    plt.show()

    cc_res = pd.DataFrame({
        "CCSentiment_1" : Sentiment_c[:, 0],
        "CCPrice_1" : Price_c[:, 0],
        "Date" : df.date.tolist()})

    plt.figure(figsize=(10,8))
    sns.scatterplot(x="CCSentiment_1", y="CCPrice_1", hue="Date", data=cc_res)
    plt.title('First Pair of Canonical Covariate, corr = %.2f' % np.corrcoef(Sentiment_c[:, 0], Price_c[:, 0])[0, 1])
    plt.show()


    ccSentiment = pd.DataFrame({
        "CCSentiment_1":Sentiment_c[:, 0],
        "CCSentiment_2":Sentiment_c[:, 1],
        #"Stock":df.stock.astype('category').cat.codes,
        "Date":df.date.astype('category').cat.codes,

        "Total Reddit Posts": Sentiment_mc.reddit_total_posts,
        "Reddit Positive Post %": Sentiment_mc.reddit_percent_pos_posts,

        "Total Twitter Posts": Sentiment_mc.twitter_total_posts,
        "Twitter Positive Post %": Sentiment_mc.twitter_percent_pos_posts
        })
    Sentiment_df= ccSentiment.corr(method='pearson')

    plt.figure(figsize=(10,8))
    plt.title("Correlation Heatmap")
    Sentiment_df_lt = Sentiment_df.where(np.tril(np.ones(Sentiment_df.shape)).astype(bool))
    sns.heatmap(Sentiment_df_lt,cmap="coolwarm",annot=True,fmt='.1g')
    plt.tight_layout()

    plt.show()


    ccAll_df = pd.DataFrame({
        #"CCSentiment_1":Sentiment_c[:, 0],
        #"CCPrice_1":Price_c[:, 0],
        #"Stock":df.stock.astype('category').cat.codes,
        "Date":df.date.astype('category').cat.codes,

        "Total Reddit Posts": Sentiment_mc.reddit_total_posts,
        "Reddit Positive Post %": Sentiment_mc.reddit_percent_pos_posts,

        "Total Twitter Posts": Sentiment_mc.twitter_total_posts,
        "Twitter Positive Post %": Sentiment_mc.twitter_percent_pos_posts,
        
        #"Adj Close": Price_mc.adj_close,
        "Daily Price Change": Price_mc.daily_price_change,
        "One Day Price Change": Price_mc.one_day_price_change
        })
    corr_df= ccAll_df.corr(method='pearson')
    #print(corr_Sentiment_df.head())

    plt.figure(figsize=(10,8))
    plt.title("Correlation Heatmap")
    All_df_lt = corr_df.where(np.tril(np.ones(corr_df.shape)).astype(bool))
    sns.heatmap(All_df_lt,cmap="coolwarm",annot=True,fmt='.1g')
    plt.tight_layout()

    plt.show()



def readTop50DF():    
    return pd.read_csv('top50ReducedDF.csv')
    #return pd.read_csv('top50DF.csv')

if __name__ == '__main__':
    #createTop50DF()
    df = readTop50DF()
    #StockTool(df)
    test(df)

