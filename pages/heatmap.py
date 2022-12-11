import dash
from dash import Dash, html, dcc, Output, Input, State, MATCH, ALL, callback
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

dash.register_page(__name__, name='MSE Heatmap')

x, y = np.arange(101), np.arange(101)
layout = html.Div([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='test1',
                                options=['MSE', 'ROP'],
                                clearable=True,
                                value=['MSE']
                                )
                ], width=2,
                   style={'margin-left': 90, 'margin-top': 10}
                ),
            ]),

            dbc.Row([
            ], style={'height': 10, }),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='graph1',
                              figure={},
                              style={'width':600, 'height': 600, 'margin-left':90}
                              )
                ], width=6),
                dbc.Col([
                    dcc.Graph(id='graph2',
                              figure={},
                              style={'width':600, 'height': 600, 'margin-left':170}
                              )
                ], width=6)
            ])
])


@callback(
    [Output('graph1', 'figure'),
     Output('graph2', 'figure')],
    Input('test1', 'value'),
    prevent_initial_call= True
)
def update_graph2(mse):
    path = 'C:/Users/pymnb/OneDrive/Desktop/Drilling Project/UI/plotly-dash/Extra/Dataset-Wells/'
    MSE_heatmap = pd.read_csv(path + mse + '_heatmap.csv')

    # Creating the Heat map
    fig1 = px.imshow(MSE_heatmap,
                    labels=dict(x="WOB", y="RPM", color="MSE"),
                    x=x, y=y
                    )
    fig1.update_yaxes(autorange=True)
    #fig1.update_layout(paper_bgcolor="red")
    fig1.update_layout(template="plotly_white")

    # Creating 2-D grid of features
    fig2 = go.Figure(data=go.Contour(
        x=x, y=y, z=MSE_heatmap,
        contours=dict(
            coloring='lines',
            showlabels=True, )
    ))
    fig2.update_layout(template="plotly_white")

    return [fig1, fig2]