import json
import os
import random
import sys
import time
import datetime

from sentiment import twitter_sentiment as ts
from sentiment import reddit_sentiment as rs

# Retrieve Job-defined env vars
TASK_INDEX = os.getenv("CLOUD_RUN_TASK_INDEX", 0)
TASK_ATTEMPT = os.getenv("CLOUD_RUN_TASK_ATTEMPT", 0)


# Define main script
def main():
    print(f"Starting Task #{TASK_INDEX}, Attempt #{TASK_ATTEMPT}...")
    
    print("Running Sentiment Analysis")
    TODAY = datetime.date.today()
    tw = ts.TwitterSentiment()
    tw.run_for_date(TODAY) 
    rd = rs.RedditSentiment()              
    rd.run_for_date(TODAY)

    print(f"Completed Task #{TASK_INDEX}.")

# Start script
if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        message = f"Task #{TASK_INDEX}, "
        + f"Attempt #{TASK_ATTEMPT} failed: {str(err)}"

        print(json.dumps({"message": message, "severity": "ERROR"}))
        sys.exit(1)  # Retry Job Task by exiting the process
