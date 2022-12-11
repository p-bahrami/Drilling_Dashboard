import dash
from dash import Dash, html, dcc, Output, Input, State, MATCH, ALL, callback
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import os
# **********************************************************************************************************************
style_convas = {'height': 600,
                'legend': {'title': '', 'x': 0, 'y': 1.06, 'orientation': 'h'},
                'margin': {'l': 0, 'r': 20, 't': 50, 'b': 0},
                'paper_bgcolor': 'white',
                'plot_bgcolor': 'white',
                }

dash.register_page(__name__, name='Rock Strength')

layout = html.Div([
    html.Div(children=[
        html.Button('add Chart', id='add-chart', n_clicks=0)
    ]),
    html.Div(id='container', children=[])
])

@callback(
    Output('container', 'children'),
    [Input('add-chart', 'n_clicks'),
    Input({'type': 'remove-btn', 'index': ALL}, 'n_clicks')],   # why 'All' here
    [State('container', 'children')],                          # what is? prevent_initial_call=True
    prevent_initial_call=True    # False will raise an error for initial empty list
)
def display_graphs(n_clicks, n, div_children):

    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    elm_in_div = len(div_children)

    if triggered_id == 'add-chart':
        new_child = html.Div(
            id={'type': 'div-num', 'index': elm_in_div},
            style={'width': '33%',
                   'height': '50%',
                   'display': 'inline-block',
                   'outline': 'none',
                   'padding': 5},
            children=[
                dbc.Container([
                    dbc.Row([
                        dbc.Col([dcc.Dropdown(id={'type': 'well-choice', 'index': n_clicks},
                                        options=['Well1', 'Well2', 'Well3', 'Well4', 'Well5'],
                                        clearable=True,
                                        value=[]
                                )], width=3),
                        dbc.Col([dcc.Dropdown(id={'type': 'feature-choice', 'index': n_clicks},
                                              options=[],
                                              multi=True,
                                              clearable=True,
                                              value=[]
                                )], width=9),
                    ]),
                    dbc.Row([
                        dbc.Col([dcc.Graph(id={'type': 'dynamic-graph', 'index': n_clicks},
                                           figure={}
                                )]),
                    ]),
                    dbc.Row([
                        dbc.Col([html.Button("Remove", id={'type': 'remove-btn', 'index': elm_in_div})
                        ])
                    ]),
                ])
            ]
        )
        div_children.append(new_child)
        return div_children

    if triggered_id != 'add-chart':
        for idx, val in enumerate(n):
            if val is not None:
                del div_children[idx]
                return div_children


@callback(
    Output({'type': 'feature-choice', 'index': MATCH}, 'options'),
    [Input({'type': 'well-choice', 'index': MATCH}, 'value')],
    prevent_initial_call=True
)
def set_well_options(chosen_well):
    if chosen_well is None:
        return dash.no_update
    else:
        path = 'C:/Users/pymnb/OneDrive/Desktop/Drilling Project/UI/plotly-dash/Extra/Dataset-Wells/'
        df = pd.read_csv(path +chosen_well+'.csv')
        features = df.columns.values[3:]
        return features


@callback(
    [Output({'type': 'dynamic-graph', 'index': MATCH}, 'figure')],
    [Input({'type': 'well-choice', 'index': MATCH}, 'value'),
     Input({'type': 'feature-choice', 'index': MATCH}, 'value')],
    prevent_initial_call=True
)
def update_graph(chosen_well1, chosen_feature):
    # if the output of the callback is already present in the app layout before its input is inserted into the layout,
    # prevent_initial_call will not prevent its execution when the input is first inserted into the layout.
    if (chosen_feature == []) or (chosen_well1 is None):  # <--- correct the condition
        return dash.no_update
    else:
        path = 'C:/Users/pymnb/OneDrive/Desktop/Drilling Project/UI/plotly-dash/Extra/Dataset-Wells/'
        df = pd.read_csv(path +chosen_well1+'.csv')

        Xmin = df[chosen_feature].min().min()
        Xmax = df[chosen_feature].max().max()
        first_ind = df[chosen_feature].first_valid_index()    # get the index of first feature available
        last_ind = df[chosen_feature].last_valid_index()
        TVDmin = df['TVD'].iloc[first_ind]
        TVDmax = df['TVD'].iloc[last_ind]

        fig1 = px.line(df, x=chosen_feature, y='TVD', color_discrete_sequence=['red', 'blue', 'black', 'purple'])
        fig1.update_layout(style_convas)

        fig1.update_yaxes(range=[TVDmin, TVDmax], showgrid=False)
        fig1.update_xaxes(showgrid=False)

        formation_names = df.Formation.dropna().unique()
        colors = ['#54FF9F', '#87CEFF', '#FFF5EE', '#F0E68C', '#FFA500', '#FFA07A', '#DDA0DD', '#AAAAAA']

        for (i,j) in zip(formation_names, colors):

            index_min = df.loc[df.Formation == i].index[0]
            index_max = df.loc[df.Formation == i].index[-1]
            if index_min == 0:
                TVD_min = df['TVD'][index_min]
            else:
                TVD_min = df['TVD'][index_min-1]
            TVD_max = df['TVD'][index_max]

            fig1.add_shape(type="rect", x0=Xmin, y0=TVD_min, x1=Xmax, y1=TVD_max, fillcolor=j, layer='below', opacity=0.5,
                        line=dict(color="#F8F8FF",width=0.2,))
        return [fig1]