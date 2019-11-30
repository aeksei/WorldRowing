# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np

from scatter_contour_config import *

def filter_speed_stroke_dataframes(df_speed, df_stroke, update=None):
    local_filter = filter_dict.copy()
    if update is not None:
        local_filter.update(update)
    if (local_filter['championship'] is None) or (local_filter['championship'] == []):
        local_filter['championship'] = init_championship
    if (local_filter['class_boat'] is None) or (local_filter['class_boat'] == []):
        local_filter['class_boat'] = init_boat_classes

    return get_speed_stroke_dataframes(df_speed, df_stroke, local_filter)

df_speed_olympic = pd.read_csv('olympic_speed.csv', index_col = 0, parse_dates=['date_competition', 'datetime_race'])
df_stroke_olympic = pd.read_csv('olympic_stroke.csv', index_col = 0)

# Инициализируем данные для полей фильтрации
# TODO return for championship and class_boat by year
init_championship = df_speed_olympic['championship'].unique().tolist()
init_boat_classes = df_speed_olympic['class_boat'].unique().tolist()
init_years = df_speed_olympic['year'].unique().tolist()
init_year_marks = {str(year): str(year) for year in init_years}

# Начальный фильтр из конфига
filter_dict = {
    'championship': init_championship,
    'class_boat': INIT_BOAT_CLASS,
    'year': INIT_YEAR
}

data = get_speed_stroke_dataframes(df_speed_olympic, df_stroke_olympic, filter_dict)
df_scatter = get_scatter_dataframe(*data)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Label('Championship'),
    dcc.Dropdown(
        id='dropdown_championship',
        options=[{'label': champ, 'value': champ} for champ in sorted(init_championship)],
        multi=True
    ),

    html.Label('Boat classes'),
    dcc.Dropdown(
        id='dropdown_boat_classes',
        options=[{'label': boat_class, 'value': boat_class} for boat_class in sorted(init_boat_classes)],
        value=INIT_BOAT_CLASS
    ),

    html.Div([
        html.Div([
            dcc.Graph(
                id="scatter_graph"
            )
        ]),
        html.Div([
            dcc.Graph(
                id="contour_graph"
            )
        ]),
    ], style={'columnCount': 2}),

    html.Div([
        dcc.Slider(
            id='slider_year',
            min=df_speed_olympic['year'].min(),
            max=df_speed_olympic['year'].max(),
            marks=init_year_marks,
            value=df_speed_olympic['year'].max(),
            step=None
        )], style={'width': '80%',
                   'margin-left': 'auto',
                   'margin-right': 'auto'}),

    html.Div(id='output-container-range-slider', style={'margin-top': 20})
], style={'columnCount': 1})


def get_scatter_graph(df, selection, selectedpoints, by='datetime_race'):
    max_bubble = MAX_BUBBLE
    x_col = 'stroke'
    y_col = 'speed'

    data = [dict(
        type='scatter',
        mode='markers',
        x=df['stroke'],
        y=df['speed'],
        customdata=df.index,
        text=[f'Counts: {c}' for c in df['count']],
        selectedpoints=selectedpoints,
        marker=dict(
            size=df['count'],
            sizemode='area',
            sizeref=2. * max(df['count']) / (max_bubble ** 2),
            colorscale="Viridis",
            # opacity=0.8
        ),
        unselected=dict(
            marker=dict(opacity=0.3),
            # make text transparent when not selected
            textfont=dict(color='rgba(0, 0, 0, 0)')
        ),
        transforms=[
            dict(
                type='groupby',
                groups=df[by]
            )
        ]
    )]

    if selection and selection['range']:
        ranges = selection['range']
        selection_bounds = {'x0': ranges['x'][0], 'x1': ranges['x'][1],
                            'y0': ranges['y'][0], 'y1': ranges['y'][1]}
    else:
        selection_bounds = {'x0': df[x_col].min(), 'x1': df[x_col].max(),
                            'y0': df[y_col].min(), 'y1': df[y_col].max()}

    return {
        'data': data,
        'layout': {
            'margin': {'l': 20, 'r': 0, 'b': 15, 't': 5},
            'dragmode': 'select',
            'hovermode': False,
            # Display a rectangle to highlight the previously selected region
            'shapes': [dict({
                'type': 'rect',
                'line': {'width': 1, 'dash': 'dot', 'color': 'darkgrey'}
            }, **selection_bounds
            )]
        }
    }

@app.callback(
    [Output('scatter_graph', 'figure')],
    [Input('dropdown_championship', 'value'),
     Input('dropdown_boat_classes', 'value'),
     Input('slider_year', 'value'),
     Input('scatter_graph', 'selectedData')]
)
def plot_scatter_graph(value_dropdown_championship, value_dropdown_boat_classes, value_slider_year, selection):
    global data
    global df
    filter_update = {
        'championship': value_dropdown_championship,
        'class_boat': value_dropdown_boat_classes,
        'year': value_slider_year
    }
    if filter_dict != filter_update:
        filter_dict.update(filter_update)
        data = filter_speed_stroke_dataframes(df_speed_olympic, df_stroke_olympic, filter_dict)
        df = get_scatter_dataframe(*data)
        selection = None

    selectedpoints = df.index
    if selection and selection['points']:
        selectedpoints = np.intersect1d(selectedpoints,
                                        [p['customdata'] for p in selection['points']])

    print(selection)
    print(selectedpoints)
    return [get_scatter_graph(df, selection, selectedpoints)]


if __name__ == '__main__':
    app.run_server(debug=True)
