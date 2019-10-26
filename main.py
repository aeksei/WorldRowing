# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

filename = 'description.csv'
df = pd.read_csv(filename, index_col=0)
filter_value = {'date_competition': df['year'].unique(),
                'gender': [1, 0], }


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Label('Championship'),
    dcc.Dropdown(
        id='dropdown_championship',
        options=[{'label': champ, 'value': champ} for champ in sorted(df['championship'].unique())],
        multi=True
    ),

    html.Label('Boat classes'),
    dcc.Dropdown(
        id='dropdown_boat_classes',
        options=[{'label': boat_class, 'value': boat_class} for boat_class in df['class_boat'].unique()],
        multi=True
    ),

    html.Label('Gender'),
    dcc.Checklist(
        id='checklist_gender',
        options=[
            {'label': 'Men', 'value': 1},
            {'label': 'Women', 'value': 0},
        ],
        value=filter_value['gender'],
        labelStyle={'display': 'inline-block'}
    ),

    html.Div([
        html.Label('Date competition'),
        dcc.RangeSlider(
            id='range_slider_date_competition'
        )], style={'width': '80%',
                   'margin-left': 'auto',
                   'margin-right': 'auto'}),

    html.Div(id='output-container-range-slider', style={'margin-top': 20})
], style={'columnCount': 1})


@app.callback(
    [dash.dependencies.Output('output-container-range-slider', 'children')],
    [dash.dependencies.Input('range_slider_date_competition', 'value'),
     dash.dependencies.Input('checklist_gender', 'value'),
     dash.dependencies.Input('dropdown_championship', 'value')])
def update_output(value_range_slider_date_competition, value_checklist_gender, value_dropdown_championship):
    output = ""
    output += 'You have selected year {} - {}\n'.format(
        filter_value['date_competition'][value_range_slider_date_competition[0]],
        filter_value['date_competition'][value_range_slider_date_competition[1]])
    output += 'You have selected gender {}\n'.format(value_checklist_gender)
    output += 'You have selected gender {}\n'.format(value_dropdown_championship)
    return [output]


@app.callback(
    [dash.dependencies.Output('range_slider_date_competition', 'min'),
     dash.dependencies.Output('range_slider_date_competition', 'max'),
     dash.dependencies.Output('range_slider_date_competition', 'marks'),
     dash.dependencies.Output('range_slider_date_competition', 'value')],
    [dash.dependencies.Input('checklist_gender', 'value'),
     dash.dependencies.Input('dropdown_championship', 'value')])
def update_range_slider(value_checklist_gender,
                        value_dropdown_championship):
    if (value_dropdown_championship is None) or (value_dropdown_championship == []):
        value_dropdown_championship = df['championship'].unique()

    if (value_checklist_gender is None) or (value_checklist_gender == []):
        value_checklist_gender = df['gender'].unique()

    filtered = {"gender": value_checklist_gender,
                'championship': value_dropdown_championship}

    selected = df[filtered.keys()].isin(filtered).sum(axis=1)
    selected = df.loc[selected[selected == selected.max()].index]

    marks = {i: str(year) for i, year in enumerate(selected['year'].unique())}

    min_ = 0
    max_ = len(marks) - 1
    value = [min_, max_]

    return [min_, max_, marks, value]


if __name__ == '__main__':
    app.run_server(debug=True)
