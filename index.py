from app import app
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from apps import homepage, userpage, newuserpage
# from app import server # for deployment

navbar = html.Nav([
    html.Ul([
        html.Li([
            dcc.Link('Home Page', href='/')
        ], 
        className='nav-item'),
        html.Li([
            dcc.Link('User Page', href='user')
        ], 
        className='nav-item'),
        html.Li([
            dcc.Link('New User', href='newUser')
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
    if pathname == '/user':
        return userpage.layout
    elif pathname == '/newUser':
        return newuserpage.layout
    else:
        return homepage.layout

if __name__ == '__main__':
    app.run_server(debug=True)