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


    def process_reddit_comments_posts(self):
        start_time = time.time()
        posts, count, c_analyzed, tickers, titles, a_comments = 0, 0, 0, {}, [], {}
        cmt_auth = {}

        for sub in self.subs:
            subreddit = self.reddit.subreddit(sub)
            hot_python = subreddit.hot()    # sorting posts by hot
            # Extracting comments, symbols from subreddit
            for submission in hot_python:
                flair = submission.link_flair_text 
                author = submission.author.name         
                
                # checking: post upvote ratio # of upvotes, post flair, and author 
                if submission.upvote_ratio >= self.upvoteRatio and submission.ups > self.ups and (flair in self.post_flairs or flair is None) and author not in self.ignoreAuthP:   
                    submission.comment_sort = 'new'     
                    comments = submission.comments
                    titles.append(submission.title)
                    posts += 1
                    submission.comments.replace_more(limit=self.limit)   
                    for comment in comments:
                        # try except for deleted account?
                        try: auth = comment.author.name
                        except: pass
                        c_analyzed += 1
                        
                        # checking: comment upvotes and author
                        if comment.score > self.upvotes and auth not in self.ignoreAuthC:      
                            split = comment.body.split(" ")
                            for word in split:
                                word = word.replace("$", "")        
                                # upper = ticker, length of ticker <= 5, excluded words,                     
                                if word.isupper() and len(word) <= 5 and word not in blacklist and word in us:
                                    
                                    # unique comments, try/except for key errors
                                    if self.uniqueCmt and auth not in self.goodAuth:
                                        try: 
                                            if auth in cmt_auth[word]: break
                                        except: pass
                                        
                                    # counting tickers
                                    if word in tickers:
                                        tickers[word] += 1
                                        a_comments[word].append(comment.body)
                                        cmt_auth[word].append(auth)
                                        count += 1
                                    else:                               
                                        tickers[word] = 1
                                        cmt_auth[word] = [auth]
                                        a_comments[word] = [comment.body]
                                        count += 1    

        # sorts the dictionary
        symbols = dict(sorted(tickers.items(), key=lambda item: item[1], reverse = True))
        top_picks = list(symbols.keys())[0:self.picks]
        time_elapsed = (time.time() - start_time)

        # print top picks
        LOGGER.info("It took {t:.2f} seconds to analyze {c} comments in {p} posts in {s} subreddits.\n".format(t=time_elapsed, c=c_analyzed, p=posts, s=len(self.subs)))
        LOGGER.info("Posts analyzed saved in titles")
        #for i in titles: print(i)  # prints the title of the posts analyzed

        LOGGER.info(f"\n{self.picks} most mentioned picks: ")

        return symbols, a_comments, top_picks

    def analyze_sentiment(self, symbols, a_comments, top_picks):
        times = []
        top = []
        for i in top_picks:
            print(f"{i}: {symbols[i]}")
            times.append(symbols[i])
            top.append(f"{i}: {symbols[i]}")
        
        # Applying Sentiment Analysis
        scores, s = {}, {}


        # adding custom words from data.py 
        self.vader.lexicon.update(new_words)

        picks_sentiment = list(symbols.keys())[0:self.picks_ayz]
        for symbol in picks_sentiment:
            stock_comments = a_comments[symbol]
            for cmnt in stock_comments:
                score = self.vader.polarity_scores(cmnt)
                if symbol in s:
                    s[symbol][cmnt] = score
                else:
                    s[symbol] = {cmnt:score}      
                if symbol in scores:
                    for key, _ in score.items():
                        scores[symbol][key] += score[key]
                else:
                    scores[symbol] = score
                    
            # calculating avg.
            for key in score:
                scores[symbol][key] = scores[symbol][key] / symbols[symbol]
                scores[symbol][key]  = "{pol:.3f}".format(pol=scores[symbol][key])
        
        return scores


    def display_sentiment(self, scores):
        # printing sentiment analysis 
        print(f"\nSentiment analysis of top {self.picks_ayz} picks:")
        df = pd.DataFrame(scores)
        df.index = ['Bearish', 'Neutral', 'Bullish', 'Total/Compound']
        df = df.T
        print(df)

        # Date Visualization
        # most mentioned picks    
        squarify.plot(sizes=times, label=top, alpha=.7 )
        plt.axis('off')
        plt.title(f"{self.picks} most mentioned picks")
        plt.show()

        # Sentiment analysis
        df = df.astype(float)
        colors = ['red', 'springgreen', 'forestgreen', 'coral']
        df.plot(kind = 'bar', color=colors, title=f"Sentiment analysis of top {self.picks_ayz} picks:")
        plt.show()

    
    def run_reddit_sentiment(self):
        symbols, a_comments, top_picks = self.process_reddit_comments_posts()
        scores = self.analyze_sentiment(symbols, a_comments, top_picks)
        insert_sentiment_scores(CONNECTION, scores, 'reddit', 'hourly')
        print("Finished analyzing reddit sentiment")
