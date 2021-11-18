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

def cryptofees():
    fees_requests = requests.get("https://cryptofees.info/api/v1/fees")
    json_data = fees_requests.json()

    _df = pd.json_normalize(json_data['protocols'],
                            record_path=['fees'],
                            meta=['name', 'tokenTicker', 'id', 'category', 'blockchain'],
                            errors='ignore')

    _df.loc[_df['blockchain'].isna(), 'blockchain'] = _df.name

    return _df


category_dict = {
    'l1': 'Layer 1',
    'l2': 'Layer 2',
    'dex': 'Decentralized Exchange',
    'lending': 'Lending',
    'xchain': 'Cross Chain',
    'other': 'Other'
}

df = cryptofees()

df.category.replace(category_dict, inplace=True)

today = max(df.date)

time_interval_filter = html.Div([
    html.Div([html.P('Time interval:')],
             style={'display': 'inline-block', 'margin-left': '5px', 'margin-right': '15px'}),

    html.Div([dcc.DatePickerRange(
        id='date-picker-range',
        start_date=(pd.to_datetime(today) - pd.Timedelta(1, unit='d')).strftime('%Y-%m-%d'),
        end_date=today,
        display_format='YYYY-M-DD')],
        style={'display': 'inline-block'})
])

bundle_filter = html.Div([
    html.Div([html.P('Bundle:')],
             style={'display': 'inline-block', 'margin-left': '5px', 'margin-right': '15px'}),
    html.Div([dbc.RadioItems(
        id='multichain-radioitems',
        options=[{'label': 'Multi-chain', 'value': 'M'},
                 {'label': 'Single-chain', 'value': 'S'}],
        value='M'
    )])
])

category_filter = html.Div([
    html.Div([html.P('Category:')],
             style={'margin-left': '5px', 'margin-right': '15px'}),
    html.Div([dcc.Dropdown(
        id='category-dropdown',
        options=[
            {'label': i, 'value': i} for i in df.category.unique().tolist()
        ],
        value=df.category.unique().tolist(),
        multi=True
    )])
])

blockchain_filter = html.Div([
    html.Div([html.P('Blockchain:')],
             style={'margin-left': '5px', 'margin-right': '15px'}),
    html.Div([dcc.Dropdown(
        id='blockchain-dropdown',
        options=[
            {'label': i, 'value': i} for i in df.blockchain.unique().tolist()
        ],
        value=df.blockchain.unique().tolist(),
        multi=True
    )])
])

collapse_content = dbc.Card([dbc.Row([            
    dbc.Col(time_interval_filter),
                                      dbc.Col(bundle_filter),
                                      dbc.Col(category_filter),
                                      dbc.Col(blockchain_filter)
]
                                     )], color="light")

navbar = html.Div(
    [
        dbc.Button(
            "Filters",
            id="collapse-button",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            collapse_content,
            id="collapse",
            is_open=False,
        ),
    ],
)


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

fee_bar = dcc.Graph(id='fee-bar')

fee_pie = dcc.Graph(id='fee-pie')

fee_bchain = dcc.Graph(id='fee-bchain')

first_card = dbc.Card(
    fee_bar
)

second_card = dbc.Card(
    fee_pie
)

third_card = dbc.Card(fee_bchain)

cards = dbc.Row(
    [
        dbc.Row(
            [dbc.Col(third_card)],
            style={'margin-top': 25, 'margin-bottom': 10,
                   # 'margin-right': '25px', 'margin-left': '25px',
                   }
        ),

        dbc.Row(
            [
                dbc.Col(first_card, width=6),
                dbc.Col(second_card, width=6),
            ],
        ),
    ]
)


# Connect the Plotly graphs with Dash Components
@app.callback(
    Output('fee-bar', 'figure'),
    Output('fee-pie', 'figure'),
    Output('fee-bchain', 'figure'),
    Input('multichain-radioitems', 'value'),
    Input('category-dropdown', 'value'),
    Input('blockchain-dropdown', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'))
def update_graph(mchain, cat, bchain, start_date, end_date):
    filtered_df = df.copy()

    # # filter non-float values from 'fee' column
    # filtered_df = filtered_df[pd.to_numeric(filtered_df.fee, errors='coerce').notnull()]

    filtered_df = filtered_df[filtered_df.category.isin(cat)]

    filtered_df = filtered_df[filtered_df.blockchain.isin(bchain)]

    filtered_df = filtered_df[filtered_df['date'].between(start_date, end_date, inclusive=True)]

    filtered_df = filtered_df.groupby(['id', 'name', 'blockchain']).sum()['fee'].reset_index()

    filtered_df['id_other'] = filtered_df.id.where(
        filtered_df.id.isin(filtered_df.nlargest(10, 'fee').id), 'Other')

    filtered_df['name_other'] = filtered_df.name.where(
        filtered_df.name.isin(filtered_df.nlargest(10, 'fee').name), 'Other')

    # print(filtered_df.columns)

    if mchain == 'M':
        filtered_df['id'] = filtered_df['name'].copy()
        filtered_df['id_other'] = filtered_df['name_other'].copy()

    bar1_data = filtered_df.groupby('id').sum().reset_index().nlargest(10, 'fee').sort_values(by='fee', ascending=False)
    bar1 = px.bar(
        bar1_data,
        y='id',
        x='fee',
        text='fee',
        color='id',
        labels={
            "id": "",
            "fee": "Fee ($)"},
        orientation='h',
        title='Top 10 fee generators',
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    bar2_data = filtered_df.groupby('blockchain').sum().reset_index().nlargest(10, 'fee').sort_values(by='fee',
                                                                                                      ascending=False)
    bar2 = px.bar(
        bar2_data,
        x='blockchain',
        y='fee',
        text='fee',
        color='blockchain',
        labels={
            "blockchain": "",
            "fee": "Fee ($)"},
        title='Top 10 blockchains',
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    pie1_data = filtered_df.groupby('id_other').sum().reset_index()
    pie1 = px.pie(pie1_data,
                  values='fee',
                  color='id_other',
                  names='id_other',
                  title='Fee distribution',
                  color_discrete_sequence=px.colors.qualitative.Set3,
                  # template='ggplot2'
                  )

    pie1.update_traces(textposition='inside', textinfo='percent+label')
    pie1.update_layout(
        # paper_bgcolor=theme_dict['white-gray']
        # ,showlegend=False
    )

    bar1.update_traces(texttemplate='%{text:.2s}', textposition='auto')
    bar1.update_layout(
        # paper_bgcolor=theme_dict['white-gray'],
        showlegend=False,
        legend_title_text='')
    bar1.update_yaxes(title='', showticklabels=True, visible=True)

    bar2.update_traces(texttemplate='%{text:.2s}', textposition='auto')
    bar2.update_layout(
        # paper_bgcolor=theme_dict['white-gray'],
        showlegend=False,
        legend_title_text='')
    bar2.update_xaxes(title='', showticklabels=True, visible=True)
    # add annotation
    bar2.add_annotation(dict(font=dict(
        color='grey',
        # size=75
    ),
        x=0.5,
        y=0.5,
        showarrow=False,
        text="crypto-charts.info",
        textangle=0,
        xanchor='center',
        xref="paper",
        yref="paper"))

    bar2.update_annotations(opacity=0.2)

    bar1.add_annotation(dict(font=dict(
        color='grey',
        # size=75
    ),
        x=0.5,
        y=0.5,
        showarrow=False,
        text="crypto-charts.info",
        textangle=0,
        xanchor='center',
        xref="paper",
        yref="paper"))

    bar1.update_annotations(opacity=0.2)

    pie1.add_annotation(dict(font=dict(
        color='grey',
        # size=75
    ),
        x=0.5,
        y=0.5,
        showarrow=False,
        text="crypto-charts.info",
        textangle=0,
        xanchor='center',
        xref="paper",
        yref="paper"
    ))

    pie1.update_annotations(opacity=0.2)

    return bar1, pie1, bar2

attribution = dbc.Row(
    [
        dbc.Row([dbc.CardLink("Created by: @tc_madt", href="https://www.twitter.com/tc_madt")]),
        dbc.Row([dbc.CardLink("Data Source: Crypto Fees", href="https://cryptofees.info")]),
    ]
)

app.layout = html.Div([title,
                       navbar,
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
