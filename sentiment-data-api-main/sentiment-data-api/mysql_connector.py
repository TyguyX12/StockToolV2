from mysql.connector import connect, Error
import config
import json

def create_mysql_connection():
    '''
    Instantiates connection to the MySQL DB
    '''
    try:
        connection = connect(**config.DB_CONFIG)
        config.LOGGER.info(f"Connection to MySQL DB successfully established as user {config.MYSQL_USER}")
        return connection
    except Error as e: 
        config.LOGGER.info(e) 
        config.LOGGER.error("Error connecting to MySQL DB.")


def get_sentiment_data_ticker_db(ticker, type, source):
    conn = create_mysql_connection()
    if source is None or source == '':
        source = 'twitter'
    sql = f"""SELECT sentiment_scores FROM sentimentdata WHERE source = '{source}' AND sentiment_type = '{type}' ORDER BY created DESC LIMIT 1"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    config.LOGGER.info(result)
    try:
        if 'sentiment_scores' in result:
            try:
                scores = json.loads(result['sentiment_scores'])
                if ticker.upper() in scores:
                    return scores[ticker.upper()]
            except Exception as e:
                return e
            
            return "Ticker not available in sentiment scores"
        else:
            return "Problem retrieving sentiment scores"
    except Exception as e:
        return e



def get_sentiment_data_db_reddit(type):
    conn = create_mysql_connection()
    sql = f"""SELECT sentiment_scores FROM sentimentdata WHERE source = 'reddit' ORDER BY created DESC LIMIT 1"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    return result
    

def get_sentiment_data_db_twitter(type):
    conn = create_mysql_connection()
    sql = f"""SELECT sentiment_scores FROM sentimentdata WHERE source = 'twitter' AND sentiment_type = '{type}' ORDER BY created DESC LIMIT 1"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    return result




    