import os
from os.path import exists
import yfinance as yf
import pandas as pd
from pathlib import Path

offsetDays = 0
rowCounter = 10000
minScores = 1

#os.remove("zzz.csv")
df_list = list()
df_train = list()
df_test = list()

folderList = ["/Users/tymar/OneDrive/Documents/Capstone/Reddit/Sentiment Scores/", "/Users/tymar/OneDrive/Documents/Capstone/Twitter/Sentiment Scores/"]
for folderName in folderList:
    for path in Path(folderName).iterdir():
        pathString=str(path)
        pathArray = pathString.split('-')
        prevFileName = pathArray[0] + '-' + pathArray[1] + "-"
        month = pathArray[2]
        finalBits = pathArray[3].split('.')
        day = finalBits[0]
        #This is hacked for only december and novemeber data.  Needs cleanup for general use
        if day == "01":
            day = "30"
            month = str(int(month) - 1)
            if len(month) == 1:
                month = "0"+month
        else:
            day = int(day) - 1
            day = str(day)
            if len(day) == 1:
                day = "0" + day

        prevFileName = prevFileName + month + "-" + day + "." + finalBits[1]
        if exists(prevFileName):
            prevfileopen = open(prevFileName, "r")
            prevfileread = prevfileopen.read()
            prevfilerows = prevfileread.splitlines()
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
                        #scan previous day for ticker an save sentiment
                        tickerFound = 0
                        for indx in range(len(prevfilerows)):
                            prevFileRow = prevfilerows[indx].split(',')
                            if prevFileRow[2] == ticker:
                                tickerFound = 1
                                prevSentiment = prevFileRow[6]
                        #print(ticker)
                        try:
                            if (int(fileRow[7]) >= minScores) and (tickerFound == 1):
                                startdate = fileRow[1]
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


