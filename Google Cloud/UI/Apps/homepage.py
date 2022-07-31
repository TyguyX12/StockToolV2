import datetime
import plotly.express as px
import pandas as pd

from dash import dcc, html 
from dash import callback_context as ctx

import dash_bootstrap_components as dbc
from index import app

from dash.dependencies import ClientsideFunction
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import (
Input,
Output,
State,
)

from bin import library as lib
from bin import sentiment as sent

timeframe_options = lib.get_timeframe_options()
indicator_options = lib.get_indicator_options()
source_options = lib.get_source_options()

layout = [
    html.Br(),
    html.H1('Homepage'),
    html.Div(className="line"),
    html.Br(),
    html.Div(className = "vertical-flex-div", children = [
        html.Div(className = "horizontal-flex-div", children = [
            dcc.Dropdown(
                #   Source may be yahoo_finance or alpha_vantage. 
                id='select-source',
                className="medium-dropdown",
                options=source_options,
                value='yahoo_finance',
                clearable=False
            ),
            dcc.Dropdown(
                #   Stock names & Symbols stored in static folder
                #   May be used for more rigerous data collection, if necessary
                id='select-asset',
                className="medium-dropdown",
                clearable=False
            )
        ]),
        dcc.Dropdown(
            #   Timeframe may be month, week, or day, changes amount of time in a single ticker
            id='select-timeframe',
            className="medium-dropdown",
            options=timeframe_options,
            value='day',
            clearable=False
        )
    ]),
    html.Br(),

    html.Div(className='wide', children = [
        dcc.Graph(
            #   Chart displays all of the stock information
            id='chart',
            className='homepage-chart',
        )
    ]),

    
    dbc.Card(class_name = 'wide', children = [
        dcc.Dropdown(
            placeholder="Select Indicators",
            id='select-indicators',
            options=indicator_options,
            value=[],
            multi=True,
            clearable=True,
        ),
        dbc.CardHeader(
            dcc.Tabs(id='indicator-form-tabs')
        ),
        dbc.CardBody(
            dbc.Form(id='indicator-form')
        )
    ]),

    html.Br(),

    dbc.Card(class_name = 'wide', children=[
        dbc.CardHeader(
            dcc.Tabs(id='sentiment-source-tab', value='twitter', children=[
                dcc.Tab(className='tab', selected_className='selected-tab', label='Twitter', value='twitter'),
                dcc.Tab(className='tab', selected_className='selected-tab', label='Reddit', value='reddit')
            ])
        ),
        dbc.CardBody([
            html.Div([
                html.Div([
                    dcc.Graph(id='numPost-chart')
                ], className="six columns"),
                html.Div([
                    dcc.Graph(id='totalSentiment-chart')
                ], className="six columns"),
            ], className="row")
        ])
    ]),
   
    dcc.Store(id='session-candles'),
    dcc.Store(id='session-volume'),
    dcc.Store(id='session-indicators-runs'),
    dcc.Store(id='session-indicators-forms'),
    dcc.Store(id='session-indicators'),
    dcc.Store(id='session-user-indicator'),
    dcc.Store(id='session-chart'),
    dcc.Store(id='session-sentiment'),
    dcc.Store(id='session-numPost-chart'),
    dcc.Store(id='session-totalSentiment-chart')
]

#   get_source_assets(source):
#   Gets all of the stock symbols from one of two sources (Yahoo Finance or Alpha Vantage)
#   Returns these stock symbols as a list of options for the select_asset dropdown
@app.callback(
    [Output('select-asset', 'options'),
     Output('select-asset', 'value')],
    Input('select-source', 'value')
)
def get_source_assets(source):
    ctxMessage = "Get assets: " + str(ctx.triggered)
    #print(ctxMessage)
    if not source:
        raise PreventUpdate
    return lib.get_asset_options(source=source)

#   Gets candles for the stock price history graph
#   Candles contain: date, open, high, low, close
#   Also currently gathers sentiment data since most sentiment activity is done client-side
@app.callback(
    [Output('session-chart', 'clear_data'),
     Output('session-volume', 'data'),
     Output('session-candles', 'data')],
    [Input('select-source', 'value'),
     Input('select-asset', 'value'),
     Input('select-timeframe', 'value')]
)
def get_candles(source, asset, timeframe):
    if not asset or not source or not timeframe:
        raise PreventUpdate
    volume, candles = lib.get_volume_candles(source, asset, timeframe)

    return True, volume, candles.to_dict('list')


#   get_indicator_stages(indicators):
#   Takes in the selections from the indicator dropdowns to get the indicators-runs and indicators-forms data
@app.callback(
    [Output('session-indicators-runs', 'data'),
     Output('session-indicators-forms', 'data')],
    Input('select-indicators', 'value'),
)
def get_indicator_stages(indicators):
    if not indicators:
        return {}, {}
    runs, forms = lib.stage_indicators(indicators=indicators)
    return runs, forms

#   run_indicators(its, cts, uts, info, candles, volume, user_args):
#   Takes in all of the indicator data and uses it to populate the session-indicators data
@app.callback(
    Output('session-indicators', 'data'),
    [Input('session-indicators-runs', 'modified_timestamp'),                #   on load
     Input('session-candles', 'modified_timestamp'),                        #   on load
     Input('session-user-indicator', 'modified_timestamp')],                #   on load
    [State('session-indicators-runs', 'data'),
     State('session-candles', 'data'),
     State('session-volume', 'data'),
     State('session-user-indicator', 'data')]
)
def run_indicators(its, cts, uts, info, candles, volume, user_args):
    if not info:
        return {}
    if not candles:
        raise PreventUpdate
    if not user_args:
        return lib.run_indicators(info, candles, volume)
    else:
        test = lib.run_indicators(info, candles, volume, user_args=user_args)
        return lib.run_indicators(info, candles, volume, user_args=user_args)

#   create_indicator_tabs(ts, forms):
#   Uses the session-indicators-forms data to create tabs for the different indicators
@app.callback(
    [Output('indicator-form-tabs', 'children'),
     Output('indicator-form-tabs', 'value')],
    Input('session-indicators-forms', 'modified_timestamp'),                #   on load
    State('session-indicators-forms', 'data')
)
def create_indicator_tabs(ts, forms):
    children, value = [], None

    if not forms:
        return children, value
    
    for indicator, form in forms.items():

        if value is None:
            value = indicator

        tab = dcc.Tab(className='tab', selected_className='selected-tab', label=form['name'], value=indicator)
        children.append(tab)

    return children, value

#   create_indicator_forms(indicator, info):
#   Uses the indicator-form-tabs and the session-indicators-forms to create the indicator-form
@app.callback(
    Output('indicator-form', 'children'),
    Input('indicator-form-tabs', 'value'),
    State('session-indicators-forms', 'data')
)
def create_indicator_forms(indicator, info):
    
    if not indicator or not info:
        return []

    i = info[indicator]
    if i['options'] == [] or i['defaults'] == None:
        return []

    form_children = []

    for option, default in zip(i['options'], i['defaults']):
        form_children.extend([
            dbc.Label(option),
            html.Br(),
            dbc.Input(type='number', placeholder=default),
            html.Br()
        ])
    submit_button = dbc.Button('Submit', type='submit', key=str(indicator))
    form_children.append(submit_button)
    return form_children

#   parse_inputs(ts, children, indicator):
#   When the button is pressed, take in the information from the indicator-form and update the session-user-indicator data
@app.callback(
    Output('session-user-indicator', 'data'),
    Input('indicator-form', 'n_submit_timestamp'),
    State('indicator-form', 'children'),
    State('indicator-form-tabs', 'value')
)
def parse_inputs(ts, children, indicator):
    if not children or not indicator:
        raise PreventUpdate

    key = [i['props']['key'] for i in children if i['type'] == 'Button']
    
    fields = [i['props'] for i in children if i['type'] == 'Input']
    args = [i['value'] if i.get('value', False)
            else i['placeholder'] for i in fields]
    return {indicator: args}

@app.callback(
    [Output('session-numPost-chart', 'clear_data'),
     Output('session-totalSentiment-chart', 'clear_data'),
     Output('session-sentiment', 'data')],
    [Input('select-asset', 'value'),
     Input('sentiment-source-tab', 'value')]
)
def get_sentiment(asset, sentimentSource):
    ctxMessage = "Get Sentiment: " + str(ctx.triggered)
    #print(ctxMessage)
    if not asset or not sentimentSource:
        raise PreventUpdate
    try:
        sentiment = sent.getSentimentDf(asset, sentimentSource)
    except:
        sentiment = None
    return True, True, sentiment

#   create_graph:
#   Takes in the data and uses js to create the graph client-side
app.clientside_callback(
    ClientsideFunction('clientside', 'create_graph'),
    Output('session-chart', 'data'),
    [Input('session-candles', 'modified_timestamp'),           #   on load
     Input('session-indicators', 'modified_timestamp')],
    [State('session-candles', 'data'),
     State('session-indicators', 'data')]
)

#   display_graph:
#   Takes in the data and uses js to disply the graph client-side
app.clientside_callback(
    ClientsideFunction('clientside', 'display_graph'),
    Output('chart', 'figure'),
    [Input('session-chart', 'modified_timestamp'),                   #   on load
     Input('session-indicators', 'modified_timestamp')],
    [State('session-chart', 'data'),
    State('select-asset', 'value'),
    State('session-indicators', 'data')
    ]
)

#   create_sentiment_graph:
#   Takes in the data and uses js to create the graph client-side
app.clientside_callback(
    ClientsideFunction('clientside', 'create_numpost_graph'),
    Output('session-numPost-chart', 'data'),
    Input('session-sentiment', 'modified_timestamp'),
    State('session-sentiment', 'data')
)

app.clientside_callback(
    ClientsideFunction('clientside', 'display_numpost_graph'),
    Output('numPost-chart', 'figure'),
    Input('session-numPost-chart', 'modified_timestamp'),
    [State('session-numPost-chart', 'data'),
    State('select-asset', 'value')]
)

@app.callback(
    Output('totalSentiment-chart', 'figure'),
    Input('session-totalSentiment-chart', 'modified_timestamp'),
    [State('session-sentiment', 'data'),
    State('select-asset', 'value')]
)
def create_totalsentiment_graph(ts, sentiment, asset):

    ctxMessage = "Create graph: " + str(ctx.triggered)
    #print(ctxMessage)

    if not asset or not sentiment:
        scatter = px.scatter().add_annotation(text="No Sentiment Data.", showarrow=False, font={"size":20})
        return scatter
    
    sentiment = dict(sentiment)
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

    scatter = px.scatter(df, x = "Date", y = "Compound Score", title = title, hover_name = dates, hover_data = hoverData , trendline="lowess", trendline_options=dict(frac=0.3))
    return scatter
