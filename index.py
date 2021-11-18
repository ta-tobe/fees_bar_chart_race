import os

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
# from dash_bootstrap_components._components.Container import Container
import pandas as pd
import plotly.express as px
import numpy as np
import requests




external_stylesheets = [dbc.themes.CERULEAN]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server



def cryptofees():
    fees_requests = requests.get("https://cryptofees.info/api/v1/fees")
    json_data = fees_requests.json()

    _df = pd.json_normalize(json_data['protocols'],
                            record_path=['fees'],
                            meta=['name', 'tokenTicker', 'id', 'category', 'blockchain'],
                            errors='ignore')

    _df.loc[_df['blockchain'].isna(), 'blockchain'] = _df.name
    _df.id.replace(id_dict, inplace=True)

    return _df


id_dict = {
    'eth': 'Ethereum',
    'bsc': 'Binance Smart Chain',
    'uniswap-v3': 'Uniswap V3',
    'uniswap-v2': 'Uniswap V2',
    'sushiswap': 'Sushiswap',
    'compound': 'Compound',
    'btc': 'Bitcoin',
    'aave-v2': 'Aave V2',
    'avalanche': 'Avalanche',
    'maker': 'MakerDAO',
    'aave-v2-avalanche-proto': 'Aave V2 - Avalanche',
    'terraswap': 'Terraswap',
    'balancerv2': 'Balance V2', 'pangolin': 'Pangolin', 'quickswap': 'Quickswap', 'ens': 'Ethereum Naming Service',
    'sushiswap-polygon': 'Sushiswap - Polygon',
    'arbitrum-one': 'Arbitrum', 'sushiswap-arbitrum': 'Sushiswap - Arbitrum',
    'osmosis': 'Osmosis', 'synthetix-mainnet': 'Synthetix',
    'polygon': 'Polygon', 'bancor': 'Bancor', 'fantom': 'Fantom', 'uniswap-arbitrum': 'Uniswap - Arbitrum',
    'ada': 'Cardano',
    'balancerv2-polygon': 'Balancer - Polygon',
    'liquity': 'Liquity', 'balancer-v1': 'Balancer V1', 'dfyn': 'Dfyn',
    'hop-arbitrum': 'Hop - Arbitrum', 'tornado': 'Tornado', 'terra': 'Terra',
    'hop-polygon': 'Hop - Polygon', 'ren': 'Ren', 'doge': 'Doge', 'visor': 'Visor',
    'xdai': 'xDAI', 'mstable': 'mStable', 'balancerv2-arbitrum': 'Balancer V2 - Arbitrum',
    'aave-v1': 'Aave V1', 'zilliqa': 'Zilliqa', 'xtz': 'Tezos', 'xrp': 'Ripple', 'bsv': 'Bitcoin Satoshi Vision',
    'ltc': 'Litecoin', 'polymarket': 'Polymarket',
    'sushiswap-fantom': 'Sushiswap - Fantom', 'swapr-arbitrum': 'Swapr - Arbitrum', 'honeyswap': 'HoneySwap',
    'polkadot': 'Polkadot', 'xlm': 'Stellar',
    'uniswap-v1': 'Uniswap V1', 'hop-xdai': 'Hop - xDAI', 'linkswap': 'Linkswap', 'aave-v2-amm': 'Aave V2',
    'xmr': 'Monero', 'bch': 'Bitcoin Cash', 'swapr-xdai': 'Swapr - xDAI',
    'tbtc': 'tBTC', 'swapr-ethereum': 'Swapr - Ethereum', 'kusama': 'Kusama', 'zerox': '0x',
    'aave-v2-polygon-proto': 'Aave V2 - Polygon'
}
column_dict = {
    'id': '',
    'name': '',
    'fee': 'Fees',
}

df_orig = cryptofees()
bar1_data = df_orig.groupby('id').sum().reset_index().nlargest(10, 'fee').sort_values(by='fee', ascending=False)
df = df_orig[df_orig.id.isin(bar1_data.id)]

fig = px.bar(df,
             y="id",
             x="fee",
             color="name",
             # height=1000,
             orientation='h',
             labels=column_dict,
             animation_frame="date",
             range_x=[0, df.fee.max() * 1.1],
             category_orders={"id": np.flip(df[['id', 'fee']].sort_values(by=['fee'], ascending=True)['id'].unique()),
                              "date": df.date.sort_values(ascending=True)}
             )

title = html.Div(
    [
        html.H1("Crypto Fees: A Brief History",
                style={'text-align': 'center'}),
    ], className='card-title'
)

first_card = dbc.Card(
    dcc.Graph(figure=fig,
              # id="splom"
              )
)

cards = dbc.Row(
    [
        dbc.Row(
            [dbc.Col(first_card)],
            style={'margin-top': 25, 'margin-bottom': 10,
                   # 'margin-right': '25px', 'margin-left': '25px',
                   }
        ),
    ]
)

attribution = dbc.Row(
    [dbc.Row([
        dbc.CardLink("Created by: @tc_madt", href="https://www.twitter.com/tc_madt")],
    ),
        dbc.Row([dbc.CardLink("Data Source: Crypto Fees", href="https://cryptofees.info")]),
    ]
)

app.layout = html.Div([title,
                       cards,
                       attribution
                      ]
                      ,
                      style={'margin-top': 10, 'margin-bottom': 10,
                             'margin-right': '25px', 'margin-left': '25px',
                             }
                      )

if __name__ == '__main__':
    app.run_server(debug=True)
