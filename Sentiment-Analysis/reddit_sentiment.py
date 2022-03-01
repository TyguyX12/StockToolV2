import praw
from praw.reddit import Comment
from config import *
import time
import datetime
import csv
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class RedditSentiment(object):

    def __init__(self):
        self.reddit = praw.Reddit(
            user_agent="Comment Extraction",
            client_id= REDDIT_ID,
            client_secret=REDDIT_SECRET
        )
        LOGGER.info("Connected to Reddit")
        self.set_parameters()

        try:
            self.vader = SentimentIntensityAnalyzer()
        except Exception as e:
            LOGGER.info(e)
            LOGGER.info("Vader Lexicon missing. Downloading required file...")
            import nltk
            nltk.download('vader_lexicon')
            self.vader = SentimentIntensityAnalyzer()


    def set_parameters(self):
        # set the program parameters
        self.subs = ['wallstreetbets', 'stocks', 'investing', 'stockmarket', 'pennystocks']     # sub-reddit to search
        self.ignore_flair = {'Meme'}                #   posts flairs to ignore
        self.upvoteRatio = 0.70                     #   upvote ratio for post to be considered
        self.postUps = 5                           #   define # of upvotes, post is considered if upvotes exceed this #
        self.limit = 100                             #   define the limit, comments 'replace more' limit
        self.commentUpvotes = 3                     #   define # of upvotes, comment is considered if upvotes exceed this #
        self.commentWordLimit = 75                  #   ignore posts with more than this many words
        self.maxNeutralSentiment = 0.75             #   Excludes Tweets with a higher neutral score than this. Removes noise from data


        
    def run_for_date(self, date):                                                               
        self.process_reddit_comments_posts(date)                                        #   Goes through top Reddit posts and collects comments about stocks and saves them in a csv file   
        CommentCounts, scores = self.runSentimentAnalysisForDate(date)                  #   Goes through post csv file and generates scores
        self.create_sentiment_csv(scores, CommentCounts, date)
        print("Finished analyzing reddit sentiment")
        
        
        
    def process_reddit_comments_posts(self, date):
        num_processed_comments, CommentCounts, titles, CommentTexts, = 0, {}, [], {}
        #   num_processed_comments: used for logging
        #   CommentCounts: contains the number of comments for a stock
        #   titles: contains the titles of all posts, used for logging
        #   CommentTexts: Text of comments about a given stock

        redditPostsCSVPath = open(('/Users/tymar/OneDrive/Documents/Capstone/Reddit/Reddit Posts/RedditPosts-' + str(datetime.date.today()) + '.csv'), 'w')
        redditPostsCSVWriter = csv.writer(redditPostsCSVPath)                                                                                                             
        for sub in self.subs:                                                                       #   Runs through: 'wallstreetbets', 'stocks', 'investing', and 'stockmarket' subreddits to search for posts
            subreddit = self.reddit.subreddit(sub)   
            print("Sub: " + str(subreddit))

            top_posts = subreddit.top('day')
            
            newEnoughPost = lambda post: datetime.date.fromtimestamp(post.created_utc) <= date
            acceptableFlair = lambda post: post.link_flair_text not in self.ignore_flair
            likedEnoughPost = lambda post: post.upvote_ratio >= self.upvoteRatio and post.ups > self.postUps
            acceptablePost = lambda post: newEnoughPost(post) and acceptableFlair(post) and likedEnoughPost(post)

            for post in filter(acceptablePost, top_posts):                                                                  #   Runs through all top posts

                #   Checking: post upvote ratio, # of upvotes, and post flair to determine whether or not to analyze the post
                #   THE POST ITSELF IS NOT CONSIDERED FOR SENTIMENT ANALYSIS, ONLY THE COMMENTS OF THE TOP POSTS

                post.comment_sort = 'best'     
                comments = post.comments                                                        #   Stores comments on post
                titles.append(post.title)                                                       #   Adds the title of the post to a list
                    

                comments.replace_more(limit=self.limit)                                    #   I believe that this may include replies to comments 

                #   Checking: comment date, upvotes, and word count to determine whether or not to analyze the comment
                newEnoughComment = lambda comment: datetime.date.fromtimestamp(comment.created_utc) == date
                likedEnoughComment = lambda comment: comment.score > self.commentUpvotes
                fewEnoughWords = lambda comment: len(comment.body.split(" ")) < self.commentWordLimit
                acceptableComment = lambda comment: newEnoughComment(comment) and likedEnoughComment(comment) and fewEnoughWords(comment)

                for comment in filter(acceptableComment, comments):                                                        #   Run through all comments on post

                    num_processed_comments += 1 
                    comment_text = comment.body.replace(",", "").replace("b'", " ").split(" ")                                
                    for word in comment_text:
                        word = word.replace("$", "")   
                        stocksInPost = []
                        if len(word) > 0 and len(word) < 7  and word.upper() in stock_list and word.upper() not in stocksInPost:
                            stocksInPost.append(word.upper())
                            stock = word.upper()
                            cmnt = self.processPostText(comment.body.encode("utf-8"), stock)
                            redditPostsCSVWriter.writerow([stock, cmnt])            
                            print(stock + ": Date of post - " + str(datetime.date.fromtimestamp(post.created_utc)) + ", Date of comment - " + str(datetime.date.fromtimestamp(comment.created_utc)) + ", Comment = " + str(comment.body)) 
                                   
                          
        redditPostsCSVPath.close()

    def runSentimentAnalysisForDate(self, date):        
        RedditPostTexts, RedditPostCounts, CommentScores, CumulativeScores, PostCounts = {}, {}, {}, {}, {}     #   tweetscores contains all neg, neu, and pos sentiment for all of a stock's tweets.
                                                                                                                #   cumulativescores contains an average of all neg, neu, and pos sentiment for a stock.
        RedditPostsCSVPath = '/Users/tymar/OneDrive/Documents/Capstone/Reddit/Reddit Posts/RedditPosts-' + str(date) + '.csv'
        
        # adding custom words from config
        self.vader.lexicon.update(new_words)
        
        print("Starting Sentiment Analysis for date: " + str(date))
        with open(RedditPostsCSVPath, newline='\n') as RedditPostCSV:
    
            RedditPostReader = csv.reader(_.replace('\x00', '') for _ in RedditPostCSV)
            for line in RedditPostReader:
                if line[0] in RedditPostCounts:                                                #   If a stock has had a tweet about it, TweetCount is incremented & TweetTexts gets new rows with text of the comment
                    RedditPostCounts[line[0]] += 1
                    RedditPostTexts[line[0]].append(line[1])
        
                else:                                                                       #   Otherwise, initialize TweetCount TweetTexts
                    RedditPostCounts[line[0]] = 1
                    RedditPostTexts[line[0]] = [line[1]]

        SortedCounts = dict(sorted(RedditPostCounts.items(), key=lambda item: item[1], reverse = True))
        SortedList = list(SortedCounts.keys())
                
        for stock in SortedList:                                                       
            for cmnt in RedditPostTexts[stock]:                                                         #   Runs through all comments for the most popular stocks                                          
                commentScore = self.vader.polarity_scores(cmnt)                                
                if (commentScore['neu'] < self.maxNeutralSentiment):
                    print("Processed Post: $" + stock + ": " + cmnt + " | Sentiment Scores: " + str(commentScore))
                    if stock in CommentScores:                                                      #   Adds score to CommentScores at index comment if a comment has been processed for it
                        CommentScores[stock][cmnt] = commentScore
                        if commentScore['compound'] < -0.33:
                            PostCounts[stock]['neg'] += 1
                        elif commentScore['compound'] < 0.33:
                            PostCounts[stock]['neu'] += 1
                        else:
                            PostCounts[stock]['pos'] += 1
                        PostCounts[stock]['total'] += 1
                    else:                                                                           #   Initializes CommentScores if a comment has not yet been processed for it.
                        CommentScores[stock] = {cmnt:commentScore}  
                        if commentScore['compound'] < -0.33:
                            PostCounts[stock] = {'neg': 1, 'neu': 0, 'pos': 0, 'total': 1}
                        elif commentScore['compound'] < 0.33:
                            PostCounts[stock] = {'neg': 0, 'neu': 1, 'pos': 0, 'total': 1}
                        else:
                            PostCounts[stock] = {'neg': 0, 'neu': 0, 'pos': 1, 'total': 1}

                    if stock in CumulativeScores:                                                   #   Adds score to CumulativeScores at if a comment has been processed for it
                        for sentimentType, score in commentScore.items():                                                       
                            CumulativeScores[stock][sentimentType] = str(float(CumulativeScores[stock][sentimentType]) + score)
                    else:                                                                           #   Initializes CumulativeScores if a comment has not yet been processed for it.
                        CumulativeScores[stock] = commentScore
                    
                    # calculating avg.
            try:
                for sentimentType in CumulativeScores[stock]:                                                   #   Runs through all scores for a stock
                    CumulativeScores[stock][sentimentType] = float(CumulativeScores[stock][sentimentType]) / float(PostCounts[stock]['total'])          #   The cumulative score for each type of sentiment (neg, neu, pos) is an average of all scores of that type. 
                    CumulativeScores[stock][sentimentType]  = "{pol:.3f}".format(pol=CumulativeScores[stock][sentimentType])        #   Formats CumulativeScores to 3 decimals
            except Exception:    #  Catch exceptions for stocks with posts, but without processed posts (neutral score under threshold)
                pass
        
        print("Finished Sentiment Analysis")
        return PostCounts, CumulativeScores 

    def create_sentiment_csv(self, scores, counts, date):
        print("Creating Sentiment CSV")
        csvName = "Reddit-" + str(date)
        pathToCSV = open(('/Users/tymar/OneDrive/Documents/Capstone/Reddit/Sentiment Scores/' + csvName + ".csv"), 'w')
        csvWriter = csv.writer(pathToCSV)
        csvWriter.writerow(["source", "date", "stock", "neg", "neu", "pos", "comp", "negative instances", "neutral instances", "positive instances", "total instances"])
        for stock in sorted(counts.keys(), key=lambda stock:(-counts[stock]['total'], stock)):
            csvWriter.writerow(["reddit", str(date), stock, scores[stock]['neg'], scores[stock]['neu'], scores[stock]['pos'], scores[stock]['compound'], counts[stock]['neg'], counts[stock]['neu'], counts[stock]['pos'], counts[stock]['total']])
        pathToCSV.close()
        LOGGER.info(f"\n{csvName} Created: ")
        print("Finished Creating Sentiment CSV")


    def processPostText(self, post, stock):
        newPost = ""
        deconPost = post.split()
        for word in deconPost:
            if len(word) > 1 and (word.isalnum() or word[0] == "$"):
                newPost = newPost + str(word) + " "
        
        #print(stock + ": " + newPost)

        return post
 
if __name__ == '__main__':
    TODAY = datetime.date.today()
    rd = RedditSentiment()
    rd.run_for_date(TODAY)
