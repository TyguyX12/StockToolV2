import os
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('/home/stocktool/envs/ci.env')

load_dotenv(dotenv_path=dotenv_path)


def __create_logger(path):
    '''
    Creates Timed Rotating Log
    '''
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    
    handler = TimedRotatingFileHandler(path,
                                       when="m",
                                       interval=10080,
                                       backupCount=5)
    logger.addHandler(handler)

    return logger


#instantiates loger
LOGGER = __create_logger('/home/stocktool/logs/twitter_stream.log')

#Twitter api creds loaded from env variables
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

#db config also loaded from env variables
DB_CONFIG = {
    'host': 'localhost',
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PSWD'),
    'database': 'StockToolDB',
    'charset': 'utf8mb4'
}

