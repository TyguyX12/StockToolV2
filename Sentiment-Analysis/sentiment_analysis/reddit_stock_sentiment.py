import praw
from config.config import *
from mysqlcon.mysql_connector import *
import time
import pandas as pd
import matplotlib.pyplot as plt
import squarify
from nltk.sentiment.vader import SentimentIntensityAnalyzer

CONNECTION = create_mysql_connection()

class RedditSentiment(object):

    def __init__(self):
        self.reddit = praw.Reddit(
            user_agent="Comment Extraction",
            client_id=REDDIT_ID,
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
        self.subs = ['wallstreetbets', 'stocks', 'investing', 'stockmarket']     # sub-reddit to search
        self.post_flairs = {'Daily Discussion', 'Weekend Discussion', 'Discussion'}    # posts flairs to search || None flair is automatically considered
        self.goodAuth = {'AutoModerator'}   # authors whom comments are allowed more than once
        self.uniqueCmt = True                # allow one comment per author per symbol
        self.ignoreAuthP = {'example'}       # authors to ignore for posts 
        self.ignoreAuthC = {'example'}       # authors to ignore for comment 
        self.upvoteRatio = 0.70         # upvote ratio for post to be considered, 0.70 = 70%
        self.ups = 20       # define # of upvotes, post is considered if upvotes exceed this #
        self.limit = 10      # define the limit, comments 'replace more' limit
        self.upvotes = 2     # define # of upvotes, comment is considered if upvotes exceed this #
        self.picks = 30     # define # of picks here, prints as "Top ## picks are:"
        self.picks_ayz = 30   # define # of picks for sentiment analysis


    def run_reddit_sentiment(self, date):                                                       #   ADDED date
        SortedCounts, CommentTexts, top_picks = self.process_reddit_comments_posts(date)        #   Goes through hot Reddit posts and collects comments about stocks
                                                                                                #   TODO, ONLY SEARCH FOR REDDIT POSTS FOR A GIVEN DATE
        
        scores = self.analyze_sentiment(SortedCounts, CommentTexts, top_picks)                  #   Goes through saved comment texts and generates scores
        
        insert_sentiment_scores(CONNECTION, scores, 'reddit', date)                             #   REMOVED type AND ADDED date
        print("Finished analyzing reddit sentiment")
        
        
        
    def process_reddit_comments_posts(self):
        start_time = time.time()
        total_posts, num_processed_comments, CommentCount, titles, CommentAuthors, CommentTexts, = 0, 0, {}, [], {}, {}         #    RENAMED posts, c_analyzed, tickers, cmt_auth, a_comments TO total_posts, num_processed_comments, CommentCount, CommentAuthors, CommentTexts, DELETED count, 
        #   total_posts & num_processed_comments: used for logging
        #   CommentCount: contains the number of comments for a stock
        #   titles: contains the titles of all posts, used for logging
        #   CommentAuthors: Name of author of comments in CommentText about a given stock
        #   CommentTexts: Text of comments about a given stock
                                                                                                                       
        for sub in self.subs:                                                                       #   Runs through: 'wallstreetbets', 'stocks', 'investing', and 'stockmarket' subreddits to search for posts
            subreddit = self.reddit.subreddit(sub)              
            hot_posts = subreddit.hot()                                                             #   RENAMED hot_python TO hot_posts. Sorting posts by hot
            
            for post in hot_posts:                                                                  #   RENAMED submission TO post. Run's through all hot posts
                flair = post.link_flair_text                                                        #   Flair = "visual flag next to community member's username. It can be used to distinguish trusted community members or highlight specialized areas of knowledge someone may have"
                author = post.author.name         
                
                #   Checking: post upvote ratio, # of upvotes, post flair, and author to determine whether or not to analyze the post
                #   THE POST ITSELF IS NOT CONSIDERED FOR SENTIMENT ANALYSIS, ONLY THE COMMENTS OF THE TOP POSTS
                if post.upvote_ratio >= self.upvoteRatio and post.ups > self.ups and (flair in self.post_flairs or flair is None) and author not in self.ignoreAuthP:   
                    post.comment_sort = 'new'     
                    comments = post.comments                                                        #   Stores comments on post
                    titles.append(post.title)                                                       #   Adds the title of the post to a list
                    num_posts += 1                                                                  
                    post.comments.replace_more(limit=self.limit)                                    #   WHAT DOES THIS DO? 
                    
                    for comment in comments:                                                        #   Run through all comments on post
                        # try except for deleted account?
                        try: auth = comment.author.name
                        except: pass
                        num_processed_comments += 1                                                
                        
                        #   Checking: comment upvotes and author to determine whether or not to analyze the comment
                        if comment.score > self.upvotes and auth not in self.ignoreAuthC:      
                            comment_text = comment.body.split(" ")                                         #   RENAMED split TO comment_text FOR CLARITY
                            for word in comment_text:
                                word = word.replace("$", "")        
                                #   upper = ticker, length of ticker <= 5, excluded words,                     
                                if word.isupper() and len(word) <= 5 and word not in blacklist and word in us:          #   WHAT DOES ISUPPER DO? IF IT CHECKS FOR WORD IN us, IT IS REDUNDANT
                                    
                                    #   unique comments, try/except for key errors
                                    if self.uniqueCmt and auth not in self.goodAuth:
                                        try: 
                                            if auth in cmt_auth[word]: break
                                        except: pass
                                        
                                    #   counting CommentCount
                                    if word in CommentCount:                                                   #   If a stock has had a post about it, CommentCount is incremented, and CommmentAuthors & CommentTexts gets new rows with the author and text of the comment, respectively
                                        CommentCount[word] += 1
                                        CommentAuthors[word].append(auth)                         
                                        CommentTexts[word].append(comment.body)
        
                                    else:                                                                       #   Otherwise, initialize CommentCount, CommentAuthors, and CommentTexts
                                        CommentCount[word] = 1
                                        CommentAuthors[word] = [auth]
                                        CommentTexts[word] = [comment.body]

        #   Sorts CommentCount by highest CommentCount
        SortedCounts = dict(sorted(CommentCount.items(), key=lambda item: item[1], reverse = True))             #   RENAMED symbols TO SortedCounts FOR CLARITY
        top_picks = list(SortedCounts.keys())[0:self.picks] 
        time_elapsed = (time.time() - start_time)                                                               #   Used for logging

        # print top picks
        LOGGER.info("It took {t:.2f} seconds to analyze {c} comments in {p} posts in {s} subreddits.\n".format(t=time_elapsed, c=num_processed_comments, p=total_posts, s=len(self.subs)))
        LOGGER.info("Posts analyzed saved in titles")
        #for i in titles: print(i)  # prints the title of the posts analyzed

        LOGGER.info(f"\n{self.picks} most mentioned picks: ")

        return SortedCounts, CommentTexts, top_picks

    def analyze_sentiment(self, SortedCounts, CommentTexts, top_picks):
#        times = []                                                                             #   COMMENTED OUT times, ONLY USED IN GRAPHING. Contains list of times that each stock is mentioned (detached from name). 
#        top = []                                                                               #   COMMENTED OUT top, ONLY USED IN GRAPHING. Contains String-formatted list "Stock: Count" with all top picks
        for i in top_picks:
            print(f"{i}: {SortedCounts[i]}")
#            times.append(SortedCounts[i])
#            top.append(f"{i}: {SortedCounts[i]}")
        
        # Applying Sentiment Analysis
        CommentScores, CumulativeScores = {}, {}                                                #   RENAMED s TO CommentScores, scores TO CumulativeScores FOR CLARITY
                                                                                                #   tweetscores contains all neg, neu, and pos sentiment for all of a stock's tweets.
                                                                                                #   cumulativescores contains an average of all neg, neu, and pos sentiment for a stock.

        # adding custom words from data.py 
        self.vader.lexicon.update(new_words)

        picks_sentiment = list(SortedCounts.keys())[0:self.picks_ayz]                           #   SEEMS REDUNDANT, SAME AS top_picks?
        for stock in picks_sentiment:                                                           #   RENAMED symbol TO stock FOR CLARITY
            stock_comments = CommentTexts[stock]
            for cmnt in stock_comments:                                                         #   Runs through all comments for the most popular stocks                                          
                commentScore = self.vader.polarity_scores(cmnt)                                 #   RENAMED score to commentScore FOR CLARITY. commentScore = neg, neu, pos, and compound scores for a given comment
               
                if stock in CommentScores:                                                      #   Adds score to CommentScores at index comment if a comment has been processed for it
                    CommentScores[stock][cmnt] = commentScore
                else:                                                                           #   Initializes CommentScores if a comment has not yet been processed for it.
                    CommentScores[stock] = {cmnt:commentScore}  
                    
                if stock in CumulativeScores:                                                   #   Adds score to CumulativeScores at if a comment has been processed for it
                    for sentimentType, _ in commentScore.items():                               #   RENAMED key TO sentimentType (neg, neu, pos) FOR CLARITY.                                  
                        CumulativeScores[stock][sentimentType] += commentScore[sentimentType]
                else:                                                                           #   Initializes CumulativeScores if a comment has not yet been processed for it.
                    CumulativeScores[stock] = commentScore
                    
            # calculating avg.
            for sentimentType in commentScore:                                                   #   Runs through all scores for a stock
                CumulativeScores[stock][sentimentType] = CumulativeScores[stock][sentimentType] / SortedCounts[stock]           #   The cumulative score for each type of sentiment (neg, neu, pos) is an average of all scores of that type. 
                CumulativeScores[stock][sentimentType]  = "{pol:.3f}".format(pol=CumulativeScores[stock][sentimentType])        #   Formats CumulativeScores to 3 decimals
        
        return CumulativeScores


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

    

