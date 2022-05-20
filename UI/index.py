from app import app
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from Apps import homepage
from Apps import debug
# from app import server # for deployment

navbar = html.Nav([
    html.Ul([
        html.Li([
            dcc.Link('Home Page', href='/')
        ], 
        className='nav-item'),
        html.Li([
            dcc.Link('Debug Page', href='debug')
        ], 
        className='nav-item'),
    ])],
    id='nav-bar')

app.layout = html.Div(id='body', children=[
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/debug':
        return debug.layout
    else:
        return homepage.layout

if __name__ == '__main__':
    app.run_server(debug=True)
