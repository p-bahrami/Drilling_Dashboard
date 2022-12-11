import dash
from dash import Dash, html, dcc, Output, Input, State, MATCH, ALL, callback
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json
from plotly.subplots import make_subplots

path = 'C:/Users/pymnb/OneDrive/Desktop/Drilling Project/UI/plotly-dash/Extra/Dataset-Wells/'
no_figures = 6

dash.register_page(__name__, path='/', name='Single Well Analyse')

layout = html.Div([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='dropdown_1',
                                options=['Well1', 'Well2', 'Well3', 'Well4'],
                                clearable=True,
                                value=[]
                                )
                ], width=2,
                   style={'margin-left': 0, 'margin-bottom': 10, 'margin-top': -5, 'color': 'black'}
                ),
                dbc.Col([
                    dcc.RadioItems(id='radioitem1',
                                   options=[{'label': 'Geological Formations', 'value': 'Formation'},
                                             {'label': 'Hole Size', 'value': 'HoleSize'},],
                                   #value=[]
                    )
                ], width=3, style={'margin-left': 80}
                )
            ]),

            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='dropdownF_1', options=[], clearable=True, value=['ROP5'], multi=True)
                ], width=2),
                dbc.Col([
                    dcc.Dropdown(id='dropdownF_2', options=[], clearable=True, value=['SWOB'], multi=True)
                ], width=2),
                dbc.Col([
                    dcc.Dropdown(id='dropdownF_3', options=[], clearable=True, value=['CMSE'], multi=True)
                ], width=2),
                dbc.Col([
                    dcc.Dropdown(id='dropdownF_4', options=[], clearable=True, value=['RPM'], multi=True)
                ], width=2),
                dbc.Col([
                    dcc.Dropdown(id='dropdownF_5', options=[], clearable=True, value=['SPPA'], multi=True)
                ], width=2),
                dbc.Col([
                    dcc.Dropdown(id='dropdownF_6', options=[], clearable=True, value=['TFLO'], multi=True)
                ], width=2),
            ]),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='graph_1',
                              figure={},
                              style={},
                              config={'displayModeBar': True,
                                      'displaylogo': False,
                                      'modeBarButtonsToRemove': ['zoomIn2d', 'zoomOut2d', 'autoScale2d',]
                              }
                    )
                ]),
            ]),

            dbc.Row([
                dbc.Col([
                    dcc.Store(id='table_1')
                ]),
            ])
], style={'margin-right': -250})


# callback to store and share the df between callbacks
@callback(
    Output('table_1', 'data'),
    Input('dropdown_1', 'value'),
    prevent_initial_call=True
)
def store_df(chosen_well):
    if chosen_well is None:
        return dash.no_update
    else:
        df = pd.read_csv(path + chosen_well + '.csv')
        df_json = df.to_json(date_format='iso', orient='split')
    return df_json


# callback for getting the well files from dropdown_1 and returns the feature options for the chained dropdowns
@callback(
    [Output('dropdownF_1', 'options'),
    Output('dropdownF_2', 'options'),
    Output('dropdownF_3', 'options'),
    Output('dropdownF_4', 'options'),
    Output('dropdownF_5', 'options'),
    Output('dropdownF_6', 'options')],
    Input('table_1', 'data'),
    prevent_initial_call=True
)
def callback_stats(js_df):
    if js_df is None:
        return dash.no_update
    else:
        dff = pd.read_json(js_df, orient='split')
        features = np.sort(dff.columns.values[2:])
    return [features]*no_figures


# callback for initial plots of selected parameters
@callback(
    Output('graph_1', 'figure'),
    Input('dropdownF_1', 'value'),
    Input('dropdownF_2', 'value'),
    Input('dropdownF_3', 'value'),
    Input('dropdownF_4', 'value'),
    Input('dropdownF_5', 'value'),
    Input('dropdownF_6', 'value'),
    Input('table_1', 'data'),
    prevent_initial_call=True
)
def subplot_plot(dd1, dd2, dd3, dd4, dd5, dd6, js_df):

    df = pd.read_json(js_df, orient='split')

    fig = make_subplots(rows=1, cols=no_figures,
                        shared_yaxes=True,
                        subplot_titles=('ROP5', 'SWOB', 'CMSE', 'RPM', 'SPPA', 'TFLO')
                       )
    all_dd = [dd1, dd2, dd3, dd4, dd5, dd6]

    for idx, name in enumerate(all_dd):
        for i in range(len(name)):
            fig.add_trace(
                go.Scatter(name=name[i], x=df[name[i]], y=df['TVD']), row=1, col=idx+1)

    fig.update_layout(height=590, width=1495, margin={'l': 0, 'r': 0, 't': 50, 'b': 20}, template="plotly_white", legend=dict(orientation="h")) #showlegend=False)
    fig.update_yaxes(title_text="TVD (m)", row=1, col=1, range=[2000, 500])
    return fig


