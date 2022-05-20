#from app import app
from dash import dcc
from dash import html
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

timeframe_options = lib.get_timeframe_options()
indicator_options = lib.get_indicator_options()
source_options = lib.get_source_options()
sentimentData = lib.getSentimentData()

layout = [
    dcc.Dropdown(
        #   Source may be yahoo_finance or alpha_vantage. 
        #   TODO, find out pros and cons of each, I believe the stock symbols differ greatly
        id='select-source',
        options=source_options,
        value='yahoo_finance',
        clearable=False
    ),
    dcc.Dropdown(
        #   Timeframe may be month, week, or day. Can be used for long-term or short-term price changes
        id='select-timeframe',
        options=timeframe_options,
        value='day',
        clearable=False
    ),
    dcc.Dropdown(
        #   Assets are stock symbols. Luckily, these all seem to come with company names as well
        #   Stock names & Symbols stored in static folder
        #   May be used for more rigerous data collection, if necessary
        id='select-asset',
        clearable=False
    ),
    dcc.Dropdown(
        #   Indicators are technical stock thingamijigs
        #   TODO, Find out pretty much anything about stock indicators
        id='select-indicators',
        options=indicator_options,
        value=[],
        multi=True,
        clearable=True,
    ),
    dcc.Graph(
        #   Chart displays all of the stock information
        #   TODO, Possibly superimpose stock sentiment data on top of stock price data when applicable
        id='chart'
    ),
    dbc.Card([
        #   Contains information about different indicators (since multiple may be selected at a given time)
        dbc.CardHeader(
            dcc.Tabs(id='indicator-form-tabs')
        ),
        dbc.CardBody(
            dbc.Form(id='indicator-form')
        )
    ]),
    dbc.Card([
        #   Contains information about different indicators (since multiple may be selected at a given time)
        dbc.CardHeader(
            dcc.Tabs(id='sentiment-source-tab', value='Reddit', children=[
                dcc.Tab(label='Reddit', value='Reddit'),
                dcc.Tab(label='Twitter', value='Twitter')
            ])
        )
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id='numPost-chart')
        ], className="six columns"),

        html.Div([
            dcc.Graph(id='totalSentiment-chart')
        ], className="six columns"),
    ], className="row"),
    #   TODO Study Store information, find out what candles are, learn about forms and runs, session storage, etc.
    dcc.Store(id='session-candles', storage_type='session'),
    dcc.Store(id='session-volume', storage_type='session'),
    dcc.Store(id='session-indicators-runs', storage_type='session'),
    dcc.Store(id='session-indicators-forms', storage_type='session'),
    dcc.Store(id='session-indicators', storage_type='session'),
    dcc.Store(id='session-user-indicator', storage_type='session'),
    dcc.Store(id='session-chart', storage_type='session'),
    dcc.Store(id='session-sentiment', storage_type='session'),
    dcc.Store(id='session-numPost-chart', storage_type='session'),
    dcc.Store(id='session-totalSentiment-chart', storage_type='session')
    #   REMOVED SENTIMENT LAYOUT. This was removed due to the change in nature of the data collection algorithm
    #html.Div(
        #id="sentiment-card",
        #children=[
            #html.Div(
                #children=[
                    #dcc.Loading(dcc.Store(id="sentiment")),
                    #html.Button(id="refresh-sentiment"),
                    #html.Div(
                    #    id="sentiment-scores",
                    #    children=[
                    #        html.Div(
                    #            [
                    #                html.Label("Twitter"),
                    #                html.Ul(id="sentiment-scores-twitter"),
                    #            ]
                    #        ),
                    #        html.Div(
                    #            [
                    #                html.Label("Reddit"),
                    #                html.Ul(id="sentiment-scores-reddit"),
                    #            ]
                    #        ),
                    #    ],
                    #),
                    #html.Label("Compound"),
                    #Gauge(min=-1, max=1, value=0.1, color="green"),
                #],
            #)
        #],
    #)
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

    return True, volume, candles

@app.callback(
    Output('session-sentiment', 'data'),
    [Input('select-asset', 'value'),
     Input('sentiment-source-tab', 'value')]
)
def get_sentiment(asset, sentimentSource):
    if not asset or not sentimentSource:
        raise PreventUpdate
    sentiment = lib.getSentimentDf(asset, sentimentSource)
    return sentiment

#   get_indicator_stages(indicators):
#   Takes in the selections from the indicator dropdowns to get the indicators-runs and indicators-forms data
#   TODO: What are the indicator-runs and indicator-forms, also check library.py file stage_indicators 
@app.callback(
    [Output('session-indicators-runs', 'data'),
     Output('session-indicators-forms', 'data')],
    Input('select-indicators', 'value')
)
def get_indicator_stages(indicators):
    if not indicators:
        return {}, {}
    return lib.stage_indicators(indicators=indicators)

#   run_indicators(its, cts, uts, info, candles, volume, user_args):
#   Takes in all of the indicator data and uses it to populate the session-indicators data
#   TODO: Learn what all of this means
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
        return lib.run_indicators(info, candles, volume, user_args=user_args)

#   create_indicator_tabs(ts, forms):
#   Uses the session-indicators-forms data to create tabs for the different indicators
#   TODO: Again, learn what the session-indicators-forms are
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

        tab = dcc.Tab(label=form['name'], value=indicator)
        children.append(tab)

    return children, value

#   create_indicator_forms(indicator, info):
#   Uses the indicator-form-tabs and the session-indicators-forms to create the indicator-form
#   TODO: ??? Probably rename everything because these names are stupid and uninformative
@app.callback(
    Output('indicator-form', 'children'),
    Input('indicator-form-tabs', 'value'),
    State('session-indicators-forms', 'data')
)
def create_indicator_forms(indicator, info):
    if not indicator or not info:
        return []

    i = info[indicator]

    form_children = []

    for option, default in zip(i['options'], i['defaults']):
        form_children.extend([
            dbc.Label(option),
            html.Br(),
            dbc.Input(type='number', placeholder=default),
            html.Br()
        ])
    submit_button = dbc.Button('Submit', type='submit')
    form_children.append(submit_button)
    return form_children

#   parse_inputs(ts, children, indicator):
#   When the button is pressed, take in the information from the indicator-form and update the session-user-indicator data
#   TODO: This would make more sense with better names
@app.callback(
    Output('session-user-indicator', 'data'),
    Input('indicator-form', 'n_submit_timestamp'),
    State('indicator-form', 'children'),
    State('indicator-form-tabs', 'value')
)
def parse_inputs(ts, children, indicator):
    if not children or not indicator:
        raise PreventUpdate
    fields = [i['props'] for i in children if i['type'] == 'Input']
    args = [i['value'] if i.get('value', False)
            else i['placeholder'] for i in fields]
    return {indicator: args}

#   create_graph:
#   Takes in the data and uses js to create the graph client-side
app.clientside_callback(
    ClientsideFunction('clientside', 'create_graph'),
    Output('session-chart', 'data'),
    [Input('session-candles', 'modified_timestamp'),                #   on load
     Input('session-indicators', 'modified_timestamp')],            #   on load
    [State('session-candles', 'data'),
     State('session-indicators', 'data')]
)

#   display_graph:
#   Takes in the data and uses js to disply the graph client-side
app.clientside_callback(
    ClientsideFunction('clientside', 'display_graph'),
    Output('chart', 'figure'),
    Input('session-chart', 'modified_timestamp'),                   #   on load
    State('session-chart', 'data')
)

#   create_sentiment_graph:
#   Takes in the data and uses js to create the graph client-side
app.clientside_callback(
    ClientsideFunction('clientside', 'create_numpost_graph'),
    Output('session-numPost-chart', 'data'),
    Input('session-sentiment', 'modified_timestamp'),                #   on load
    State('session-sentiment', 'data')
)

app.clientside_callback(
    ClientsideFunction('clientside', 'display_numpost_graph'),
    Output('numPost-chart', 'figure'),
    [Input('select-asset', 'value'),
    Input('session-numPost-chart', 'data')]
)

app.clientside_callback(
    ClientsideFunction('clientside', 'create_totalsentiment_graph'),
    Output('session-totalSentiment-chart', 'data'),
    Input('session-sentiment', 'modified_timestamp'),                #   on load
    State('session-sentiment', 'data')
)

app.clientside_callback(
    ClientsideFunction('clientside', 'display_totalsentiment_graph'),
    Output('totalSentiment-chart', 'figure'),
    [Input('select-asset', 'value'),
    Input('session-totalSentiment-chart', 'data')]
)

#def get_sentiment_data():
#    sentiment = {}
#    for timeframe in ["daily", "weekly", "hourly"]:
#        sentiment[timeframe] = {}
#        for social in ["twitter", "reddit"]:
#            t = {"type": timeframe}
#            payload = json.dumps(t)
#            url = f"http://45.33.127.174//get_sentiment_data_{social}"                                  #   Call to Haki's API???
#            headers = {"Content-Type": "text/plain"}
#            try:
#                response = requests.request(
#                    "GET", url, headers=headers, data=payload)
#                raw = json.loads(response.text)
#                sentiment[timeframe][social] = json.loads(
#                    raw["sentiment_scores"])
#            except Exception as e:
#                app.logger.error(
#                    f"Failed to collect sentiment {e}: {social} {timeframe}"
#                )
#                continue
#    return sentiment


#def get_sentiment_data_ticker(asset, timeframe):
#    payload = json.dumps({"ticker": asset, "type": timeframe})
#    url = f"http://45.33.127.174//get_sentiment_data_ticker"                            #   Call to Haki's API???
#    headers = {"Content-Type": "text/plain"}
#    try:
#        response = requests.request("GET", url, headers=headers, data=payload)
#        return json.loads(response.text)
#    except Exception as e:
#        app.logger.error(f"Failed to collect sentiment {e}: {asset}")
#        return {}


#class Sentiment:
#    #def __init__(self):
#        #self._sentiment = get_sentiment_data
#        #self._fetch = get_sentiment_data_ticker
#        #self.data = {}
#        #self.build()
#
#    def _to_frame(self, t, s):
#        df = pd.DataFrame.from_records(self.data[t][s]).transpose()
#        self.data[t][s] = df
#
#    def _sentiment_item(self, p, color):
#        return html.Div(
#            className="sentiment-item",
#            children=[
#                html.Label(className="graduated-label", children=f"{p}%"),
#                GraduatedBar(
#                    value=p,
#                    max=100,
#                    min=0,
#                    color={"ranges": {color: [0, p]}},
#                ),
#            ],
#        )
#
#    def _sentiment_row(self, scores):
#        return html.Li(
#            html.Div(
#                className="sentiment-row",
#                children=[
#                    html.Label(className="sentiment-ticker",
#                               children=scores.Index),
#                    self._sentiment_item(scores.pos, "green"),
#                    self._sentiment_item(scores.neg, "red"),
#                    self._sentiment_item(scores.neu, "blue"),
#                ],
#            )
#        )
#
#    def leaderboard(self, t, s):
#        d = self.data[t][s]
#        d = d.applymap(lambda x: math.floor(float(x) * 100))
#        header = [
#            html.Li(
#                [
#                    html.Label(),
#                    html.Label("Bullish"),
#                    html.Label("Bearish"),
#                    html.Label("Neutral"),
#                ],
#                className="sentiment-row",
#            )
#        ]
#        return header + [self._sentiment_row(score) for score in d.itertuples()]

#    def build(self):
#        self.data = self._sentiment()
#        for t in ["hourly", "daily", "weekly"]:
#            for s in ["reddit", "twitter"]:
#                self._to_frame(t, s)
#
#    def fetch(self, asset, timeframe):
#        return self._fetch(asset=asset, timeframe=timeframe)
#
#    @property
#    def reddit(self):
#        return {t: d["reddit"] for t, d in self.data.items()}
#
#    @property
#    def twitter(self):
#        return {t: d["twitter"] for t, d in self.data.items()}

#@app.callback(
#    ServersideOutput("sentiment", "data"), Trigger("page-content", "id"), memoize=True
#)
#def initialize_sentiment():
#    sentiment = Sentiment()
#    sentiment.build()
#    return sentiment


#@app.callback(
#    Input("refresh-sentiment", "n_clicks"),
#    State("sentiment", "data"),
#)
#def refresh(clicks, sentiment):
#    if not sentiment:
#        raise PreventUpdate
#    sentiment.build()


#@app.callback(
#    [
#        Output("sentiment-scores-twitter", "children"),
#        Output("sentiment-scores-reddit", "children"),
#    ],
#    Input("sentiment", "data"),
#)
#def sentiment_leaderboards(sentiment):
#    if not sentiment:
#        raise PreventUpdate
#    return sentiment.leaderboard("weekly", "twitter"), sentiment.leaderboard(
#        "hourly", "reddit"
#    )

if __name__ == '__main__':
    app.layout = html.Div(layout)
    app.run_server(debug=True, use_reloader=False)
