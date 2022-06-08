# Sentiment Analysis (OUTDATED)

This is the code for the sentiment analysis. This code may be turned into a Windows Service that runs at a specific time each day.
The Twitter and Reddit analyzers work in different ways:
Twitter analysis runs though a CSV of Tweets that have been collected through a stream controlled by a Windows Service
Reddit analysis runs through the top posts on specific subreddits each day. This must be done daily, and it is TBD when the best time to do this would be
The config file is the same as the one for the TwitterStream, as the same information is important for both files, such as flairs and stock names.
