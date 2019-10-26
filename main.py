# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

filename = 'description.csv'
df = pd.read_csv(filename, index_col=0)
df_selected = df
filter_value = {'date_competition': df_selected['year'].unique(),
                'gender': [1, 0], }

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Label('Championship'),
    dcc.Dropdown(
        options=[{'label': champ, 'value': champ} for champ in df_selected['championship'].unique()],
        multi=True
    ),

    html.Label('Multi-Select Dropdown'),
    dcc.Dropdown(
        options=[
            {'label': 'New York City', 'value': 'NYC'},
            {'label': u'Montréal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        multi=True
    ),

    html.Label('Gender'),
    dcc.Checklist(
        id='checklist_gender',
        options=[
            {'label': 'Men', 'value': 1},
            {'label': u'Women', 'value': 0},
        ],
        value=filter_value['gender'],
        labelStyle={'display': 'inline-block'}
    ),

    html.Div([
        html.Label('Date competition'),
        dcc.RangeSlider(
            id='range_slider_date_competition',
            min=0,
            max=len(df_selected['year'].unique()) - 1,
            value=[0, len(df_selected['year'].unique()) - 1],
            marks={i: str(year) for i, year in enumerate(df_selected['year'].unique())},
        )], style={'width': '80%',
                   'margin-left': 'auto',
                   'margin-right': 'auto'}),

    html.Div(id='output-container-range-slider', style={'margin-top': 20})
], style={'columnCount': 1})


@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('range_slider_date_competition', 'value')])
def update_output(value):
    output = ""
    output += 'You have selected year {} - {}\n'.format(filter_value['date_competition'][value[0]],
                                                        filter_value['date_competition'][value[1]])

    return output


if __name__ == '__main__':
    app.run_server(debug=True)
