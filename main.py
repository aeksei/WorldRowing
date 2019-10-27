# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def filter_df(df, update=None):
    local_filter = filter_value.copy()
    if update is not None:
        local_filter.update(update)
    if local_filter['gender'] == []:
        local_filter['gender'] = init_gender
    if (local_filter['championship'] is None) or (local_filter['championship'] == []):
        local_filter['championship'] = init_championship
    if (local_filter['class_boat'] is None) or (local_filter['class_boat'] == []):
        local_filter['class_boat'] = init_boat_classes

    selected = df[local_filter.keys()].isin(local_filter).sum(axis=1)
    selected = df.loc[selected[selected == selected.max()].index]
    return selected


filename = 'description.csv'
df_description = pd.read_csv(filename, index_col=0)
df_data = pd.read_csv("data.csv", index_col=0)

init_years = df_description['year'].unique()
init_gender = df_description['gender'].unique()
init_championship = df_description['championship'].unique()
init_boat_classes = df_description['class_boat'].unique()

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

    html.Label('Boat classes'),
    dcc.Dropdown(
        id='dropdown_boat_classes',
        options=[{'label': boat_class, 'value': boat_class} for boat_class in sorted(init_boat_classes)],
        multi=True
    ),

    html.Div([
        dcc.Graph(
            id="bar_plot_total_time"
        ),
    ]),

    html.Div([
        # html.Label('Date competition'),
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
    filter_value.update({"gender": value_checklist_gender,
                         'championship': value_dropdown_championship,
                         'class_boat': value_dropdown_boat_classes})

    selected = filter_df(df_description, {"year": init_years})
    years = selected['year'].unique()
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
                                 value_dropdown_boat_classes):
    filter_value.update({"gender": value_checklist_gender,
                         'class_boat': value_dropdown_boat_classes})

    selected = filter_df(df_description, {"championship": init_championship})

    championships = selected['championship'].unique()
    filter_value.update({"championship": championships})

    options = [{'label': champ, 'value': champ} for champ in sorted(championships)]
    return options


@app.callback(
    dash.dependencies.Output('dropdown_boat_classes', 'options'),
    [dash.dependencies.Input('checklist_gender', 'value'),
     dash.dependencies.Input('dropdown_championship', 'value')])
def update_dropdown_boat_classes(value_checklist_gender,
                                 value_dropdown_championship):
    filter_value.update({"gender": value_checklist_gender,
                         'championship': value_dropdown_championship})
    selected = filter_df(df_description, {'class_boat': init_boat_classes})

    boat_classes = selected['class_boat'].unique()
    filter_value.update({"class_boat": boat_classes})
    options = [{'label': boat, 'value': boat} for boat in sorted(boat_classes)]
    return options

@app.callback(
    dash.dependencies.Output('bar_plot_total_time', 'figure'),
    [dash.dependencies.Input('range_slider_year', 'value'),
     dash.dependencies.Input('checklist_gender', 'value'),
     dash.dependencies.Input('dropdown_championship', 'value'),
     dash.dependencies.Input('dropdown_boat_classes', 'value')])
def update_split_time(value_range_slider_year,
                      value_checklist_gender,
                      value_dropdown_championship,
                      value_dropdown_boat_classes):
    # TODO uuid index in data and desc

    years = filter_value['year'][value_range_slider_year[0]:value_range_slider_year[1]]

    df_description_index = filter_df(df_description, {'year': years}).index

    df = df_data.loc[df_description_index, :]

    fig = make_subplots(
        rows=1, cols=2, subplot_titles=('Последовательность мест по общему времени среди всех спортсменов заезда',
                                        'Ранжирование личного среднего времени на протяжении заезда'))

    color = ['indianred', 'lightsalmon']
    place = 1
    for i, col in enumerate([['total_rank_common'], ['split_rank_self']], start=1):
        plot_total_rank_common = df.loc[df['_2000m_total_rank'] == place, col + ["_2000m_total_rank"]].groupby(
            by=col).count()
        plot_total_rank_common = plot_total_rank_common.sort_values(by=["_2000m_total_rank"], ascending=False).iloc[:15]
        fig.add_trace(
            go.Bar(
                x=plot_total_rank_common.index,
                y=plot_total_rank_common['_2000m_total_rank'],
                name=place,
                marker_color=color[place - 1]),
            row=1, col=i
        )

    fig.update_layout(showlegend=False)
    return {
        'data': fig['data'],
        'layout': fig['layout']
    }

    # output = []
    # output.append(html.Label('You have selected year {} - {}\n'.format(filter_value['year'][value_range_slider_year[0]],
    #                                                                    filter_value['year'][value_range_slider_year[1]])))
    # output.append(html.Label('You have available year {}\n'.format(filter_value['year'])))
    # output.append(html.Label('------'))
    # output.append(html.Label('You have selected gender {}\n'.format(value_checklist_gender)))
    # output.append(html.Label('You have available gender {}\n'.format(filter_value['gender'])))
    # output.append(html.Label('------'))
    # output.append(html.Label('You have selected championship {}\n'.format(value_dropdown_championship)))
    # output.append(html.Label('You have available championship {}\n'.format(filter_value['championship'])))
    # output.append(html.Label('------'))
    # output.append(html.Label('You have selected boat classes {}\n'.format(value_dropdown_boat_classes)))
    # output.append(html.Label('You have available boat classes {}\n'.format(filter_value['class_boat'])))


if __name__ == '__main__':
    app.run_server(debug=True)
