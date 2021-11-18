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
        html.H1("Crypto Fees: A Brief History",
                style={'text-align': 'center'}),
    ], className='card-title'
)

# first_card = dbc.Card(
#     dcc.Graph(figure=fig,
#               # id="splom"
#               )
# )

# cards = dbc.Row(
#     [
#         dbc.Row(
#             [dbc.Col(first_card)],
#             style={'margin-top': 25, 'margin-bottom': 10,
#                    # 'margin-right': '25px', 'margin-left': '25px',
#                    }
#         ),
#     ]
# )

attribution = dbc.Row(
    [dbc.Row([
        dbc.CardLink("Created by: @tc_madt", href="https://www.twitter.com/tc_madt")],
    ),
        dbc.Row([dbc.CardLink("Data Source: Crypto Fees", href="https://www.cryptofees.info")]),
    ]
)

app.layout = html.Div([title,
#                        cards,
                       attribution
                      ]
                      ,
                      style={'margin-top': 10, 'margin-bottom': 10,
                             'margin-right': '25px', 'margin-left': '25px',
                             }
                      )

if __name__ == '__main__':
    app.run_server(debug=True)
