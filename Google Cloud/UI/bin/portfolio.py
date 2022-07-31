import json
from datetime import timedelta
import yfinance as yf
from google.cloud import storage

# credentials to get access google cloud storage
# write your key path in place of gcloud_private_key.json
storage_client = storage.Client.from_service_account_json('portfolio-key.json')
BUCKET = storage_client.get_bucket('portfolios-json')

def get_portfolios_json():
    '''
    this function will get the json object from
    google cloud storage bucket
    '''
    # get the blob
    blob = BUCKET.get_blob('portfolios.json')
    # load blob using json
    file_data = json.loads(blob.download_as_string())
    return file_data

# run the function and pass the filename which you want to get
portfolios = get_portfolios_json()

def save_portfolios():
    '''
    this function will create json object in
    google cloud storage
    '''
    # create a blob
    blob = BUCKET.blob('portfolios.json')
    # upload the blob 
    blob.upload_from_string(
        data=json.dumps(portfolios),
        content_type='application/json'
        )


def initialize():
    global portfolios

    portfolioOptions = []
    firstPortfolioValue = None

    portfolioOptions = getPortfolioOptions()
    if len(portfolioOptions) == 0:
        return [], None, [], None

    firstPortfolioValue = list(portfolioOptions)[0]["value"]
    stocksInPortfolio = getStockInPortfolioOptions(firstPortfolioValue)

    if len(stocksInPortfolio) == 0:
        return portfolioOptions, firstPortfolioValue, [], None
        
    firstStockInPortfolioValue = list(stocksInPortfolio)[0]["value"]

    return portfolioOptions, firstPortfolioValue, stocksInPortfolio, firstStockInPortfolioValue

 
def getPortfolios():
    global portfolios
    return portfolios

def getPortfolioOptions():
    global portfolios
    options = []
    for portfolio in portfolios:
        portfolioOption = {'label': portfolio, 'value': portfolio}
        options.append(portfolioOption)

    return options


def getPortfolioList():
    global portfolios
    portfolioList = list(portfolios.keys())
    return portfolioList

def getStockInPortfolioOptions(chosenPortfolio):
    global portfolios
    if chosenPortfolio is None:
        return []
    options = []
    for stock in portfolios[chosenPortfolio]["stocks"]:
        stockOption = {'label': portfolios[chosenPortfolio]['stocks'][stock], 'value': stock}
        options.append(stockOption)

    return options

def getStocksInPortfolio(chosenPortfolio):
    global portfolios
    values = []
    labels = []
    for stock in portfolios[chosenPortfolio]["stocks"]:
        values.append(stock)
        labels.append(portfolios[chosenPortfolio]['stocks'][stock])
    return values, labels

def getStockAmount(stock, portfolio):
    global portfolios
    amountVol = portfolios[portfolio]['amounts'][stock]

    return amountVol


def getStockPurchaseDate(stock, portfolio):
    global portfolios    
    date = portfolios[portfolio]['purchase_dates'][stock]
    return date

def addStockToPortfolio(amount, date, stockSymbol, stockName, portfolioName):
    global portfolios
    date = str(date)
    if stockSymbol in portfolios[portfolioName]["stocks"]:
        return
    
    portfolios[portfolioName]["stocks"][stockSymbol] = stockName
    portfolios[portfolioName]["amounts"][stockSymbol] = amount
    portfolios[portfolioName]["purchase_dates"][stockSymbol] = date
    save_portfolios()


def deleteStockFromPortfolio(portfolio, stockSymbol):
    global portfolios
    try:
        del portfolios[portfolio]["stocks"][stockSymbol]
        del portfolios[portfolio]["amounts"][stockSymbol]
        del portfolios[portfolio]["purchase_dates"][stockSymbol]
    except:
        pass
    save_portfolios()

def createNewPortfolio(newPortfolioName):
    global portfolios
    if newPortfolioName in portfolios:
        return
    
    portfolios[newPortfolioName] = {"stocks": {}, "amounts": {}, "purchase_dates": {}}
    save_portfolios()

def deletePortfolio(portfolio):
    global portfolios
    try:
        del portfolios[portfolio]
    except:
        pass
    save_portfolios()

def getPortfolioData(stock, portfolio):
    stockLabel = stock[:-3]
    volume = ("%.2f" % getStockAmount(stock, portfolio))
    
    purchaseDate = getStockPurchaseDate(stock, portfolio)
    yfData = yf.download(stockLabel, start=purchaseDate)
    yfData = yfData.dropna()
    initialPrice = yfData["Adj Close"].tolist()[0]
    currentPrice = yfData["Adj Close"].tolist()[-1]

    valueChange = currentPrice - initialPrice
    valueChangePercent = (valueChange / currentPrice) * 100
    pfValueChange = valueChange * float(volume)

    if float(valueChange) > 0:
        valueChangeLabelColor = "green"
    elif float(valueChange) < 0:
        valueChangeLabelColor = "red"
    else:
        valueChangeLabelColor = "gray"

    currentPrice = "${:,.2f}".format(currentPrice)
  
    valueChangePercent = "{:+.2f}".format(valueChangePercent) + "%"
    pfValueChange = "{:+.2f}".format(pfValueChange)
    pfValueChange = pfValueChange[0] + "$" + pfValueChange[1:]
    
    return stockLabel, volume, purchaseDate, initialPrice, currentPrice, valueChangePercent, pfValueChange, valueChangeLabelColor

if __name__ == '__main__':
    getPortfolioData("AAPL-tr", "Tyler")
