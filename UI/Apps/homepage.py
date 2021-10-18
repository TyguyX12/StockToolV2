from app import app
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

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

import requests
import json
import math
import bin.library as lib
import pandas as pd

timeframe_options = lib.get_timeframe_options()
indicator_options = lib.get_indicator_options()
source_options = lib.get_source_options()


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
                app.logger.error(
                    f"Failed to collect sentiment {e}: {social} {timeframe}"
                )
                continue
    return sentiment


def get_sentiment_data_ticker(asset, timeframe):
    payload = json.dumps({"ticker": asset, "type": timeframe})
    url = f"http://45.33.127.174//get_sentiment_data_ticker"
    headers = {"Content-Type": "text/plain"}
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        return json.loads(response.text)
    except Exception as e:
        app.logger.error(f"Failed to collect sentiment {e}: {asset}")
        return {}


class Sentiment:
    def __init__(self):
        self._sentiment = get_sentiment_data
        self._fetch = get_sentiment_data_ticker
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


layout = [
    dcc.Dropdown(
        id='select-source',
        options=source_options,
        value='yahoo_finance',
        clearable=False
    ),
    dcc.Dropdown(
        id='select-timeframe',
        options=timeframe_options,
        value='week',
        clearable=False
    ),
    dcc.Dropdown(
        id='select-asset',
        clearable=False
    ),
    dcc.Dropdown(
        id='select-indicators',
        options=indicator_options,
        value=['ema'],
        multi=True,
        clearable=True,
    ),
    dcc.Graph(
        id='chart'
    ),
    dbc.Card([
        dbc.CardHeader(
            dcc.Tabs(id='indicator-form-tabs')
        ),
        dbc.CardBody(
            dbc.Form(id='indicator-form')
        )
    ]),
    dcc.Store(id='session-candles', storage_type='session'),
    dcc.Store(id='session-volume', storage_type='session'),
    dcc.Store(id='session-indicators-runs', storage_type='session'),
    dcc.Store(id='session-indicators-forms', storage_type='session'),
    dcc.Store(id='session-indicators', storage_type='session'),
    dcc.Store(id='session-user-indicator', storage_type='session'),
    dcc.Store(id='session-chart', storage_type='session'),
    html.Div(
        id="sentiment-card",
        children=[
            html.Div(
                children=[
                    dcc.Loading(dcc.Store(id="sentiment")),
                    html.Button(id="refresh-sentiment"),
                    html.Div(
                        id="sentiment-scores",
                        children=[
                            html.Div(
                                [
                                    html.Label("Twitter"),
                                    html.Ul(id="sentiment-scores-twitter"),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Label("Reddit"),
                                    html.Ul(id="sentiment-scores-reddit"),
                                ]
                            ),
                        ],
                    ),
                    html.Label("Compound"),
                    Gauge(min=-1, max=1, value=0.1, color="green"),
                ],
            )
        ],
    )
]


@app.callback(
    [Output('select-asset', 'options'),
     Output('select-asset', 'value')],
    Input('select-source', 'value')
)
def get_source_assets(source):
    if not source:
        raise PreventUpdate
    return lib.get_asset_options(source=source)


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


@app.callback(
    [Output('session-indicators-runs', 'data'),
     Output('session-indicators-forms', 'data')],
    Input('select-indicators', 'value')
)
def get_indicator_stages(indicators):
    if not indicators:
        return {}, {}
    return lib.stage_indicators(indicators=indicators)


@app.callback(
    Output('session-indicators', 'data'),
    [Input('session-indicators-runs', 'modified_timestamp'),
     Input('session-candles', 'modified_timestamp'),
     Input('session-user-indicator', 'modified_timestamp')],
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


@app.callback(
    [Output('indicator-form-tabs', 'children'),
     Output('indicator-form-tabs', 'value')],
    Input('session-indicators-forms', 'modified_timestamp'),
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


@app.callback(
    ServersideOutput("sentiment", "data"), Trigger("page-content", "id"), memoize=True
)
def initialize_sentiment():
    sentiment = Sentiment()
    sentiment.build()
    return sentiment


@app.callback(
    Input("refresh-sentiment", "n_clicks"),
    State("sentiment", "data"),
)
def refresh(clicks, sentiment):
    if not sentiment:
        raise PreventUpdate
    sentiment.build()


@app.callback(
    [
        Output("sentiment-scores-twitter", "children"),
        Output("sentiment-scores-reddit", "children"),
    ],
    Input("sentiment", "data"),
)
def sentiment_leaderboards(sentiment):
    if not sentiment:
        raise PreventUpdate
    return sentiment.leaderboard("weekly", "twitter"), sentiment.leaderboard(
        "hourly", "reddit"
    )


app.clientside_callback(
    ClientsideFunction('clientside', 'create_graph'),
    Output('session-chart', 'data'),
    [Input('session-candles', 'modified_timestamp'),
     Input('session-indicators', 'modified_timestamp')],
    [State('session-candles', 'data'),
     State('session-indicators', 'data')]
)

app.clientside_callback(
    ClientsideFunction('clientside', 'display_graph'),
    Output('chart', 'figure'),
    Input('session-chart', 'modified_timestamp'),
    State('session-chart', 'data')
)
