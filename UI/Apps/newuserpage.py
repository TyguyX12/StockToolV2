from app import app
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import json

import bin.library as lib

from dash.dependencies import Input, Output, State, ClientsideFunction

prevCreateAccountClicks = 0

layout = [

  html.Label("Username:", className= 'create-account'),
  dcc.Input(className= 'create-account', id='username'), 

  html.Br(),
  html.Br(),

  html.Label("Password:", className= 'create-account'),
  dcc.Input(className = 'create-account', id='password'),
  

  html.Br(),
  html.Br(),

  html.Button('Create Account', className = 'create-account', id='create-account', n_clicks=0),

]
@app.callback(
  Output('create-account', 'n_clicks'),
  Input('create-account', 'n_clicks'), # get sign in button clicks (sign_in_clicks)
  [State('username', 'value'), # user name typed in (username-input)
  State('password', 'value')] # password typed in (password-input)
  )
def add_account(create_account_clicks, username_input, password_input):
  global prevCreateAccountClicks
  if (create_account_clicks > prevCreateAccountClicks and create_account_clicks > 0):
    lib.add_account(username_input, password_input)
    prevCreateAccountClicks = create_account_clicks
  return create_account_clicks
