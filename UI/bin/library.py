#%%
from plotly import graph_objects as go
import pandas as pd
import numpy as np
import tulipy

import pathlib
import json

import bin.librarian as ask

PATH = pathlib.Path(__file__).parent
STATIC_PATH = PATH.joinpath("../static").resolve()
DB_PATH = PATH.joinpath("../db").resolve()
INDICATOR_INFO_PATH = STATIC_PATH.joinpath("tulipy_financial_indicators.json").resolve()
CHART_FIELDS = ['date', 'open', 'high', 'low', 'close']

def get_all_indicators():
    data = None
    try:
        info = None
        with open(INDICATOR_INFO_PATH, 'r') as doc:
            info = doc.read()
        data = json.loads(info)
    except Exception as e:
        print(e)
        return []
    else:
        return data

def get_indicator_info(indicator):
    info = get_all_indicators()
    return info[indicator]

def get_indicators_info(*, indicators):
    info = get_all_indicators()
    return {indicator: info[indicator] for indicator in indicators}
        
def get_indicator_options():
    indicators = get_all_indicators()
    return [{'label': info['full_name'], 'value': i} for i, info in indicators.items()]

def get_indicator_func(*, indicator):
    return getattr(tulipy, indicator)

def stage_indicators(indicators):
    info = get_indicators_info(indicators=indicators)
    form_info = {}
    run_info = {}
    for indicator in indicators:
        defaults = info[indicator].get('defaults', [])
        run_info.update({
            indicator: {
                'name': info[indicator]['full_name'],
                'type': info[indicator]['type'],
                'inputs': info[indicator]['inputs'],
                'outputs': info[indicator]['outputs'],
                'defaults': defaults
            }})
        form_info.update({
            indicator: {
                'name': info[indicator]['full_name'],
                'options': info[indicator]['options'],
                'defaults': defaults
            }})
    
    return run_info, form_info

def run_indicators(info, candles, volume, user_args=None):
    overlays, figures = [], []
    
    for indicator, meta in info.items():
        
        func = get_indicator_func(indicator=indicator)

        args = []
        for arg in meta['inputs']:
            if arg == 'real':
                args.append(
                    np.array(candles['close'], dtype=float)
                )
            elif arg in ['open', 'high', 'low', 'close']:
                args.append(
                    np.array(candles[arg], dtype=float)
                )
            elif arg == 'volume' and volume:
                args.append(
                    np.array(volume, dtype=float)
                )

        if user_args and (indicator in user_args.keys()):
            args.extend([float(d) for d in user_args[indicator]])
        elif meta['defaults']:
            args.extend([float(d) for d in meta['defaults']])

        data = func(*args)

        traces = format_trace_data(data, meta['outputs'], candles['x'])
        
        if meta['type'] == 'overlay':
            overlays.extend(traces)
        else:
            figures.extend(traces)

    return {'overlays': overlays, 'figures': figures}


def format_trace_data(data, outputs, xaxis):

    traces = []

    if isinstance(data, tuple):
        for output, trace in zip(outputs, data):
            traces.append(go.Scatter(
                x=xaxis,
                y=trace,
                mode='lines',
                line=go.scatter.Line(color='darkblue'),
                name=output
            ))
    else: 
        traces.append(go.Scatter(
            x=xaxis,
            y=data,
            mode='lines',
            line=go.scatter.Line(color='darkblue'),
            name=outputs[0]
        ))

    return traces

def get_source_asset_types(*, source):
    api = ask.Librarian(path=STATIC_PATH, api_name=source)
    return api.get_api_asset_types()

def get_asset_options(*, source):
    types = get_source_asset_types(source=source)

    options = []
    for type_ in types:
        assets_df = None
        if type_ == 'tr':
            assets_df = get_tr_list_df()
        elif type_ == 'fx':
            assets_df = get_fx_list_df()
        elif type_ == 'cc':
            assets_df = get_cc_list_df()
        atype = f'-{type_}'
        options.extend([{'label': f'{a.name} ({a.symbol})', 'value': a.symbol+atype} for a in assets_df.itertuples()])

    default = ''
    if source == 'alpha_vantage':
        default = 'BTC-cc'
    elif source == 'yahoo_finance':
        default = 'AAPL-tr'

    return options, default

def get_tr_list_df():
    file = 'nasdaq_stock_list.csv'
    path = STATIC_PATH.joinpath(file).resolve()
    df = pd.read_csv(path)
    df.rename(columns={
        'Symbol': 'symbol',
        'Company Name': 'name',
    }, inplace=True
    )
    return df


def get_fx_list_df():
    file = 'physical_currency_list.csv'
    path = STATIC_PATH.joinpath(file).resolve()
    df = pd.read_csv(path)
    df.rename(columns={
        'currency code': 'symbol',
        'currency name': 'name',
    }, inplace=True
    )
    return df

def get_cc_list_df():
    file = 'digital_currency_list.csv'
    path = STATIC_PATH.joinpath(file).resolve()
    df = pd.read_csv(path)
    df.rename(columns={
        'currency code': 'symbol',
        'currency name': 'name',
    }, inplace=True
    )
    return df

def get_tf_list():
    ls = ['month', 'week', 'day']
    return ls

def get_timeframe_options():
    return [{'label': tf.title(), 'value': tf.lower()} for tf in get_tf_list()]

def get_source_list():
    ls = ['alpha_vantage', 'yahoo_finance']
    return ls

def get_source_options():
    return [{'label': s.replace('_', ' '), 'value': s} for s in get_source_list()]

users = {
    "users": []
}

portfolios = []

with open('users.json') as f:
    users = json.load(f)
    user = users["users"][0]

def save_portfolios():
    global users
    global user
    global portfolios
    portfolios = user["portfolios"]
    for index, account in enumerate(users["users"]):
        if user["username"] == account["username"]:
            userIndex = index
            users["users"][userIndex]["portfolios"] = portfolios
    with open("users.json", "w") as outfile: 
        json.dump(users, outfile)

def sign_in(username, password):
    global user
    global portfolios
    for account in users["users"]:
        if account["username"] == username and account["password"] == password:
            user = account
            portfolios = user["portfolios"]
            break
        else:
            user = users["users"][0]


    

def get_portfolio_options():
    global portfolios
    portfolios = user["portfolios"]
    return [{'label': p["name"], 'value': p["name"]} for p in portfolios]


def get_stock_in_portfolio_options(chosenPortfolio):
    global portfolios
    portfolios = user["portfolios"]
    try:
        return [{'label': p["name"], 'value': p["value"]} for p in portfolios[chosenPortfolio]["stocks"]]  
    except IndexError:
        return []

def get_df(*, api_name, type_, symbol, timeframe):
    df = None
    try:
        file = f'{api_name}/{type_}/{symbol}_{timeframe}.csv'
        path = DB_PATH.joinpath(file).resolve()
        df = pd.read_csv(path, delimiter=',').dropna()
    except (pd.errors.EmptyDataError, FileNotFoundError):
        create_csv(api_name=api_name, type_=type_,
                   symbol=symbol, timeframe=timeframe)
        df = pd.read_csv(path, delimiter=',').dropna()

    if df.shape[0] > 300:
        return df.iloc[-300:]
    else: 
        return df

def get_volume_candles(source, asset, timeframe):
    symbol, type_ = tuple(asset.split('-')) 
    df = get_df(api_name=source, type_=type_, symbol=symbol, timeframe=timeframe)
    volume = df['volume'].to_list() if 'volume' in df.columns.values else []

    unrelated = [col for col in df.columns.values if col not in CHART_FIELDS]
    df.drop(columns=unrelated, inplace=True)
    df.rename(columns={'date': 'x'}, inplace=True)
 
    return volume, df

def create_csv(*, api_name, type_, symbol, timeframe):
    try:
        api = ask.Librarian(path=STATIC_PATH, api_name=api_name)
        data = api.get_all_market_data(
            type_=type_, symbol=symbol, timeframe=timeframe)
        filename = f'{api_name}/{type_}/{symbol}_{timeframe}.csv'
        path = DB_PATH.joinpath(filename).resolve()
        with open(path, 'x') as out:
            out.write(data)
    except FileExistsError:
        with open(path, 'w') as out:
            out.write(data)
    finally:
        del api

COLORS = ['aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure',
          'beige', 'bisque', 'black', 'blanchedalmond', 'blue',
          'blueviolet', 'brown', 'burlywood', 'cadetblue',
          'chartreuse', 'chocolate', 'coral', 'cornflowerblue',
          'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan',
          'darkgoldenrod', 'darkgray', 'darkgrey', 'darkgreen',
          'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange',
          'darkorchid', 'darkred', 'darksalmon', 'darkseagreen',
          'darkslateblue', 'darkslategray', 'darkslategrey',
          'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
          'dimgray', 'dimgrey', 'dodgerblue', 'firebrick',
          'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro',
          'ghostwhite', 'gold', 'goldenrod', 'gray', 'grey', 'green',
          'greenyellow', 'honeydew', 'hotpink', 'indianred', 'indigo',
          'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen',
          'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
          'lightgoldenrodyellow', 'lightgray', 'lightgrey',
          'lightgreen', 'lightpink', 'lightsalmon', 'lightseagreen',
          'lightskyblue', 'lightslategray', 'lightslategrey',
          'lightsteelblue', 'lightyellow', 'lime', 'limegreen',
          'linen', 'magenta', 'maroon', 'mediumaquamarine',
          'mediumblue', 'mediumorchid', 'mediumpurple',
          'mediumseagreen', 'mediumslateblue', 'mediumspringgreen',
          'mediumturquoise', 'mediumvioletred', 'midnightblue',
          'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy',
          'oldlace', 'olive', 'olivedrab', 'orange', 'orangered',
          'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise',
          'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink',
          'plum', 'powderblue', 'purple', 'red', 'rosybrown',
          'royalblue', 'saddlebrown', 'salmon', 'sandybrown',
          'seagreen', 'seashell', 'sienna', 'silver', 'skyblue',
          'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen',
          'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise',
          'violet', 'wheat', 'white', 'whitesmoke', 'yellow',
          'yellowgreen']

def get_color_len():
    return len(COLORS)

def get_color(*, index):
    return COLORS[index]


#%%
# %%
