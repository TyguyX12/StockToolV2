import os

import yfinance as yf
import pandas as pd
from pathlib import Path

offsetDays = 0
rowCounter = 10000
minScores = 50

#os.remove("zzz.csv")
df_list = list()
df_train = list()
df_test = list()

#folderList = ["RedditScores", "twitterscores"]
#folderList = ["RedditScores"]#, "twitterscores"]
folderList = ["twitterscores"]#, ]
for folderName in folderList:
    for path in Path(folderName).iterdir():
        #print(path)
        fileopen = open(path, "r")
        fileread = fileopen.read()
        # using splitlines() function to display the contents of the file as a list
        fileRows = fileread.splitlines()
        for i in range(len(fileRows)):
            fileRow = fileRows[i]
            if fileRow != '':
                fileRow = fileRow.split(',')
                if fileRow[0] != 'source':
                    #print(fileRow)
                    ticker = fileRow[2]
                    #print(ticker)
                    try:
                        if int(fileRow[7]) >= minScores:
                            startdate = start = fileRow[1]
                            if offsetDays > 0:
                                startdate = pd.to_datetime(startdate) + pd.DateOffset(days=offsetDays)

                            enddate = pd.to_datetime(startdate) + pd.DateOffset(days=1)
                            data = yf.download(ticker, group_by="Ticker", start=startdate, end=enddate)
                            data['ticker'] = ticker  # add this column because the dataframe doesn't contain a column with the ticker
                            data['feed'] = fileRow[0]
                            data['score'] = fileRow[6] #add score
                            if float(fileRow[6]) < 0.0:
                                data['ABScomp'] = 0.0-float(fileRow[6])
                            else:
                                data['ABScomp'] = float(fileRow[6])
                            df_list.append(data)
                            df = pd.concat(df_list)
                            df.to_csv('ticker_data_single.csv')

                            with open('ticker_data_single.csv', 'r') as single:
                                myFile = single.read()
                            single.close()
                            os.remove('ticker_data_single.csv')
                            df_list = list()
                            lines = myFile.splitlines()
                            #line=lines[len(lines)-1].split(",")
                            line=lines[1].split(",")
                            changePercent = 100*(float(line[1])-float(line[4]))/float(line[1])
                            if changePercent < 0:
                                changePercent = 0-changePercent
                                data["pos/neg"] = "-"
                            else:
                                data["pos/neg"] = "+"

                            data['changePercent'] = changePercent

                            rowCounter = rowCounter + 1
                            if rowCounter % 5 == 0:
                                df_test.append(data)
                                test_df = pd.concat(df_test)
                                test_df.to_csv('OneDayTest.csv')
                            else:
                                df_train.append(data)
                                final_df = pd.concat(df_train)
                                final_df.to_csv('OneDayTrain.csv')



                    except:
                        print(ticker, startdate, enddate)


