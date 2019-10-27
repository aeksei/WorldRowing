# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

filename = 'description.csv'
df = pd.read_csv(filename, index_col=0)

init_years = df['year'].unique()
init_gender = df['gender'].unique()
init_championship = df['championship'].unique()
init_boat_classes = df['class_boat'].unique()

filter_value = {'year': init_years,
                'gender': init_gender,
                'championship': init_championship,
                'class_boat': init_boat_classes}

init_year_marks = {i: str(year) for i, year in enumerate(init_years)}

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
        multi=True
    ),

    html.Label('Gender'),
    dcc.Checklist(
        id='checklist_gender',
        options=[
            {'label': 'Men', 'value': 1},
            {'label': 'Women', 'value': 0},
        ],
        value=init_gender,
        labelStyle={'display': 'inline-block'}
    ),

    html.Div([
        html.Label('Date competition'),
        dcc.RangeSlider(
            id='range_slider_year',
            min=0,
            max=len(init_year_marks) - 1,
            marks=init_year_marks,
            value=[0, len(init_year_marks) - 1]
        )], style={'width': '80%',
                   'margin-left': 'auto',
                   'margin-right': 'auto'}),

    html.Div(id='output-container-range-slider', style={'margin-top': 20})
], style={'columnCount': 1})


@app.callback(
    [dash.dependencies.Output('output-container-range-slider', 'children')],
    [dash.dependencies.Input('range_slider_year', 'value'),
     dash.dependencies.Input('checklist_gender', 'value'),
     dash.dependencies.Input('dropdown_championship', 'value'),
     dash.dependencies.Input('dropdown_boat_classes', 'value')])
def update_graph(value_range_slider_year,
                 value_checklist_gender,
                 value_dropdown_championship,
                 value_dropdown_boat_classes):

    output = []
    output.append(html.Label('You have selected year {} - {}\n'.format(
        filter_value['year'][value_range_slider_year[0]],
        filter_value['year'][value_range_slider_year[1]])))
    output.append(html.Label('You have selected gender {}\n'.format(value_checklist_gender)))
    output.append(html.Label('You have filter gender {}\n'.format(filter_value['gender'])))
    output.append(html.Label('------'))
    output.append(html.Label('You have selected championship {}\n'.format(value_dropdown_championship)))
    output.append(html.Label('You have filter championship {}\n'.format(filter_value['championship'])))
    output.append(html.Label('------'))
    output.append(html.Label('You have selected boat classes {}\n'.format(value_dropdown_boat_classes)))
    output.append(html.Label('You have filter boat classes {}\n'.format(filter_value['class_boat'])))
    return [output]


@app.callback(
    [dash.dependencies.Output('range_slider_year', 'min'),
     dash.dependencies.Output('range_slider_year', 'max'),
     dash.dependencies.Output('range_slider_year', 'marks'),
     dash.dependencies.Output('range_slider_year', 'value')],
    [dash.dependencies.Input('checklist_gender', 'value'),
     dash.dependencies.Input('dropdown_championship', 'value'),
     dash.dependencies.Input('dropdown_boat_classes', 'value')])
def update_range_slider(value_checklist_gender,
                        value_dropdown_championship,
                        value_dropdown_boat_classes):
    if not value_checklist_gender:
        value_checklist_gender = init_gender
    if (value_dropdown_championship is None) or not value_dropdown_championship:
        value_dropdown_championship = init_championship
    if (value_dropdown_boat_classes is None) or not value_dropdown_boat_classes:
        value_dropdown_boat_classes = init_boat_classes

    filter_value.update({"year": init_years,
                         "gender": value_checklist_gender,
                         'championship': value_dropdown_championship,
                         'class_boat': value_dropdown_boat_classes})

    selected = df[filter_value.keys()].isin(filter_value).sum(axis=1)
    selected = df.loc[selected[selected == selected.max()].index]

    years = list(selected['year'].unique())
    filter_value.update({"year": years})

    marks = {i: str(year) for i, year in enumerate(years)}
    min_ = 0
    max_ = len(marks) - 1
    value = [min_, max_]

    return [min_, max_, marks, value]


@app.callback(
    dash.dependencies.Output('dropdown_championship', 'options'),
    [dash.dependencies.Input('checklist_gender', 'value'),
     dash.dependencies.Input('dropdown_boat_classes', 'value')])
def update_dropdown_championship(value_checklist_gender,
                                 value_dropdown_boat_classes,
                                 value_dropdown_championship=None):
    if not value_checklist_gender:
        value_checklist_gender = init_gender
    if (value_dropdown_championship is None) or not value_dropdown_championship:
        value_dropdown_championship = init_championship
    if (value_dropdown_boat_classes is None) or not value_dropdown_boat_classes:
        value_dropdown_boat_classes = init_boat_classes
    filter_value.update({"gender": value_checklist_gender,
                         'class_boat': value_dropdown_boat_classes,
                         'championship': value_dropdown_championship})

    selected = df[filter_value.keys()].isin(filter_value).sum(axis=1)
    selected = df.loc[selected[selected == selected.max()].index]

    championships = list(selected['championship'].unique())
    filter_value.update({"championship": championships})

    options = [{'label': champ, 'value': champ} for champ in sorted(championships)]
    return options

@app.callback(
    dash.dependencies.Output('dropdown_boat_classes', 'options'),
    [dash.dependencies.Input('checklist_gender', 'value'),
     dash.dependencies.Input('dropdown_championship', 'value')])
def update_dropdown_boat_classes(value_checklist_gender,
                                 value_dropdown_championship,
                                 value_dropdown_boat_classes=None):
    if not value_checklist_gender:
        value_checklist_gender = init_gender
    if (value_dropdown_championship is None) or not value_dropdown_championship:
        value_dropdown_championship = init_championship
    if (value_dropdown_boat_classes is None) or not value_dropdown_boat_classes:
        value_dropdown_boat_classes = init_boat_classes
    filter_value.update({"gender": value_checklist_gender,
                         'championship': value_dropdown_championship,
                         'class_boat': value_dropdown_boat_classes})

    selected = df[filter_value.keys()].isin(filter_value).sum(axis=1)
    selected = df.loc[selected[selected == selected.max()].index]

    boat_classes = list(selected['class_boat'].unique())
    filter_value.update({"class_boat": boat_classes})

    options = [{'label': boat, 'value': boat} for boat in sorted(boat_classes)]
    return options


if __name__ == '__main__':
    app.run_server(debug=True)
