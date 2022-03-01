from config import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import csv
import datetime


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
        SortedCounts, CumulativeScores = self.runSentimentAnalysisForDate(date)
        self.create_sentiment_csv(CumulativeScores, SortedCounts, date)

    
    def runSentimentAnalysisForDate(self, date):
        TweetTexts, TweetCounts, ProcessedTweetCounts, TweetScores, CumulativeScores = {}, {}, {}, {}, {}

        tweetPath = '/Users/tymar/OneDrive/Documents/Capstone/Twitter/Tweets/Tweets-' + str(date) + '.csv'

        # adding custom words from config
        self.vader.lexicon.update(new_words)
                
        print("Starting Sentiment Analysis for date: " + str(date))
        with open(tweetPath, newline='\n') as tweetCSV:
    
            tweetReader = csv.reader(_.replace('\x00', '') for _ in tweetCSV)
            for line in tweetReader:
                if line[0] in TweetCounts:                                                #   If a stock has had a tweet about it, TweetCount is incremented & TweetTexts gets new rows with text of the comment
                    TweetCounts[line[0]] += 1
                    TweetTexts[line[0]].append(line[1])
        
                else:                                                                       #   Otherwise, initialize TweetCount TweetTexts
                    TweetCounts[line[0]] = 1
                    TweetTexts[line[0]] = [line[1]]

        SortedCounts = dict(sorted(TweetCounts.items(), key=lambda item: item[1], reverse = True))
        SortedList = list(SortedCounts.keys())
        
        for stock in SortedList:                                                                
            for tweet in TweetTexts[stock]:                                                         #   Runs through all comments for the most popular stocks                                          
                
                #TODO: MAKE IT SO THAT ONLY NEARBY WORDS ARE COUNTED (POSSIBLY REMOVE NOISE)
                tweet = self.processTweetText(tweet, stock)
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


    def create_sentiment_csv(self, scores, counts, date):
    #   Creates the CSV file with the sentiment information for a given day
        csvName = "Twitter-" + str(date)
        pathToCSV = open(('/Users/tymar/OneDrive/Documents/Capstone/Twitter/Sentiment Scores/' + csvName + ".csv"), 'w')   
        csvWriter = csv.writer(pathToCSV)
        csvWriter.writerow(["source", "date", "stock", "neg", "neu", "pos", "comp", "negative instances", "neutral instances", "positive instances", "total instances"])
        for stock in sorted(counts.keys(), key=lambda stock:(-counts[stock]['total'], stock)):
            csvWriter.writerow(["twitter", str(date), stock, scores[stock]['neg'], scores[stock]['neu'], scores[stock]['pos'], scores[stock]['compound'], counts[stock]['neg'], counts[stock]['neu'], counts[stock]['pos'], counts[stock]['total']])
        pathToCSV.close()
        LOGGER.info(f"\n{csvName} Created: ")
    
    def processTweetText(self, tweet, stock):
        newTweet = ""
        deconTweet = tweet.split(" ")
        for word in deconTweet:
            if len(word) > 1 and (word.isalnum() or word[0] == "$"):
                newTweet = newTweet + word + " "
        
        #print(stock + ": " + newTweet)

        return tweet

    
 
if __name__ == '__main__':
    TODAY = datetime.date.today()
    tw = TwitterSentiment()
    tw.run_for_date(TODAY)

    
