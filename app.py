import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

colors = {
    'bg': '#0C0F0A',
    'text': '#FFFFFF',
    'legend-text': '#C4CFC7',
    'x-axis': '#FFFFFF',
    'y-axis': '#1F7BAA',
    'sidebar-header': '#926DDE',
    'sidebar': '#242A33',
}

plot_colors = ['#00D1E2', '#96E7BE', '#9F4D97', '#F3CAD2', '#B4EFE9', '#FF206E']

# **********************************************************************************************************************
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SUPERHERO])

sidebar = dbc.Nav([
            dbc.NavLink([
                html.Div(page["name"], className="ms-2", style={'background-color': colors['sidebar']}),
            ],  href=page["path"], style={'color': colors['text'], 'background-color': colors['sidebar']},
                active="exact",
            )

            for page in dash.page_registry.values()
         ], vertical=True,
            pills=True,
            className="bg-light",
            style={'background-color': "red"}
)
# **********************************************************************************************************************

download_icon = DashIconify(icon='ic:baseline-menu', width=30, style={})

app.layout = dbc.Container([

    dbc.Row([

        dbc.Col([
            dbc.Button([download_icon, ''], id="open-offcanvas", n_clicks=0),
        ], width=1,
           style={'margin-left': 10,
                  'margin-top': 5,
                  'padding': 0,}
        ),

        dbc.Col([
            html.Div(id='page-content')
        ], width=10,
           style={'textAlign': 'center',
                  'fontSize': 40,
                  'margin-top': 10}
        ),
        dbc.Col([
            dcc.Location(id='url', refresh=False)
        ], width=1)
    ]),

    html.Hr(
        style={'margin-top': 0, 'opacity': 1, 'color': 'white'}
    ),

    dbc.Row([
        dbc.Offcanvas(
            dbc.Col([sidebar], width=12),
            id="offcanvas", title="Challenges", is_open=False,
            style={'width': 300, 'top': 60,
                   # 'border-color': 'gray', 'border-width': 5,
                   'background-color': colors['sidebar'],
            },


        ),
    ],),

    dbc.Row([
        dbc.Col([dash.page_container], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10)
    ])
], fluid=True,
    style={'background-color': colors['bg']})


@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


# This callback is for having a dynamic page title
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    style_title = {'fontSize': 40,
                   'textAlign': 'right',
                   'color': colors['text']},

    if pathname == '/':
        return html.Div([html.H3(f'Drilling Dashboard-Single Well Analysis')])
    elif pathname == '/trajectory':
        return html.Div([html.H3(f'Drilling Dashboard-Trajectory')])
    elif pathname == '/heatmap':
        return html.Div([html.H3(f'Drilling Dashboard-HeatMap')])
    elif pathname == '/rock strength':
        return html.Div([html.H3(f'Drilling Dashboard-Rock Strength')])


if __name__ == "__main__":
    app.run(debug=True, port=5044)