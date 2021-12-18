from pathlib import Path
folderList = ["twitterscores", "RedditScores"]
for folderName in folderList:
    for path in Path(folderName).iterdir():
        print(path)
        fileopen = open(path, "r")
        fileread = fileopen.read()
        # using splitlines() function to display the contents of the file as a list
        fileRows = fileread.splitlines()
        for i in range(len(fileRows)):
            fileRow = fileRows[i]
            if fileRow != '':
                fileRow = fileRow.split(',')
                if fileRow[0] != 'source':
                    print(fileRow)
        break