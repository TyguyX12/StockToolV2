import os
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('/home/stocktool/envs/ci.env')

load_dotenv(dotenv_path=dotenv_path)

MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PSWD = os.getenv('MYSQL_PSWD')

DB_CONFIG = {
    'host': 'localhost',
    'user': MYSQL_USER,
    'password': MYSQL_PSWD,
    'database': 'StockToolDB'
}

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


LOGGER = __create_logger('/home/stocktool/logs/sentiment_api.log')
