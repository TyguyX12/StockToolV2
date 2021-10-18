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


def gather_tweets_from_db(conn, sentiment_type):
    '''
    Gathers all tweets from a particular date in dictionary form
    '''
    col_name = 'processed' if sentiment_type != 'weekly' and sentiment_type != 'daily' else 'processed_{}'.format(sentiment_type)
    sql = """SELECT * FROM twitterdata WHERE {} = 'N'""".format(col_name)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    return cursor


def update_processed_col(conn, tweet_ids, sentiment_type):
    '''
    Updates the rows which have been processed with processed = 'Y'
    '''
    col_name = 'processed' if sentiment_type != 'weekly' and sentiment_type != 'daily' else 'processed_{}'.format(sentiment_type)
    tweet_ids = tuple(tweet_ids)
    sql = f"""UPDATE twitterdata SET {col_name} = 'Y' WHERE idTwitterData IN {tweet_ids}"""
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.commit()


def insert_sentiment_scores(conn, scores, source, sentiment_type):
    '''
    Inserts sentiment scores into sentimentdata table
    '''
    sql = """INSERT INTO sentimentdata (sentiment_scores, source, sentiment_type) VALUES (%s, %s, %s)"""
    sentiment_data = (json.dumps(scores), source, sentiment_type)
    cursor = conn.cursor()
    cursor.execute(sql, sentiment_data)
    cursor.close()
    conn.commit()

        
