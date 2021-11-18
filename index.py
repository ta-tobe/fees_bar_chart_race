import os

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
# from dash_bootstrap_components._components.Container import Container
import pandas as pd
import plotly.express as px 


import requests




external_stylesheets = [dbc.themes.CERULEAN]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

title = html.Div(
    [
        html.H1("Crypto Charts",
                style={'text-align': 'center'}),
        html.H4("compare blockchains and applications at a glance",
                style={'text-align': 'center', 'color': 'grey'})
    ], className='card-title'
)

app.layout = html.Div([title,
#                        navbar,
#                        cards,
#                        attribution
                      ]
                      ,
                      style={'margin-top': 10, 'margin-bottom': 10,
                             'margin-right': '25px', 'margin-left': '25px',
                             }
                      )

if __name__ == '__main__':
    app.run_server(debug=True)
