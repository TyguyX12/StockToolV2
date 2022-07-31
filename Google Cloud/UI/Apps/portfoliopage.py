import bin.portfolio as pf
import bin.sentiment as sent
import bin.library as lib

from app import app
from dash import dcc, html, ALL
from dash import callback_context as ctx

import dash_bootstrap_components as dbc
from index import app
from datetime import date, timedelta

from dash_extensions.enrich import (
    Input,
    Output,
    State,
)
from dash_daq import Gauge
import json

portfolio_options, initial_portfolio, stock_in_portfolio_options, initial_stock_in_portfolio = pf.initialize()
add_asset_options = lib.get_asset_options(source="yahoo_finance")

layout = [
    html.Br(),
    html.H1('Portfolio Page'),
    html.Div(className="line"),
    html.Br(),

    html.H2('Edit Portfolios'),

    html.Div(id = "stock-tool", className = "vertical-flex-div", children = [
        
        dbc.Button('Edit Portfolios', id='edit-portfolios-button'),

        html.Div(className='horizontal-flex-div', children = [
            dcc.Dropdown(
                className='medium-dropdown',
                id='select-portfolio',
                searchable=False,
                options=portfolio_options,
                value=initial_portfolio,
                clearable=True
            ),
            dbc.Button('Edit Portfolio', id='edit-portfolio-button')
        ]),  

        html.Br(),

        html.H2('Add Stock To Portfolio'),

        dbc.Alert(
            id="add-stock-alert",
            dismissable=True,
            is_open=False,
        ),

        dbc.Table(className= "wide", bordered=True, children = [
            html.Thead(html.Tr(className = "table-header", children = [
                html.Th(html.Div("Stock")),
                html.Th(html.Div("Volume")),
                html.Th(html.Div("Purchase Date")),
                html.Th(html.Div("Add To Portfolio?"))
            ])),
            html.Tbody(
                html.Tr([
                    html.Td(html.Div(
                        dcc.Dropdown(
                            className='large-dropdown',
                            id='select-add-asset',
                            options= add_asset_options[0],
                            value= add_asset_options[1],
                            clearable=False
                        )
                    )),
                    html.Td(html.Div(dbc.Input(class_name="input", value=10, id='stock-volume-input', type = 'number'))),
                    html.Td(html.Div(dcc.DatePickerSingle(className="input", id= "stock-date-input", max_date_allowed=(date.today()-timedelta(days=1)), date=date.today(), display_format='MM/DD/YYYY', reopen_calendar_on_clear = True))),
                    html.Td(html.Div(dbc.Button('Add to Portfolio', type = 'button', id='add-portfolio-asset'))),
                ])
            )
            
        ]),

        html.Br(),
        html.H2('View Portfolio Sentiment'),

        dbc.Card(class_name = 'wide', children=[
            dbc.CardHeader( 
                dcc.Tabs(id='portfolio-sentiment-source-tab', value='twitter', children=[
                    dcc.Tab(className='tab', selected_className='selected-tab', label='Twitter', value='twitter'),
                    dcc.Tab(className='tab', selected_className='selected-tab', label='Reddit', value='reddit')
                ])
            ),
            dbc.CardBody(
                html.Div([
                    dcc.Loading(
                        id="sentiment-table-loading",
                        type="circle",
                        children= dbc.Table(id ="portfolio-sentiment-table", style={"min-height":"10vw", "padding":"1vw"}, bordered=True)
                    )
                ])
            )
        ]),

    ]),
    html.Br(),
    

    dbc.Modal(id="edit-portfolios-modal", is_open=False, children=[     
        dbc.ModalHeader(dbc.ModalTitle("Edit Portfolios")),
        dbc.ModalBody([
            html.Div(className="horizontal-flex-div", children = [
                dbc.Table(id = "portfolios-table", bordered=True),
                
            ])               
        ]),
        dbc.ModalFooter([
            html.Div("Add Portfolio:", style={"font-size": "16px"}),
            html.Div(className = "add-portfolio-div", children = [
                dbc.Input(id='new-portfolio-name', class_name="input"),
                dbc.Button('Add Portfolio', id='add-portfolio')
            ]),
            dbc.Button("Close", id="close-edit-portfolios"),
            dbc.Alert(
                id="add-portfolio-alert",
                dismissable=True,
                is_open=False,
            )
        ])
    ]),

    dbc.Modal(id="edit-portfolio-modal", is_open=False, children = [
        dbc.ModalHeader(dbc.ModalTitle("Edit Portfolio")),
        dbc.ModalBody(id = "edit-portfolio-body"),
        dbc.ModalFooter(dbc.Button("Close", id="close-edit-portfolio"))
    ]),

    dcc.Store(id='session-portfolios'),

]

@app.callback(
    [Output('select-portfolio', 'options'),
    Output('select-portfolio', 'value')],           #   Handles issue when deleting selected portfolio
    Input('session-portfolios', 'modified_timestamp'),
    State('select-portfolio', 'value')
)
def get_portfolio_options(ts, currentPortfolio):   
    portfolioOptions = pf.getPortfolioOptions()
    portfolios = pf.getPortfolioList()
    if currentPortfolio in portfolios:
        return portfolioOptions, currentPortfolio
    if not portfolios:
        return [], None
    return portfolioOptions, portfolios[0]
    

@app.callback(
    [Output("add-portfolio-alert", "is_open"),
     Output("add-portfolio-alert", "children"),
     Output("add-stock-alert", "is_open"),
     Output("add-stock-alert", "children"),
     Output('session-portfolios', 'data')],
    [Input('add-portfolio', 'n_clicks'),
     Input({'type': 'delete-portfolio', 'index': ALL}, 'n_clicks'),
     Input('add-portfolio-asset', 'n_clicks'),
     Input({'type': 'delete-portfolio-asset', 'index': ALL}, 'n_clicks')],
    [State('new-portfolio-name', 'value'),
     State('select-portfolio', 'value'),
     State('select-add-asset', 'options'),
     State('select-add-asset', 'value'),
     State('stock-volume-input', 'value'),
     State('stock-date-input', 'date')]
)
def update_session_portfolios(add_portfolio_clicks, delete_portfolio_clicks, add_stock_clicks, delete_stock_clicks, newPortfolio, portfolio, stockOptions, stock, amount, date):
    ctxMessage = "Update Session Portfolios: " + str(ctx.triggered)
    #print(ctxMessage)
    triggeredId = (ctx.triggered[0]['prop_id'].split('.')[0])   

    try:
        triggeredType = json.loads(triggeredId)["type"]
        index = json.loads(triggeredId)["index"]
    except:
        triggeredType, index = "", ""

    addPortfolioErrorStatus, addPortfolioErrorMessage = False, None
    addStockErrorStatus, addStockErrorMessage = False, None
    
    if triggeredId == "add-portfolio" and add_portfolio_clicks:
        addPortfolioErrorStatus, addPortfolioErrorMessage = add_portfolio(newPortfolio)

    if triggeredType == "delete-portfolio" and sum(filter(None, delete_portfolio_clicks)) != 0:
        delete_portfolio(index)
    if triggeredId == "add-portfolio-asset" and add_stock_clicks:
        addStockErrorStatus, addStockErrorMessage = add_stock_to_portfolio(stock, stockOptions, portfolio, amount, date)
    if triggeredType == "delete-portfolio-asset" and sum(filter(None, delete_stock_clicks)) != 0:
        delete_stock_from_portfolio(index)

    portfolio_data = pf.getPortfolios()
    return addPortfolioErrorStatus, addPortfolioErrorMessage, addStockErrorStatus, addStockErrorMessage, portfolio_data

def add_portfolio(newPortfolio):
    if not newPortfolio or newPortfolio == "":
        return True, ["Please Enter A Valid Portfolio Name"]
    if newPortfolio in pf.getPortfolios():
        label = str(newPortfolio) + " Already in Portfolios"
        return True, [label]
   
    pf.createNewPortfolio(newPortfolio)
    return False, []


def delete_portfolio(portfolio):
    pf.deletePortfolio(portfolio)


def add_stock_to_portfolio(stock, assetOptions, portfolio, amount, date):
    if not portfolio:
        return True, ["Please Select A Portfolio"]
    if stock in pf.getStocksInPortfolio(portfolio)[0]:
        label = str(stock[:-3]) + " Already in " + portfolio
        return True, [label]
    if not amount or amount == 0 or amount == "":
        return True, ["Please Enter A Valid Volume"]
    if not date:
        return True, ["Please Enter A Valid Date"]

    assetIndex = next((i for i, item in enumerate(assetOptions) if item["value"] == stock), None)
    newLabel = assetOptions[assetIndex]["label"] #Label given by label of first stock in options with matching value
    newValue = assetOptions[assetIndex]["value"] #Value given by label of first stock in options with matching value
    
    pf.addStockToPortfolio(amount, date, newValue, newLabel, portfolio)
    return False, []


def delete_stock_from_portfolio(key):
    try:
        portfolio = key.split("|")[0]
        stock = key.split("|")[1]
    except:
        return
    pf.deleteStockFromPortfolio(portfolio, stock)


@app.callback(
    Output('portfolios-table', 'children'),
    Input('session-portfolios', 'modified_timestamp')
)
def create_portfolios_table(ts):
    ctxMessage = "Get portfolios: " + str(ctx.triggered)
    #print(ctxMessage)
    
    portfolios = pf.getPortfolioList()
    header = html.Thead(html.Tr(className = "table-header", children = [
        html.Th(html.Div("Portfolio")),
        html.Th(html.Div("Stocks")),
        html.Th(html.Div("Delete?"))
    ]))

    if not portfolios:
        return html.Div("No Portfolios", style={"font-size": "20px"})

    children = [header]
    body = html.Thead(children=[])

    for portfolio in portfolios:
        stocksInPortfolio = pf.getStocksInPortfolio(portfolio)[1]
        stockDivs = []
        if len(stocksInPortfolio) == 0:
            stockDivs.append(html.Div("None"))
        for stock in stocksInPortfolio:
            stockDivs.append(html.Div(stock))

        row = html.Tr(style = {"font-size": "14px"}, children = [
            html.Td(html.Div(portfolio), style={"font-size": "16px"}), 
            html.Td(html.Div(stockDivs, className = "vertical-flex-div", style = {"row-gap":"0px"})),
            html.Td(html.Div(dbc.Button('Delete Portfolio', key=portfolio, id = {
            'type': 'delete-portfolio',
            'index': portfolio
            })))         
        ])
        body.children.append(row)
    children.append(body)   
    return children

@app.callback(
    Output('edit-portfolio-body', 'children'),
    [Input('session-portfolios', 'modified_timestamp'),
     Input('select-portfolio', 'value')]
)
def create_portfolio_table(ts, portfolio):

    ctxMessage = "Get portfolio: " + str(ctx.triggered)
    #print(ctxMessage)

    if portfolio == None:
        return html.Div("No Portfolio Chosen", style={"font-size": "20px"})

    stocksInPortfolioSymbols = pf.getStocksInPortfolio(portfolio)[0]
    stocksInPortfolioNames = pf.getStocksInPortfolio(portfolio)[1]

    if len(stocksInPortfolioSymbols) == 0:
        label = "No Stocks In " + str(portfolio)
        return html.Div(label, style={"font-size": "20px"})

    label = "Edit Portfolio: " + str(portfolio)
    header = html.Div(label, style={"font-size": "20px"})
    tableHeader = html.Thead(html.Tr(className = "table-header", children = [
        html.Th(html.Div("Stock")),
        html.Th(html.Div("Purchase Date", style={"min-width": "100px"})),
        html.Th(html.Div("Volume")),
        html.Th(html.Div("Delete?"))
    ]))

    tbody = html.Tbody(children = [])

    for symbol, stock in zip(stocksInPortfolioSymbols, stocksInPortfolioNames):
        purchaseDate = pf.getStockPurchaseDate(symbol, portfolio)
        amountVol = pf.getStockAmount(symbol, portfolio)       
        key = portfolio + "|" + symbol
    
        row = html.Tr(style = {"font-size": "14px"}, children = [
            html.Td(html.Div(stock)), 
            html.Td(html.Div(purchaseDate)),
            html.Td(html.Div(amountVol)),
            html.Td(html.Div(dbc.Button('Delete From Portfolio',  key=key, id =
            {
                'type': 'delete-portfolio-asset',
                'index': key
            })))
        ])
        tbody.children.append(row)
    table = dbc.Table(bordered=True, children = [tableHeader, tbody])

    return [header, table]

@app.callback(
    Output('portfolio-sentiment-table', 'children'),
    [Input('session-portfolios', 'modified_timestamp'),
    Input('select-portfolio', 'value'),
    Input('portfolio-sentiment-source-tab', 'value')]
)
def gatherPortfolioSentiment(ts, portfolio, source):
    ctxMessage = "Get portfolio sentiment: " + str(ctx.triggered)
    #print(ctxMessage)
    if not portfolio:
        return html.Div("No Portfolio In Chosen", style={"font-size": "25px", "text-align": "center"})

    header = html.Thead(html.Tr(className = "table-header", children = [
        html.Th(html.Div("Stock")),
        html.Th(html.Div("Volume")),
        html.Th(html.Div("Purchase Date"), style={"min-width": "150px"}),
        html.Th(html.Div("Current Value")),
        html.Th(html.Div("Stock Value Change")),
        html.Th(html.Div("Portfolio Value Change")),
        html.Th(html.Div("Predicted Change")),
        html.Th(html.Div("Sentiment Chart"))
    ]))

    stocksInPortfolio = pf.getStocksInPortfolio(portfolio)[0]
    if len(stocksInPortfolio) == 0:
        label = "No Stocks In " + str(portfolio)
        return html.Div(label, style={"font-size": "25px", "text-align": "center"})

    children = [header]
    body = html.Tbody(children = [])

    for stock in stocksInPortfolio:
        stockLabel, volume, purchaseDate, initialPrice, currentPrice, valueChange, pfValueChange, valueChangeColor = pf.getPortfolioData(stock, portfolio)
        
        try:
            latestDate, latestSentiment = sent.getLatestSentiment(stock, source)
            compoundSentiment = latestSentiment[3]
            prediction, predictionColor = sent.singleStockARIMA(source, stock)
            gaugeLabel = ("Sentiment For " + str(latestDate))

        except:
            gaugeLabel = ("No Sentiment Data Available")
            compoundSentiment = 0
            prediction = "Not Enough Data"
        
        gauge = Gauge(min=-1, max=1, value=compoundSentiment, label = gaugeLabel, color={"gradient":True,"ranges":{"red":[-1,0.35],"yellow":[0.35,0.8],"green":[0.8,1]}}, size = 150)
        
        newRow = html.Tr(className = "sentiment-table-row", children = [
            html.Td(html.Div(stockLabel, style = {"font-weight": "600"})),
            html.Td(html.Div(volume)),
            html.Td(html.Div(purchaseDate)),
            html.Td(html.Div(currentPrice)),
            html.Td(html.Div(valueChange, style = {"color": valueChangeColor})),
            html.Td(html.Div(pfValueChange, style = {"color": valueChangeColor})),
            html.Td(html.Div(prediction, style = {"color": predictionColor})),
            html.Td(gauge)

        ])
        body.children.append(newRow)
    children.append(body)
    return children

@app.callback(
    Output("edit-portfolios-modal", "is_open"),
    [Input("edit-portfolios-button", "n_clicks"), Input("close-edit-portfolios", "n_clicks")],
    [State("edit-portfolios-modal", "is_open")],
)
def toggle_edit_portfolios_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("edit-portfolio-modal", "is_open"),
    [Input("edit-portfolio-button", "n_clicks"), Input("close-edit-portfolio", "n_clicks")],
    [State("edit-portfolio-modal", "is_open")],
)
def toggle_edit_portfolio_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("no-pf-name-alert", "is_open"),
    Input("add-portfolio", "n_clicks"),
    State("new-portfolio-name", "value")
)
def toggle_no_pf_name_alert(n, name):
    if n and (not name or name == ""):
        return True

