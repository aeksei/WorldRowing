# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go


from scatter_contour_config import *

with open('race_members_1.json', 'r') as f:
    df = pd.DataFrame()
    data = json.load(f)
    all_data = data[2]['data']
    for i in range(len(all_data)):
        for_df = all_data[i]['result_json']
        df_json = pd.read_json(for_df, orient='records')
        df_json['name'] = all_data[i]['name']
        df = df.append(df_json)
    df.to_csv('sgl.csv', encoding='UTF-8')





#
# def filter_speed_stroke_dataframes(df_speed, df_stroke, update=None):
#     local_filter = filter_dict.copy()
#     if update is not None:
#         local_filter.update(update)
#     if (local_filter['championship'] is None) or (local_filter['championship'] == []):
#         local_filter['championship'] = init_championship
#     if (local_filter['class_boat'] is None) or (local_filter['class_boat'] == []):
#         local_filter['class_boat'] = init_boat_classes
#
#     return get_speed_stroke_dataframes(df_speed, df_stroke, local_filter)
#
#
# df_speed_olympic = pd.read_csv('olympic_speed.csv', index_col=0, parse_dates=['date_competition', 'datetime_race'])
# df_stroke_olympic = pd.read_csv('olympic_stroke.csv', index_col=0)
#
# # Инициализируем данные для полей фильтрации
# # TODO return for championship and class_boat by year
# init_championship = df_speed_olympic['championship'].unique().tolist()
# init_boat_classes = df_speed_olympic['class_boat'].unique().tolist()
# init_years = df_speed_olympic['year'].unique().tolist()
# init_year_marks = {str(year): str(year) for year in init_years}
#
# # Начальный фильтр из конфига
# filter_dict = {
#     'championship': init_championship,
#     'class_boat': INIT_BOAT_CLASS,
#     'year': INIT_YEAR
# }
#
# data = get_speed_stroke_dataframes(df_speed_olympic, df_stroke_olympic, filter_dict)
# df_scatter = get_scatter_dataframe(*data)
# df_scatter = df_scatter.sort_values(['stroke', 'speed'])
# df_scatter.to_csv('grouped.csv')
#
# # linear regression
# df_lr = get_linear_regression_dataframe(*data)
# df_lr.to_csv("linear_regression.csv")
#
#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown_championship',
        options=[{'label': champ, 'value': champ} for champ in df['name'].unique()],
        value=df['name'].unique()[0]
    ),

    html.Div([
        html.Div([
            dcc.Graph(
                id="scatter_graph"
            )
        ]),
    ]),

], style={'columnCount': 1})


def get_scatter_graph(df, value):
    df = df.loc[df['name'] == value]
    fig = make_subplots(specs=[[{"secondary_y": True}]])


    # name = 'spm'
    # fig.add_trace(
    #     go.Scatter(x=df['meters'], y=df[name], mode='lines', name=name),
    #     secondary_y=False
    # )
    #
    # name = 'pace'
    # fig.add_trace(
    #     go.Scatter(x=df['meters'], y=df[name], mode='lines', name=name),
    #     secondary_y=True
    # )
    #
    # fig.update_yaxes(title_text="<b>Stroke</b>", secondary_y=False)
    # fig.update_yaxes(title_text="<b>Pece</b>", secondary_y=True)

    name = 'spm'
    fig.add_trace(
        go.Scatter(x=df['meters'], y=df[name], mode='lines', name=name)
    )

    name = 'pace'
    fig.add_trace(
        go.Scatter(x=df['meters'], y=df[name], mode='lines', name=name)
    )

    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=250
        )
    )

    # data = [{
    #     "x": df['meters'],
    #     "y": df['pace'],
    #     "type": "lines"
    # }]

    return fig

@app.callback(
    [Output('scatter_graph', 'figure')],
    [Input('dropdown_championship', 'value')]
)
def plot_scatter_graph(value):
    return [get_scatter_graph(df, value)]


if __name__ == '__main__':
    app.run_server(debug=True)
