#from app import app
import datetime
from logging import debug
import dash
import assets
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from index import app
import plotly.express as px

from dash.dependencies import ClientsideFunction
from dash.exceptions import PreventUpdate
from dash_daq import GraduatedBar, Gauge
from dash_extensions.enrich import (
    Input,
    Output,
    State,
    ServersideOutput,
    Trigger,
)
from numpy import True_

import requests
import json
import math
from bin import library as lib
import pandas as pd

timeframe_options = lib.get_timeframe_options()
source_options = lib.get_source_options()

layout = [
    dcc.Dropdown(
        id='select-source-db',
        options=source_options,
        value='yahoo_finance',
        clearable=False
    ),
    dcc.Dropdown(
        id='select-asset-db',
        clearable=False
    ),
    dbc.Card([
        #   Contains information about different indicators (since multiple may be selected at a given time)
        dbc.CardHeader(
            dcc.Tabs(id='sentiment-source-tab-db', value='Reddit', children=[
                dcc.Tab(label='Reddit', value='Reddit'),
                dcc.Tab(label='Twitter', value='Twitter')
            ])
        )
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id='numPost-chart-db')
        ], className="six columns"),

        html.Div([
            dcc.Graph(id='totalSentiment-chart-db')
        ], className="six columns"),
    ], className="row"),
    dcc.Store(id='session-sentiment-db', storage_type='session'),
    dcc.Store(id='session-numPost-chart-db', storage_type='session'),
    dcc.Store(id='session-totalSentiment-chart-db', storage_type='session')
]

@app.callback(
    [Output('select-asset-db', 'options'),
     Output('select-asset-db', 'value')],
    Input('select-source-db', 'value'),
)
def get_source_assets(source):
    if not source:
        raise PreventUpdate
    return lib.get_asset_options(source=source)

@app.callback(
     Output('session-sentiment-db', 'data'),
     [Input('select-asset-db', 'value'),
     Input('sentiment-source-tab-db', 'value')]
)
def get_sentiment(asset, sentimentSource):
    if not asset or not sentimentSource:
        raise PreventUpdate
    sentiment = lib.getSentimentDf(asset, sentimentSource)
    return sentiment

@app.callback(
    Output('numPost-chart-db', 'figure'),
    [Input('session-sentiment-db', 'modified_timestamp'),                #   on load
     Input('select-asset-db', 'value')],
    State('session-sentiment-db', 'data')
)
def create_numpost_graph(ts, asset, sentiment):
    if (sentiment is None):
        return []
    
    dates, negatives, neutrals, positives, totals, zeroes, negativeScores, neutralScores, positiveScores, compoundScores = [],[],[],[],[],[],[],[],[],[]

    for date in sentiment:
        dates.append(date)
        sentimentScores = sentiment[date]
        negatives.append(sentimentScores[5])
        neutrals.append(sentimentScores[6])
        positives.append(sentimentScores[7])
        totals.append(int(sentimentScores[5]) + int(sentimentScores[6]) + int(sentimentScores[7]))
        zeroes.append(0)

    positiveBar = {
        "x": dates,
        "y": positives,
        "name": 'Positives',
        "type": 'bar',
        "marker": {
            "color": 'rgb(140,200,100)'
        }
    }

    neutralBar = {
        "x": dates,
        "y": neutrals,
        "name": 'Neutrals',
        "type": 'bar',
        "marker": {
            "color": 'rgb(240,220,60)'
        }
    }

    negativeBar = {
        "x": dates,
        "y": negatives,
        "name": 'Negatives',
        "type": 'bar',
        "marker": {
            "color": 'rgb(230,70,70)'
        }
    }
    hoverOver = {
        "x": dates,
        "y": totals,
        "base": zeroes,
        "type": "bar",
        "name": "Total Posts",
        "showlegend": False,
        "opacity": 0,
    }
   
    data  = [negativeBar, neutralBar, positiveBar, hoverOver]

    title = asset[0 : -3] + " Post Counts"
    layout = {"barmode": 'stack', "title": title, "hovermode": "x unified" }

    return {"data": data, "layout": layout }


@app.callback(
    Output('totalSentiment-chart-db', 'figure'),
    [Input('session-sentiment-db', 'modified_timestamp'),                #   on load
     Input('select-asset-db', 'value')],
    State('session-sentiment-db', 'data')
)
def create_totalsentiment_graph(ts, asset, sentiment):
    if (sentiment is None):
        return []
    
    dates, datetimeDates, negativeScores, neutralScores, positiveScores, compoundScores = [], [],[],[],[],[]

    for date in sentiment:
        newDate = datetime.datetime.strptime(date, "%Y-%m-%d")
        dates.append(newDate.strftime("%b, %d, %Y"))
        datetimeDates.append(newDate)
        sentimentScores = sentiment[date]
        negativeScores.append(float(sentimentScores[0]))
        neutralScores.append(float(sentimentScores[1]))
        positiveScores.append(float(sentimentScores[2]))
        compoundScores.append(float(sentimentScores[3]))


    title = asset[0 : -3] + " Sentiment History"

    hoverData = {
        "Date": False,
        "Positive Score" : positiveScores,
        "Neutral Score" : neutralScores,
        "Negative Score": negativeScores
    }
    
    data = {'Date': datetimeDates, 'Compound Score': compoundScores}  
    df = pd.DataFrame(data)  

    # TODO, add customization of trend lines #
    scatter = px.scatter(df, x = "Date", y = "Compound Score", title = title, hover_name = dates, hover_data = hoverData , trendline="lowess", trendline_options=dict(frac=0.3))
    return scatter

