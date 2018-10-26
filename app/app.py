import dash
import dash_core_components as dcc
import dash_html_components as html
from utils import *
import pandas as pd

app = dash.Dash(__name__)

df = pd.read_csv('../data/processed.csv')
df = get_tops_by_year(df, 2014)
# df = df[['title', 'year', 'poster']]

poster_url_base = 'http://image.tmdb.org/t/p/w185///'

def gen_table(df):
    return html.Table(
        [html.Tr([html.Th(col) for col in df.columns])] +
        [html.Tr([html.Td(row[col]) for col in df.columns])
            for index, row in df.iterrows()]
    )

def gen_figs(df):
    return html.Ul(
        [html.Li(
            html.Div([
                html.Img(src=poster_url_base+row['poster_path']),
                html.P(row['title'] + ' (' + str(row['year']) + ')')
            ])
        ) for index, row in df.iterrows()]
    )

app.layout = html.Div(children=[
    html.H4('Welcome!', style={'textAlign': 'center'}),
    gen_figs(df)
])


if __name__ == '__main__':
    app.run_server(debug=True)
