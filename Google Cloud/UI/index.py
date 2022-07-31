import os

from app import app
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from Apps import homepage
from Apps import portfoliopage
import dash_bootstrap_components as dbc



navbar = html.Nav([
    html.Ul([
        html.Li([
            dcc.Link('Home Page', href='/')
        ], 
        className='nav-item'),
        html.Li([
            dcc.Link('Portfolio Page', href='portfolio')
        ], 
        className='nav-item'),
        html.Li([
            dcc.Link('Debug Page', href='debug')
        ], 
        className='nav-item'),
    ])],
    id='nav-bar')

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Homepage", class_name="nav-item", href="/")),
        dbc.NavItem(dbc.NavLink("Portfolio", class_name="nav-item", href="portfolio")),
    ],
    color="#fc4961",
    dark=True,
)

app.layout = html.Div(id='body', children=[
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/portfolio':
        return portfoliopage.layout
    else:
        return homepage.layout

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8050')
    app.run_server(debug=False, port=server_port, host='0.0.0.0')
