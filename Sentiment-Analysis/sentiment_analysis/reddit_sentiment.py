import praw
from config import *
from mysql_connector_sentiment_analysis import *
import time
import pandas as pd
import matplotlib.pyplot as plt
import squarify
import datetime
import csv
from nltk.sentiment.vader import SentimentIntensityAnalyzer

#CONNECTION = create_mysql_connection()

class RedditSentiment(object):

    def __init__(self):
        self.reddit = praw.Reddit(
            user_agent="Comment Extraction",
            client_id= config.REDDIT_ID,
            client_secret=config.REDDIT_SECRET
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
        self.subs = ['wallstreetbets', 'stocks', 'investing', 'stockmarket']     # sub-reddit to search
        self.post_flairs = {'Daily Discussion', 'Weekend Discussion', 'Discussion', 'Opinion', 'News', 'Gain', 'Loss', 'YOLO', 'Company Discussion', 'Advice Request', 'Advice' 'Company News', 'Trades', None}    # posts flairs to search || None flair is automatically considered
        self.ignore_flair = {'Meme'}    # posts flairs to search
        self.ignoreAuthP = {'example'}       # authors to ignore for posts 
        self.ignoreAuthC = {'example'}       # authors to ignore for comment 
        self.upvoteRatio = 0.70         # upvote ratio for post to be considered
        self.postUps = 15       # define # of upvotes, post is considered if upvotes exceed this #
        self.limit = 30      # define the limit, comments 'replace more' limit
        self.commentUpvotes = 5     # define # of upvotes, comment is considered if upvotes exceed this #
        self.commentWordLimit = 100 #ignore posts with more than this many words

        self.picks = 50     # define # of picks here, prints as "Top ## picks are:"
        self.picks_ayz = 50   # define # of picks for sentiment analysis

        
    def run_for_date(self, date):                                                               
        SortedCounts, CommentTexts, CommentCounts, top_picks = self.process_reddit_comments_posts(date)        #   Goes through top Reddit posts and collects comments about stocks  
        
        scores = self.analyze_sentiment(SortedCounts, CommentTexts, top_picks)                  #   Goes through saved comment texts and generates scores
        
        self.create_sentiment_csv(scores, CommentCounts, date)
        #insert_sentiment_scores(CONNECTION, scores, 'reddit', date)                        
        
        print("Finished analyzing reddit sentiment")
        
        
        
    def process_reddit_comments_posts(self, date):
        start_time = time.time()
        total_posts, num_processed_comments, CommentCounts, titles, CommentAuthors, CommentTexts, = 0, 0, {}, [], {}, {}
        #   total_posts & num_processed_comments: used for logging
        #   CommentCounts: contains the number of comments for a stock
        #   titles: contains the titles of all posts, used for logging
        #   CommentAuthors: Name of author of comments in CommentText about a given stock
        #   CommentTexts: Text of comments about a given stock
                                                                                                                       
        for sub in self.subs:                                                                       #   Runs through: 'wallstreetbets', 'stocks', 'investing', and 'stockmarket' subreddits to search for posts
            subreddit = self.reddit.subreddit(sub)   
            print("Sub: " + str(subreddit))

            top_posts = subreddit.top('day')
            
            newEnoughPost = lambda post: datetime.date.fromtimestamp(post.created_utc) <= date
            correctFlair = lambda post: post.link_flair_text not in self.ignore_flair and post.link_flair_text in self.post_flairs
            likedEnoughPost = lambda post: post.upvote_ratio >= self.upvoteRatio and post.ups > self.postUps
            acceptablePost = lambda post: newEnoughPost(post) and correctFlair(post) and likedEnoughPost(post)

            for post in filter(acceptablePost, top_posts):                                                                  #   Runs through all top posts

                flair = post.link_flair_text                                                        #   Flair = "visual flag next to community member's username. It can be used to distinguish trusted community members or highlight specialized areas of knowledge someone may have"
                if post.author is None:
                    continue
                
                author = post.author.name      

                #   Checking: post upvote ratio, # of upvotes, post flair, and author to determine whether or not to analyze the post
                #   THE POST ITSELF IS NOT CONSIDERED FOR SENTIMENT ANALYSIS, ONLY THE COMMENTS OF THE TOP POSTS

                if author not in self.ignoreAuthP:   
                    post.comment_sort = 'best'     
                    comments = post.comments                                                        #   Stores comments on post
                    titles.append(post.title)                                                       #   Adds the title of the post to a list
                    total_posts += 1 
                    

                    comments.replace_more(limit=self.limit)                                    #   I believe that this may include replies to comments 

                    newEnoughComment = lambda comment: datetime.date.fromtimestamp(comment.created_utc) == date
                    likedEnoughComment = lambda comment: comment.score > self.commentUpvotes
                    fewEnoughWords = lambda comment: len(comment.body.split(" ")) < self.commentWordLimit
                    acceptableComment = lambda comment: newEnoughComment(comment) and likedEnoughComment(comment) and fewEnoughWords(comment)
                    #containsKeyword = lambda comment: word.isupper and comment.body.split(" ").isupper()

                    for comment in filter(acceptableComment, comments):                                                        #   Run through all comments on post
                        # try except for deleted account?
                        try: 
                            auth = comment.author.name
                        except: 
                            pass

                        num_processed_comments += 1 

                        #   Checking: comment upvotes and author to determine whether or not to analyze the comment
                        if auth not in self.ignoreAuthC:  
                            comment_text = comment.body.split(" ")                                     
                            for word in comment_text:
                                word = word.replace("$", "")        
                                if word.isupper() and word in us and word not in blacklist:         
                                    try: 
                                        if auth in CommentAuthors[word]: break
                                    except: 
                                        pass
                                        
                                    print(word + ": Date of post - " + str(datetime.date.fromtimestamp(post.created_utc)) + ", Date of comment - " + str(datetime.date.fromtimestamp(comment.created_utc)) + ", Comment = " + str(comment.body)) 
                                   
                                   #   counting CommentCounts
                                    if word in CommentCounts:                                                   #   If a stock has had a post about it, CommentCount is incremented, and CommmentAuthors & CaommentTexts gets new rows with the author and text of the comment, respectively
                                        CommentCounts[word] += 1
                                        CommentAuthors[word].append(auth)                         
                                        CommentTexts[word].append(comment.body)
        
                                    else:                                                                       #   Otherwise, initialize CommentCount, CommentAuthors, and CommentTexts
                                        CommentCounts[word] = 1
                                        CommentAuthors[word] = [auth]
                                        CommentTexts[word] = [comment.body]
                


            #   Sorts CommentCounts by highest CommentCounts
        SortedCounts = dict(sorted(CommentCounts.items(), key=lambda item: item[1], reverse = True))          
        top_picks = list(SortedCounts.keys())[0:self.picks] 
        time_elapsed = (time.time() - start_time)                                                               #   Used for logging

        # print top picks
        LOGGER.info("It took {t:.2f} seconds to analyze {c} comments in {p} posts in {s} subreddits.\n".format(t=time_elapsed, c=num_processed_comments, p=total_posts, s=len(self.subs)))
        LOGGER.info("Posts analyzed saved in titles")
       #for i in titles: print(i)  # prints the title of the posts analyzed

        LOGGER.info(f"\n{self.picks} most mentioned picks: ")

        return SortedCounts, CommentTexts, CommentCounts, top_picks

    def analyze_sentiment(self, SortedCounts, CommentTexts, top_picks):
    #        times = []                                                                             #   COMMENTED OUT times, ONLY USED IN GRAPHING. Contains list of times that each stock is mentioned (detached from name). 
    #        top = []                                                                               #   COMMENTED OUT top, ONLY USED IN GRAPHING. Contains String-formatted list "Stock: Count" with all top picks
        for i in top_picks:
            print(f"{i}: {SortedCounts[i]}")
    #       times.append(SortedCounts[i])
    #       top.append(f"{i}: {SortedCounts[i]}")
        
        # Applying Sentiment Analysis
        CommentScores, CumulativeScores = {}, {}                                             
                                                                                                    #   tweetscores contains all neg, neu, and pos sentiment for all of a stock's tweets.
                                                                                                    #   cumulativescores contains an average of all neg, neu, and pos sentiment for a stock.

        # adding custom words from data.py 
        self.vader.lexicon.update(new_words)

        picks_sentiment = list(SortedCounts.keys())[0:self.picks_ayz]                   
        for stock in picks_sentiment:                                                        
            stock_comments = CommentTexts[stock]
            for cmnt in stock_comments:                                                         #   Runs through all comments for the most popular stocks                                          
                commentScore = self.vader.polarity_scores(cmnt)                                
               
                if stock in CommentScores:                                                      #   Adds score to CommentScores at index comment if a comment has been processed for it
                    CommentScores[stock][cmnt] = commentScore
                else:                                                                           #   Initializes CommentScores if a comment has not yet been processed for it.
                    CommentScores[stock] = {cmnt:commentScore}  
                    
                if stock in CumulativeScores:                                                   #   Adds score to CumulativeScores at if a comment has been processed for it
                    for sentimentType, score in commentScore.items():                                                       
                        CumulativeScores[stock][sentimentType] = str(float(CumulativeScores[stock][sentimentType]) + score)
                else:                                                                           #   Initializes CumulativeScores if a comment has not yet been processed for it.
                    CumulativeScores[stock] = commentScore
                    
                    # calculating avg.
            for sentimentType in CumulativeScores[stock]:                                                   #   Runs through all scores for a stock
                CumulativeScores[stock][sentimentType] = float(CumulativeScores[stock][sentimentType]) / float(SortedCounts[stock])         #   The cumulative score for each type of sentiment (neg, neu, pos) is an average of all scores of that type. 
                CumulativeScores[stock][sentimentType]  = "{pol:.3f}".format(pol=CumulativeScores[stock][sentimentType])        #   Formats CumulativeScores to 3 decimals
        
        return CumulativeScores

    def create_sentiment_csv(self, scores, counts, date):
        csvName = "Reddit-" + str(date)
        pathToCSV = open(('/users/tymar/downloads/Schoolwork/Capstone/Reddit/RedditScores/' + csvName + ".csv"), 'w')
        csvWriter = csv.writer(pathToCSV)
        csvWriter.writerow(["source", "date", "stock", "neg", "neu", "pos", "comp", "instances"])
        for stock in scores:
            csvWriter.writerow(["reddit", str(date), stock, scores[stock]['neg'], scores[stock]['neu'], scores[stock]['pos'],  scores[stock]['compound'], counts[stock]])
        pathToCSV.close()
        LOGGER.info(f"\n{csvName} Created: ")




    #    def display_sentiment(self, scores):
    #        # printing sentiment analysis 
    #        print(f"\nSentiment analysis of top {self.picks_ayz} picks:")
    #        df = pd.DataFrame(scores)
    #        df.index = ['Bearish', 'Neutral', 'Bullish', 'Total/Compound']
    #        df = df.T
    #        print(df)
    #
    #        # Date Visualization
    #        # most mentioned picks    
    #        squarify.plot(sizes=times, label=top, alpha=.7 )
    #        plt.axis('off')
    #        plt.title(f"{self.picks} most mentioned picks")
    #        plt.show()
    #
    #        # Sentiment analysis
    #        df = df.astype(float)
    #        colors = ['red', 'springgreen', 'forestgreen', 'coral']
    #        df.plot(kind = 'bar', color=colors, title=f"Sentiment analysis of top {self.picks_ayz} picks:")
    #        plt.show()

    

