from config import config
from mysql.connector import MySQLConnection, connect, Error


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


def build_tweets_procedure(tweet_dict):
    '''
    Builds an array from the tweet dictionary to use as parameters for
    the db insert stored procedure
    '''
    arr = []
    #username
    arr.append(tweet_dict['username'])
    #description of user
    arr.append('None')
    #location
    arr.append(tweet_dict['location'] if tweet_dict['location'] is not None else 'None')
    #following
    arr.append(tweet_dict['following'])
    #followers
    arr.append(int(tweet_dict['followers']))
    #total tweets
    arr.append(int(tweet_dict['total_tweets']))
    #retweets
    arr.append(0)
    #hashtags
    arr.append('None')
    #tweet text
    arr.append(str(tweet_dict['text']))
    #created
    arr.append(tweet_dict['created'])
    #stock reference
    arr.append(0)

    return arr



def insert_tweets_db(conn, tweet_dict):
    '''
    Inserts tweets into the MySQL db retrieved from stream listener
    '''
    print(tweet_dict)
    if conn is None:
        config.LOGGER.error("No connection available to MySQL DB.")
        return
    if tweet_dict is None:
        config.LOGGER.error("No Data specified for DB insertion")
        return

    try:
        with conn.cursor() as cursor:
            vals = build_tweets_procedure(tweet_dict)
            result = cursor.callproc('Create_Twitter_Row', vals)
        conn.commit()
    except Exception as e:
        print(e)
        config.LOGGER.error(e)

