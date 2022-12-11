import dash
from dash import Dash, html, dcc, Output, Input, State, MATCH, ALL, callback, ctx
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json
from plotly.subplots import make_subplots


path = 'C:/Users/pymnb/OneDrive/Desktop/Drilling Project/UI/plotly-dash/Extra/Dataset-Wells/'


dash.register_page(__name__, name='Trajectory Analysis')

layout = html.Div([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='dropdown1',
                                options=['Well1'],
                                clearable=True,
                                value=[]
                                )
                ], width=2,
                   style={'margin-left': 90, 'margin-top': 20, 'color': 'black'}
                ),

                dbc.Col([
                    dcc.Dropdown(id='dropdown2',
                                 options=[],
                                 clearable=True,
                                 value=[]
                                 )
                ], width=2,
                    style={'margin-left': 0, 'margin-top': 20, 'color': 'black'}
                ),

                dbc.Col(id='appear_rangeslider', children=[
                    dcc.RangeSlider(0, 100, value=[], allowCross=False, marks=None,
                                    tooltip={"placement": "top", "always_visible": True},
                                    id='my_rangeslider',
                                    )
                ], width=6, style={'width': 335, 'display': 'none'}),
            ]),

            dbc.Row([
                dbc.Col([
                    html.Hr(
                        style={'margin-top': 30, 'margin-right': -255, 'opacity': 0.7, 'color': 'white'}
                    ),
                ])
            ], style={'margin-top': -10},),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='graph3',
                              figure={},
                              style={'width': 600, 'height': 580, 'margin-left': 90}
                              )
                ], width=6),
                dbc.Col([
                    dcc.Graph(id='graph4',
                              figure={},
                              style={'width': 600, 'height': 580, 'margin-left': 90}
                              )
                ], width=6),
            ], style={'margin-left': -100}),

            dbc.Row([
                dbc.Col([
                    dcc.Store(id='table1')
                ]),
            ])
],)


# --------------------------- call back to store and share the df between callbacks ------------------------------------
@callback(
    Output('table1', 'data'),
    Input('dropdown1', 'value'),
    prevent_initial_call=True
)
def store_df(chosen_well):
    if chosen_well is None:
        return dash.no_update
    else:
        df = pd.read_csv(path + chosen_well + '.csv')
        df_json = df.to_json(date_format='iso', orient='split')
    return df_json


# -------------- gets well files from dropdown1 and returns the feature options in dropdown2 ---------------------------
@callback(
    Output('dropdown2', 'options'),
    Input('table1', 'data'),
    prevent_initial_call=True
)
def set_well_options(js_df):
    if js_df is None:
        return dash.no_update
    else:
        dff = pd.read_json(js_df, orient='split')
        features = np.sort(dff.columns.values[2:])
        return features


# ----------------- gets the feature from dropdown 2 and returns the numbers on rangeslider ----------------------------
@callback(
    Output('my_rangeslider', 'min'),
    Output('my_rangeslider', 'max'),
    Output('my_rangeslider', 'marks'),
    Output('my_rangeslider', 'value'),
    Output('appear_rangeslider', 'style'),
    Input('table1', 'data'),
    Input('dropdown2', 'value'),
    prevent_initial_call=True
)
def set_rangeslider_values(js_df, feature):
    if (feature == []) or (feature is None):
        return dash.no_update
    else:
        R = {'display': 'block'}
        dff = pd.read_json(js_df, orient='split')
        minn = round(dff[feature].min(), 2)
        maxx = round(dff[feature].max(), 2)
        min_value = dff[feature].min()
        max_value = dff[feature].max()
        v25 = dff[feature].quantile(0.25)
        v75 = dff[feature].quantile(0.75)
        lower_inner_fence = v25 - 1.5 * (v75 - v25)
        upper_inner_fence = v75 + 1.5 * (v75 - v25)

        marks = {int(lower_inner_fence): {'label': 'Lower Limit', 'style': {'position': 'absolute'}},
                 int(v25): '%25', int(v75): '%75',
                 int(upper_inner_fence): 'Upper Limit'}
        return minn, maxx, marks, [min_value, max_value], R


# --------------- plot trajectory from the stored df & update the plot by moving the rangeslider -----------------------
@callback(
    Output('graph3', 'figure'),
    Input('dropdown1', 'value'),
    Input('my_rangeslider', 'value'),
    Input('table1', 'data'),
    Input('dropdown2', 'value'),
    prevent_initial_call=True
)
def group1(b1, b2, js_df, feature):

    triggered_id = ctx.triggered_id
    print(triggered_id)
    if triggered_id in ['dropdown1', 'dropdown2', 'table1']:
        return plot3d(js_df)
    elif triggered_id == 'my_rangeslider':
        fig = update_with_rangeslider(js_df, feature, b2)
        fig.update_scenes(zaxis_autorange="reversed")
        fig.update_layout(hovermode='closest', margin={'l': 0, 'r': 0, 't': 30, 'b': 0}, showlegend=False,
                          template="plotly_white", uirevision=True),
        return fig


def plot3d(js_df):
    dff = pd.read_json(js_df, orient='split')
    fig = go.Figure()

    unique_holesize = dff["HoleSize"].unique()
    colors = ['#89ffc8', '#42ffa7', '#00d673']

    for index, (value, color) in enumerate(zip(unique_holesize[1:], colors)):
        df_holesize = dff[(dff['HoleSize'] == value)]
        fig.add_trace(go.Scatter3d(x=df_holesize['EW'], y=df_holesize['NS'], z=df_holesize['TVD'],
                                   marker={'color': color, 'size': (10-index*3)},
                                   name='well1', hovertemplate="<b><i>TVD</i>: %{z:.2f}</b>" + "<br><b><i>%{text}</i>"),)

    fig.update_layout(hovermode='closest', margin={'l': 0, 'r': 0, 't': 30, 'b': 0}, showlegend=False, template="plotly_white"),
    fig.update_scenes(zaxis_autorange="reversed")
    return fig


def update_with_rangeslider(js_df, feature, ranges):
    if (feature is None) or (ranges == []):
        return dash.no_update
    else:
        dff = pd.read_json(js_df, orient='split')
        df_sliced_min = dff[(dff[feature] < ranges[0])]
        df_sliced_max = dff[(dff[feature] > ranges[1])]
        fig = go.Figure()

        unique_holesize = dff["HoleSize"].unique()
        colors = ['#89ffc8', '#42ffa7', '#00d673']
        for index, (value, color) in enumerate(zip(unique_holesize[1:], colors)):
            df_holesize1 = dff[(dff['HoleSize'] == value)]
            df_holesize2 = df_sliced_min[(df_sliced_min['HoleSize'] == value)]
            df_holesize3 = df_sliced_max[(df_sliced_max['HoleSize'] == value)]

            fig.add_trace(go.Scatter3d(x=df_holesize2['EW'], y=df_holesize2['NS'], z=df_holesize2['TVD'], mode='markers', marker={'color': '#1F7BAA', 'size': (12 - index * 3)}))
            fig.add_trace(go.Scatter3d(x=df_holesize3['EW'], y=df_holesize3['NS'], z=df_holesize3['TVD'], mode='markers', marker={'color': '#FF206E', 'size': (12 - index * 3)}))
            fig.add_trace(go.Scatter3d(x=df_holesize1['EW'], y=df_holesize1['NS'], z=df_holesize1['TVD'], marker={'color': color, 'size': (10 - index * 3)}))
        fig.update_layout(hovermode='closest', margin={'l': 0, 'r': 0, 't': 30, 'b': 0}, showlegend=False, template="plotly_white")

    return fig


# ------------------------------------ show the feature on hovering plot------------------------------------------------
@callback(
    Output('graph4', 'figure'),
    Input('table1', 'data'),
    Input('dropdown2', 'value'),
    Input('graph3', 'hoverData'),
    prevent_initial_call=True
)
def callback_stats(js_df, feature, hover_data):

    if (hover_data is None) or (feature is None):
        return dash.no_update
    else:
        df = pd.read_json(js_df, orient='split')

        tvd = hover_data['points'][0]['z']
        df1 = df[df['TVD'].between(tvd-50, tvd+50)]

        fig = make_subplots(rows=1, cols=4,
                            shared_yaxes=True,
                            subplot_titles=('ROP5', 'SWOB', 'CCS', 'GR')
                            )
        fig.update_scenes(zaxis_autorange="reversed")

        columns = ['ROP5', 'SWOB', 'CCS', 'GR']
        for idx, name in enumerate(columns):
            fig.add_trace(go.Scatter(name=name, mode='lines', x=df1[name], y=df1['TVD']), row=1, col=idx + 1)
            fig.update_scenes(zaxis_autorange="reversed")

        units = ['ROP()', 'SWOB()', 'CCS(Kpsi)', 'GR()']
        for j, name in enumerate(units):
            fig.update_xaxes(title_text=name, row=1, col=j+1, autorange='reversed')

        fig.update_yaxes(title_text="TVD (m)", row=1, col=1, autorange='reversed')
        fig.update_layout(height=580, width=826, margin={'l': 0, 'r': 0, 't': 50, 'b': 20}, template="plotly_white", showlegend=False)

    return fig