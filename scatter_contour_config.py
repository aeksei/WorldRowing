import pandas as pd

distance_columns = [
    "_50", "_100", "_150", "_200", "_250", "_300", "_350", "_400", "_450","_500",
    "_550", "_600", "_650", "_700", "_750", "_800", "_850", "_900", "_950", "_1000",
    "_1050", "_1100", "_1150", "_1200", "_1250", "_1300", "_1350", "_1400", "_1450", "_1500",
    "_1550", "_1600", "_1650", "_1700", "_1750", "_1800", "_1850", "_1900", "_1950", "_2000"
]

INIT_BOAT_CLASS = 'M1x'
INIT_YEAR = 2019
MAX_BUBBLE = 25.


def get_speed_stroke_dataframes(df_speed, df_stroke, filter_dict):
    filtered_index = df_speed.index
    for column, value in filter_dict.items():
        if not isinstance(value, list):
            value = [value]
        filtered_index = filtered_index & df_speed.loc[df_speed[column].isin(value)].index
        print(column, len(filtered_index))
    return df_speed.loc[filtered_index], df_stroke.loc[filtered_index]


def get_scatter_dataframe(df_speed, df_stroke):
    df = pd.DataFrame()
    for date_race in sorted(df_speed['datetime_race'].dt.date.unique()):
        index = df_speed[df_speed['datetime_race'].dt.date == date_race].index
        speed = df_speed.loc[index, distance_columns].values.flatten()
        stroke = df_stroke.loc[index, distance_columns].values.flatten()

        df_plot = pd.Series(zip(stroke, speed, )).value_counts().reset_index(name='count')
        df_plot['datetime_race'] = date_race
        df_plot['date_competition'] = df_speed.loc[index, 'date_competition'].iloc[0].date()
        df = df.append(df_plot, ignore_index=True)

    # filter test
    df = df[df['count'] > 3].reset_index(drop=True)
    df[['stroke', 'speed']] = pd.DataFrame(df['index'].tolist(), index=df.index)
    return df