from twitter_sentiment import TwitterSentiment
from reddit_sentiment import RedditSentiment
import datetime
import csv
from config import *

tw = TwitterSentiment()
rd = RedditSentiment()

#DATES = [datetime.date(2022, 2, 15), datetime.date(2022, 2, 16)]
TODAY = datetime.date.today()

#dates[] = [date1, date2, date3]


def createSuperCSV(threshold):
    #   Creates the superCSV file that determines stocks that should be read every day, parameterized by threshold
    #   If a stock appears more than threshold amount of times over the course of all of the csv files, it is added to the superCSV
    #   The schema of the superCSV is as follows: [stockName,   requiresAdditionalHashtag   tweetWeight] 
    #   Where requiresAdditionalHashtag is a boolean indicating whether or not the stock requires a second stock-related hashtag (ex. a 1-2 character stock, or a common word)  
    #   and tweetWeight is the number of Tweets that are collected in one scrape of the Tweet Collector (NOT IMPLEMENTED)
    #   This algorithm may be imperfect, and may require additional dilligence on behalf of the user to make sure common words are not included ("Ex. HOPE")
        print("Creating Super CSV")
        StockCounts, StockAdditionalHashtags = {}, {}                                              #   StockCounts keeps track of stock names and counts while iterating over all of the stocks
                                                                                                   #   StockAdditionalHashtags keeps track of stock names and whether or not they will need an additional hashtag.

        superCSVPath = open(('/Users/tymar/OneDrive/Documents/Capstone/Twitter/superCSV.csv'), 'w')
        superCSVWriter = csv.writer(superCSVPath)

        scorePath = '/Users/tymar/OneDrive/Documents/Capstone/Reddit/Sentiment Scores/'
        for fileName in os.listdir(scorePath):
            filePath = str(scorePath) + str(fileName)
            with open(filePath, newline='\n') as csvfile:
                csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')
                for line in csvReader:
                    #   Skips top line of each CSV
                    if str(line[0]) ==  'source':
                        continue
                    #   Handles adding instances of stocks to StockCounts
                    if line[2] in StockCounts:                                                      #   An instance has already been processed for this stock
                        StockCounts[line[2]] += int(line[7])
                    else: 
                        StockCounts[line[2]] = int(line[7])
        
        #Orders stocks by StockCount and adds them to superCSV.csv
        superCSVWriter.writerow(["stock", "redditInstances"])
        for stock in reversed(sorted(StockCounts.items(), key=lambda item: item[1])):
            if stock[1] >= threshold:
                superCSVWriter.writerow([str(stock[0]), str(StockCounts[stock[0]])])

        superCSVPath.close()
        print("Finished Creating Super CSV")


if __name__ == '__main__':
    createSuperCSV(3)
    tw.run_for_date(TODAY)                
    rd.run_for_date(TODAY)

            
#       This code gathers sentiment scores for both Twitter and Reddit for a given day, as well as creating the SuperCSV
#       The Twitter Process is quicker, as it must simply run through all of the tweets collected for that day
#       The Reddit Process takes longer, as it must search through all of the top Reddit posts for that day, collect them, and then run sentiment analysis
#       Both of these must be run every day, missing a day with the Twitter Process is okay, because the Tweets are stored
#       If the Reddit Process is missed, a majority of the posts for that day will be unavailable
#       As of now, This may be implemented as a second Windows Service, timed to run at 9PM every night

#       SCHEMA FOR SentimentScore CSV
#       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       `id`                (PRIMARY KEY)
#       `source`            (TWITTER OR REDDIT)
#       `asset`             (STOCK NAME)
#       `score_neg`         (AVERAGE NEGATIVE SCORES FOR DAY)
#       `score_neu`         (AVERAGE NEUTRAL SCORES FOR DAY)
#       `score_pos`         (AVERAGE POSITIVE SCORES FOR DAY)
#       `num_neg`           (NUMBER OF MOSTLY NEGATIVE TWEETS FOR DAY)
#       `num_neu`           (NUMBER OF MOSTLY NEUTRAL TWEETS FOR DAY)
#       `num_pos`           (NUMBER OF MOSTLY POSITIVE TWEETS FOR DAY)
#       `date`              (DATE OF SENTIMENT SCORES)
            
        
