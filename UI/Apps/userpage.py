from app import app
import requests
import math
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import json

import bin.library as lib

from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
from dash_daq import GraduatedBar, Gauge
from dash_extensions.enrich import (
    Input,
    Output,
    State,
    ServersideOutput,
    Trigger,
)

lib.save_portfolios()

indicator_options = lib.get_indicator_options()
timeframe_options = lib.get_timeframe_options()

portfolio_options = lib.get_portfolio_options()
stock_in_portfolio_options = lib.get_stock_in_portfolio_options(0)
source_options = lib.get_source_options()

prevSignInClicks = 0
prevAddClicks = 0
prevDeleteClicks = 0
prevAddPortfolioClicks = 0
prevDeletePortfolioClicks = 0

portfolioIndex=0
stockIndex=0

sentiment_list = {}

layout = [
  
  dcc.Input(className= 'sign-in', id='username'),
  html.Label("Username:", className= 'sign-in'),
  
  html.Br(),
  html.Br(),

  dcc.Input(className = 'sign-in', type='password', id='password'),
  html.Label("Password:", className= 'sign-in'),


  html.Br(),
  html.Br(),

  html.Button('Sign In', className = 'sign-in', id='sign-in', n_clicks=0),

  html.Br(),
  html.Br(),

  html.H1('STOCK TOOL'),

  html.Br(),
  html.Br(),

  html.Div(className="line"),
  
  html.Div([
    
    html.Br(),
    html.H2('View Stock Data'),

    html.Div([

      dcc.Dropdown(
        className='small-dropdown',
        id='select-source',
        options=source_options,
        value='yahoo_finance',
        clearable=False
      ),

      dcc.Dropdown(
        className='large-dropdown',
        id='select-asset',
        clearable=False
      ),

      html.Button('Add to Portfolio', className = 'user-button', id='add-stock-to-portfolio', n_clicks=0),

    ], className='graph-header', style=dict(display='flex')),
    
    
    html.Div([
      html.Div([

        dcc.Dropdown(
          className='small-dropdown',
          id='select-timeframe',
          options=timeframe_options,
          value='week',
          clearable=False
        ),

        html.Br(),

        dcc.Dropdown(
          className='large-dropdown',
          id='select-indicators',
          options=indicator_options,
          value=['ema'],
          multi=True,
          clearable=True,
        ),
      ], className='graph-dropdowns'),

      dcc.Graph(
            id='chart',
            className='user-chart',
        ),

      html.Div([
        
        Gauge(id = "compound-user", min=-1, max=1, value=0.1, color="green", className='compound-guage'),
        html.Label("Compound For Stock", className='compound-guage-label'),

      ],className = "compound-div"),
      

    ], style=dict(display='flex')),

    html.Br(),

    html.Div([

      dbc.Card([
          dbc.CardHeader(
              dcc.Tabs(id='indicator-form-tabs')
          ),
          dbc.CardBody(
              dbc.Form(id='indicator-form')    
          )
      ]),

    ], className='user-cards', style=dict(display='flex')),
    

    html.Br(),
    html.Br(),

    html.Div(className="line"),

    html.Br(),
    html.Br(),

    html.H2('View Portfolio Sentiment'),

    html.Br(),
    html.Br(),


    html.Div([

      html.Div([

        dcc.Dropdown(
          className='small-dropdown',
          id='select-portfolio',
          options=portfolio_options,
          clearable=False
        ),
        html.Button('Delete Portfolio', className = 'user-button', id='delete-portfolio', n_clicks=0),
        
      ], style=dict(display='flex')),
      
      html.Div([
        dcc.Input(id='new-portfolio-name'),
        html.Button('Add Portfolio', className = 'user-button', id='add-portfolio', n_clicks=0)
      ], className="right-align"),

   ], style=dict(display='flex')),

    html.Br(),
    html.Br(),

    html.Div([

      html.Button('Refresh Sentiment Analysis for Portfolio',id="refresh-sentiment-users", className = 'user-button', n_clicks = 0),

      html.Div([

        dcc.Dropdown(
          className='large-dropdown',
          id='select-stocks',
          options=stock_in_portfolio_options,
          clearable=True
       ),

       html.Button('Delete from Portfolio', className = 'user-button', id='delete-stock-from-portfolio', n_clicks=0)

      ], className="right-align", style=dict(display='flex')),

    ]),


    html.Br(),
    html.Br(),


    html.Div(
          id="sentiment-card-users",
          children=[
              html.Div(
                  children=[
                      dcc.Loading(dcc.Store(id="sentiment-users")),
                      html.Div(
                          id="sentiment-scores-users",
                          children=[
                              html.Div(
                                  [
                                      html.Label("Twitter"),
                                      html.Ul(id="sentiment-scores-twitter-users"),
                                  ]
                              ),
                              html.Div(
                                  [
                                      html.Label("Reddit"),
                                      html.Ul(id="sentiment-scores-reddit-users"),
                                  ]
                              ),
                          ],
                      ),
                  ],
              )
          ], 
        className="compound-div"),
    html.Div(className="line"),
  ], className="tool"),

  
  dcc.Store(id='session-candles', storage_type='session'),
  dcc.Store(id='session-volume', storage_type='session'),
  dcc.Store(id='session-indicators-runs', storage_type='session'),
  dcc.Store(id='session-indicators-forms', storage_type='session'),
  dcc.Store(id='session-indicators', storage_type='session'),
  dcc.Store(id='session-user-indicator', storage_type='session'),
  dcc.Store(id='session-chart', storage_type='session')

]
@app.callback(
  [Output('select-portfolio', 'options'),
  Output('select-portfolio', 'value'),
  Output('select-stocks', 'options'),
  Output('select-stocks', 'value')],
  [Input('sign-in', 'n_clicks'), # get sign in button clicks (sign_in_clicks)
  Input('add-stock-to-portfolio', 'n_clicks'), # get add button clicks (add_clicks)
  Input('delete-stock-from-portfolio', 'n_clicks'), # get delete button clicks (delete_clicks)
  Input('add-portfolio', 'n_clicks'), # get add portfolio button clicks (add_portfolio_clicks)
  Input('delete-portfolio', 'n_clicks'), # get delete portfolio button clicks (delete_portfolio_clicks)
  Input('select-portfolio', 'value')], # which portfolio is selected (chosenPortfolio)
  [State('username', 'value'), # user name typed in (username-input)
  State('password', 'value'), # password typed in (password-input)
  State('select-stocks', 'value'), # which stock is selected in the portfolio (chosen_stock_value)
  State('select-asset', 'value'), # which stock is to be added to the selection (newStockValue)
  State('select-portfolio', 'options'), # options of portfolios to be added (portfolio_options)
  State('new-portfolio-name', 'value'), # name typed in to the new portfolio input (new_portfolio_name)
  State('select-stocks', 'options'), #options of stocks within portfolio (stock_in_portfolio_options)
  State('select-asset', 'options')] # options of stocks to be added (asset_options)

  )
def update_stocks_and_portfolios(sign_in_clicks, add_clicks, delete_clicks, add_portfolio_clicks, delete_portfolio_clicks, chosenPortfolio, username_input, password_input, chosen_stock_value, new_stock_value, portfolio_options, new_portfolio_name, stock_in_portfolio_options, asset_options):
  global portfolioIndex
  global stockIndex
  portfolioIndex = next((i for i, item in enumerate(portfolio_options) if item["value"] == chosenPortfolio), None)
  handleSignInClicked(sign_in_clicks, username_input, password_input)  
  handleAddButtonClicked(add_clicks, portfolioIndex, new_stock_value, asset_options)
  handleDeleteButtonClicked(delete_clicks, portfolioIndex, chosen_stock_value)  
  handleAddPortfolioClicked(add_portfolio_clicks, new_portfolio_name) 
  handleDeletePortfolioClicked(delete_portfolio_clicks, chosenPortfolio, portfolio_options) 
  
  portfolio_options = lib.get_portfolio_options()
  portfolioIndex = next((i for i, item in enumerate(portfolio_options) if item["value"] == chosenPortfolio), None)
    
  if (not portfolio_options):
    return [], "", [], ""

  if (not chosenPortfolio or portfolioIndex is None):
    return portfolio_options, "", [], ""

  stock_in_portfolio_options = lib.get_stock_in_portfolio_options(portfolioIndex)
  
  if(not stock_in_portfolio_options):
    return portfolio_options, portfolio_options[portfolioIndex]["value"], [], ""
  else:
    getPortfolioSentiment(stock_in_portfolio_options)
    return portfolio_options, portfolio_options[portfolioIndex]["value"], stock_in_portfolio_options, stock_in_portfolio_options[stockIndex]["value"]

def handleSignInClicked(sign_in_clicks, username, password):
  global prevSignInClicks
  if (prevSignInClicks < sign_in_clicks and sign_in_clicks > 0):
    lib.sign_in(username,password)

def handleAddPortfolioClicked(add_portfolio_clicks, new_portfolio_name):
  global prevAddPortfolioClicks
  global portfolioIndex
  newPortfolio = True
  for p in lib.user["portfolios"]:
      if (p["name"] == new_portfolio_name):
        newPortfolio = False
  if (prevAddPortfolioClicks < add_portfolio_clicks and add_portfolio_clicks > 0 and newPortfolio):
    if (new_portfolio_name):
      new_portfolio = {"name": new_portfolio_name,"stocks": []}
      L1=list(lib.user["portfolios"])
      L1.append(new_portfolio)
      T1=tuple(L1)
      lib.user["portfolios"] = T1
      prevAddPortfolioClicks = add_portfolio_clicks
      lib.save_portfolios()
      portfolioIndex = len(L1)-1

def handleDeletePortfolioClicked(delete_portfolio_clicks, chosenPortfolio, portfolio_options):
  global prevDeletePortfolioClicks
  global portfolioIndex
  if (chosenPortfolio and prevDeletePortfolioClicks < delete_portfolio_clicks):
    if (delete_portfolio_clicks > 0):
      portfolioIndex = next((i for i, item in enumerate(portfolio_options) if item["value"] == chosenPortfolio), None)
      L1=list(lib.user["portfolios"])
      L1.remove(L1[portfolioIndex])
      T1=tuple(L1)
      lib.user["portfolios"] = T1
      prevDeletePortfolioClicks = delete_portfolio_clicks
      lib.save_portfolios()
      portfolioIndex = 0
        
def handleAddButtonClicked(add_clicks, portfolioIndex, new_stock_value, asset_options):
  global prevAddClicks
  global stockIndex
  if (add_clicks > prevAddClicks and portfolioIndex is not None):
    newStock = True
    assetIndex = next((i for i, item in enumerate(asset_options) if item["value"] == new_stock_value), None)
    newLabel = asset_options[assetIndex]["label"] #Label given by label of first stock in options with matching value
    newValue = asset_options[assetIndex]["value"] #Value given by label of first stock in options with matching value
    for p in lib.user["portfolios"][portfolioIndex]["stocks"]:
      if (p["value"] == newValue):
        newStock = False

    if (newStock and add_clicks > 0):
      L1=list(lib.user["portfolios"][portfolioIndex]["stocks"])
      L1.append({'name': newLabel, 'value' : newValue})
      T1=tuple(L1)
      lib.user["portfolios"][portfolioIndex]["stocks"] = T1

      prevAddClicks = add_clicks
      lib.save_portfolios()
      stockIndex = len(L1)-1

def handleDeleteButtonClicked(delete_clicks, portfolioIndex, chosen_stock_value):
  global prevDeleteClicks
  global stockIndex
  if (delete_clicks > prevDeleteClicks and chosen_stock_value):
    if (delete_clicks > 0):
      L1=list(lib.user["portfolios"][portfolioIndex]["stocks"])
      assetIndex = next((i for i, item in enumerate(L1) if item["value"] == chosen_stock_value), None)
      L1.remove(L1[assetIndex])
      T1=tuple(L1)
      lib.user["portfolios"][portfolioIndex]["stocks"] = T1
      prevDeleteClicks = delete_clicks
      lib.save_portfolios()
      stock_in_portfolio_options = lib.get_stock_in_portfolio_options
      stockIndex = 0

def getPortfolioSentiment(stock_in_portfolio_options):
  global sentiment_list
  sentiment_list = []
  counter = 0
  for stock in stock_in_portfolio_options:
    valString = stock['value']
    sentiment_list.append(valString[0:-3])
    counter = counter + 1

@app.callback(
    ServersideOutput("sentiment-users", "data"), Input("refresh-sentiment-users", "n_clicks"), memoize=True
)
def initialize_sentiment(clicks):
    sentiment = SentimentUsers()
    sentiment.build()
    return sentiment

#@app.callback(
    #ServersideOutput("sentiment-users", "data"), Trigger("refresh-sentiment-users", "n_clicks"), memoize=True
    #Input("refresh-sentiment-users", "n_clicks"),
    #State("sentiment-users", "data"),
#)
#def refresh(clicks):
# if (clicks > 0):
#    sentiment = SentimentUsers()
#    if not sentiment:
#      raise PreventUpdate


@app.callback(
    [
        Output("sentiment-scores-twitter-users", "children"),
        Output("sentiment-scores-reddit-users", "children"),
    ],
    [
        Input("sentiment-users", "data"),
        Input("refresh-sentiment-users", "n_clicks")
    ],
        
  )
def sentiment_leaderboards(sentiment, clicks):
    if not sentiment:
        raise PreventUpdate
    return sentiment.leaderboard("hourly", "twitter"), sentiment.leaderboard(
        "hourly", "reddit"
    )

def get_sentiment_data():
    sentiment = {}
    for timeframe in ["daily", "weekly", "hourly"]:
        sentiment[timeframe] = {}
        for social in ["twitter", "reddit"]:
            t = {"type": timeframe}
            payload = json.dumps(t)
            url = f"http://45.33.127.174//get_sentiment_data_{social}"
            headers = {"Content-Type": "text/plain"}
            try:
                response = requests.request(
                    "GET", url, headers=headers, data=payload)
                raw = json.loads(response.text)
                sentiment[timeframe][social] = json.loads(
                    raw["sentiment_scores"])
            except Exception as e:
                #app.logger.error(
                    #f"Failed to collect sentiment {e}: {social} {timeframe}"
                #)
                continue
    return sentiment

@app.callback(
    Output("compound-user", "value"),
    Input("select-asset", "value")
)
def set_compound(selectedAsset):
  valString = selectedAsset[0:-3]
  return get_compound(valString)

def get_sentiment_data_ticker():
  global sentiment_list
  sentiment = {}
  for timeframe in ["daily", "weekly", "hourly"]:
    sentiment[timeframe] = {}
    for social in ["twitter", "reddit"]:
      sentiment[timeframe][social] = {}
      for asset in sentiment_list:   
        payload = json.dumps({"type": timeframe, "ticker": asset, "source": social})
        url = f"http://45.33.127.174//get_sentiment_data_ticker"
        headers = {"Content-Type": "text/plain"}
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            raw = json.loads(response.text)
            sentiment[timeframe][social][asset] = raw
        except Exception as e:
            raw = {'compound': '0.000', 'neg': '0.000', 'neu': '0.000', 'pos' : '0.000'}
            sentiment[timeframe][social][asset] = raw
            #app.logger.error(f"Failed to collect sentiment {e}: {asset}")
  return sentiment

def get_compound(asset):
  timeframe = "hourly"
  social = "reddit"  
  payload = json.dumps({"type": timeframe, "ticker": asset, "source": social})
  url = f"http://45.33.127.174//get_sentiment_data_ticker"
  headers = {"Content-Type": "text/plain"}
  try:
    response = requests.request("GET", url, headers=headers, data=payload)
    raw = json.loads(response.text)
    compound = float(raw['compound'])
    
  except Exception as e:
    compound = 0.000
    #app.logger.error(f"Failed to collect sentiment {e}: {asset}")
  return compound


class SentimentUsers:
    def __init__(self):
        self._sentiment = get_sentiment_data_ticker
        #self._fetch = get_sentiment_data_ticker
        self.data = {}
        self.build()

    def _to_frame(self, t, s):
        
        df = pd.DataFrame.from_records(self.data[t][s]).transpose()
        self.data[t][s] = df

    def _sentiment_item(self, p, color):
        return html.Div(
            className="sentiment-item",
            children=[
                html.Label(className="graduated-label", children=f"{p}%"),
                GraduatedBar(
                    value=p,
                    max=100,
                    min=0,
                    color={"ranges": {color: [0, p]}},
                ),
            ],
        )

    def _sentiment_row(self, scores):
        return html.Li(
            html.Div(
                className="sentiment-row",
                children=[
                    html.Label(className="sentiment-ticker",
                               children=scores.Index),
                    self._sentiment_item(scores.pos, "green"),
                    self._sentiment_item(scores.neg, "red"),
                    self._sentiment_item(scores.neu, "blue"),
                ],
            )
        )

    def leaderboard(self, t, s):
        d = self.data[t][s]
        d = d.applymap(lambda x: math.floor(float(x) * 100))
        header = [
            html.Li(
                [
                    html.Label(),
                    html.Label("Bullish"),
                    html.Label("Bearish"),
                    html.Label("Neutral"),
                ],
                className="sentiment-row",
            )
        ]
        return header + [self._sentiment_row(score) for score in d.itertuples()]

    def build(self):
        self.data = self._sentiment()
        for t in ["hourly", "daily", "weekly"]:
            for s in ["reddit", "twitter"]:
                self._to_frame(t, s)

    def fetch(self, asset, timeframe):
        return self._fetch(asset=asset, timeframe=timeframe)

    @property
    def reddit(self):
        return {t: d["reddit"] for t, d in self.data.items()}

    @property
    def twitter(self):
        return {t: d["twitter"] for t, d in self.data.items()}
