from mysql.connector import MySQLConnection, Error
from config import config
import json


def create_mysql_connection():
    '''
    Instantiates connection to the MySQL DB
    '''
    try:
        connection = MySQLConnection(**config.DB_CONFIG)
        config.LOGGER.info(f"Connection to MySQL DB successfully established as user {config.DB_CONFIG['user']}")
        with connection.cursor() as cursor:
            cursor.execute("SET NAMES utf8mb4")
        connection.commit()
        return connection
    except Error as e:  
        config.LOGGER.error("Error connecting to MySQL DB.")

	
#	Gathers unprocessed Tweets from the db
#	TODO: ONLY GATHER TWEETS FROM A SPECIFIC DATE
def gather_tweets_from_db(conn, date):								#	REPLACED sentiment_type WITH date														
	'''
    	Gathers all tweets from a particular date in dictionary form
    	'''
	formattedDate = date									#	REPLACED FORMATTING OF processed WITH FORMATING OF date
	sql = """SELECT * FROM twitterdata WHERE processed = 'N' AND date = {}""".format(formattedDate) 	#	TEMPORARY, FIND HOW TO INCLUDE DATE WHEN PULLING TWEETS
    	cursor = conn.cursor(dictionary=True)
    	cursor.execute(sql)
    	return cursor


#	Marks Tweets as "processed" once they have had their sentiment analyzed
def update_processed_col(conn, tweet_ids, sentiment_type):
	'''
    	Updates the rows which have been processed with processed = 'Y'
    	'''
	#REMOVED FORMATTING OF processed, OUTDATED
    	tweet_ids = tuple(tweet_ids)
    	sql = f"""UPDATE twitterdata SET processed = 'Y' WHERE idTwitterData IN {tweet_ids}"""
    	cursor = conn.cursor()
    	cursor.execute(sql)
    	cursor.close()
    	conn.commit()

	
#	Inserts sentiment scores for a given date
#	TODO: REIMPLEMENT USING NEW sentimentdata SCHEMA
def insert_sentiment_scores(conn, scores, source, sentiment_type, date):					#	ADDED date
    	'''
    	Inserts sentiment scores into sentimentdata table
    	'''
    	sql = """INSERT INTO sentimentdata (sentiment_scores, source, sentiment_type) VALUES (%s, %s, %s)"""
    	sentiment_data = (json.dumps(scores), source, sentiment_type)
    	cursor = conn.cursor()
    	cursor.execute(sql, sentiment_data)
    	cursor.close()
    	conn.commit()


#def insert_processed_sentiment_score(conn, asset, score, sentiment_type):
#    '''
#    Inserts processed sentiment scores into processedsentimentdata table
#    '''
#	
#	''' IF THERE EXISTS A PROCESSED SENTIMENT SCORE WITH THE NAME OF A GIVEN ASSET, UPDATE RELEVENT SCORE'''
#	IF EXISTS
#	(
#		sql = """SELECT * FROM processedsentimentdata WHERE asset = %s"""
#		cursor.execute(sql, asset))
#	)
#	BEGIN
#		CASE
#			WHEN sentiment_type = 'twitter' THEN """UPDATE processedsentimentdata SET daily_twitter_score = $s WHERE asset = $s;"""
#			WHEN sentiment_type = 'reddit' THEN """UPDATE processedsentimentdata SET daily_reddit_score = $s WHERE asset = $s;"""
#		END AS sql
#		processed_sentiment_data = (score, asset)
#	END
#	''' IF THERE DOES NOT EXIST A PROCESSED SENTIMENT SCORE WITH THE NAME OF A GIVEN ASSET, AN ENTRY IS MADE IN THE PROCESSEDSENTIMENT SCORE TABLE '''
#	ELSE
#	BEGIN
#		CASE
#			WHEN sentiment_type = 'twitter' THEN """INSERT INTO processedsentimentdata (asset, daily_twitter_score, daily_reddit_score, daily_cumulative_score, weekly_score, monthly_score) VALUES (%s, %s, NULL, %s, %s, %s)"""
#			WHEN sentiment_type = 'reddit' THEN """INSERT INTO processedsentimentdata (asset, daily_twitter_score, daily_reddit_score, daily_cumulative_score, weekly_score, monthly_score) VALUES (%s, NULL, %s, %s, %s, %s)"""
#		END AS sql
#		processed_sentiment_data = (asset, score, score, score, score)
#	END
#	cursor = conn.cursor()
#	cursor.execute(sql, processedsentiment_data)
#	cursor.close()
#	conn.commit()   


#def update_daily_cumulative_scores(conn, asset):
#	BOOLEAN reddit, twitter
#	INTEGER cumulativeScore = 0
#	IF EXISTS
#	(
#		sql = """SELECT daily_reddit_score FROM processedsentimentdata WHERE asset = %s"""
#		cursor = conn.cursor()
#		cursor.execute(sql, asset)
#	)	
#	BEGIN
#		cumulativeScore += cursor
#		reddit = TRUE
#	END
#	IF EXISTS
#	(
#		sql = """SELECT daily_twitter_score FROM processedsentimentdata WHERE asset = %s"""
#		cursor = conn.cursor()
#		cursor.execute(sql, asset)
#	)	
#	BEGIN
#		cumulativeScore += cursor
#		twitter = TRUE
#	END
#	
#	CASE
#		WHEN reddit = true AND twitter = true THEN cumulativeScore / 2
#		WHEN reddit = false AND twitter = false THEN 0
#		ELSE 0
#	END AS cumulativeScore
#	
#	sql = """UPDATE processedsentimentdata SET daily_cumulative_score = $s WHERE asset = $s;"""
#	cursor = conn.cursor()
#	cursor.execute(sql, cumulativeScore)
#	
#	cursor.close()
#	conn.commit()


#def update_weekly_monthly_scores(conn, asset):
#	
#	''' 
#	Updates weekly processed sentiment scores in processedsentimentdata table
#	'''
#	weeklyScore = 0;
#	
#	sql = """SELECT weekly_score FROM processedsentimentdata WHERE asset = %s"""
#	cursor.execute(sql, asset))
#	weeklyScore = cursor
#	newWeeklyScore = ((6/7) * weeklyScore) + ((1/7) * score)
#	
#	sql = """UPDATE processedsentimentdata SET weekly_score = $s WHERE asset = $s;"""
#	processed_sentiment_data = (newWeeklyScore, asset)
#	cursor = conn.cursor()
#	cursor.execute(sql, processedsentiment_data)
#	
#	
#	'''
#	Updates monthly processed sentiment scores in processedsentimentdata table
#	'''
#	monthlyScore = 0;
#	
#	sql = """SELECT monthly_score FROM processedsentimentdata WHERE asset = %s"""
#	cursor.execute(sql, asset))
#	monthlyScore = cursor
#	newMonthlyScore = ((27/28) * monthlyScore) + ((1/28) * score)
#	
#	sql = """UPDATE processedsentimentdata SET monthly_score = $s WHERE asset = $s;"""
#	processed_sentiment_data = (newMonthlyScore, asset)
#	cursor = conn.cursor()
#	cursor.execute(sql, processedsentiment_data)
#	
#	cursor.close()
#	conn.commit()

	
