import dash
import dash_core_components as dcc
import dash_html_components as html
from utils import *
import pandas as pd
from dash.dependencies import Input, Output, State, Event
import flask

app = dash.Dash(__name__)
app.css.append_css({
    "external_url": "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"
})
app.config['suppress_callback_exceptions']=True
all = pd.read_csv('./data/processed.csv')
df = get_tops_by_years(all, range(2012, 2017), 50)
selected_titles = []

poster_url_base = 'http://image.tmdb.org/t/p/w185///'



def gen_table(df):
    return html.Table(
        [html.Tr([html.Th(col) for col in df.columns])] +
        [html.Tr([html.Td(row[col]) for col in df.columns])
            for index, row in df.iterrows()]
    )
def get_poster(row):
    return html.Div([
        html.Span(row['title'],
                    style=dict(textAlign='center', display='block', overflow='scroll',
                                width='200px', height='22px')),
        html.Span('(' + str(row['year']) + ')',
                    style=dict(textAlign='center', display='block'))
    ])
def gen_poster(row):
    return html.Label([
        dcc.Input(type='checkbox', name='selected_movies', value=row['title'], style=dict(visibility='hidden')),
        html.Div([
            html.Img(src=poster_url_base+row['poster_path'], className='img-thumbnail'),
            get_poster(row)
        ], style=dict(display='inline-block', width='200px', margin='5px'), className='movie_option')
    ], id=row['title'])

def gen_poster_by_title(df, title):
    return gen_poster(df[df['title' == title]])

def gen_figs(df, id):
    return html.Div([
            gen_poster(row) for index, row in df.iterrows()], id=id)

# url_bar_and_content_div = html.Div([
#     dcc.Location(id='url', refresh=False),
#     html.Div(id='page-content')
# ])

index_page = html.Div(children=[
    html.H4('Welcome! Please select the movies you like from the top rated movies from 2012 to 2017', style={'textAlign': 'center'}, className='jumbotron'),
    gen_figs(df, 'all_movies'),
    html.H4('Your selection:'),
    html.Div(id='output'),
    html.Div(id='output_poster'),
    html.Button('Confirm Selection', id='confirm_selection', className='btn btn-primary')
    # html.Button('Get recommendations', id='get_recommendation_by_title'),
    # dcc.Link('Get recommendations', href='/recommendations_by_titles', id='get_rec'),
    # html.Br(),
    # dcc.Link('Rate Selected Movies', href='/rate_selected_movies')
    # html.Button('Rate these movies', id='rate_these_movies'),
])

rec_by_titles = html.Div('', id='rec_by_titles')


rate_movies = html.Div('', id='rate')

per_recs = html.Div('', id='per_recs')

def serve_layout():
    # if flask.has_request_context():
    #     return url_bar_and_content_div
    return html.Div([
        # url_bar_and_content_div,
        index_page,
        rec_by_titles,
        rate_movies,
        per_recs
    ])

app.layout = serve_layout

#####
movie_titles = df['title'].values.tolist()
# def create_callback(output):
#     def callback(input_value):
#         return input_value
#     return callback
# for title in movie_titles:
#     dynamic_gened_func = create_callback(title)
#     app.callback(Output('output', 'children'), [Input(title, 'value')])(dynamic_gened_func)
@app.callback(
    Output('output', 'children'),
    [Input(title, 'n_clicks') for title in movie_titles],
    [State(title, 'children') for title in movie_titles]
    # [Input('all_movies', 'children')]
)
def update_value(*args):
    n = 50
    selected_titles[:] = []
    for i in range(n):
        if args[i] and (args[i]/2)%2 != 0:
            selected_titles.append(args[n+i][0]['props']['value'])
    # print(args[0])
    print(selected_titles)
    selected_df = df[np.isin(df['title'], selected_titles)]
    # print(selected_df.title)
    # print(type(args[50]))
    # print(type(args[0]))
    # return html.Ul([html.Li(row['title'] + " (" + str(row['year']) + ")", className='list-group-item list-group-item-success')
    #                 for index, row in selected_df.iterrows()], className='list-group')
    return html.Div([html.Img(src=poster_url_base+row['poster_path'], className='img-thumbnail')
                        for index, row in selected_df.iterrows()])

@app.callback(
    Output('rec_by_titles', 'children'),
    [Input('confirm_selection', 'n_clicks')]
)
def get_rec_by_titles(click):
    if click:
        res = get_recommendation_by_titles(all, selected_titles)[['title', 'year', 'weighted_rating', 'poster_path']]
        return html.Div([
            html.H4('You might also like the following based on what you like: '),
            html.Div([html.Img(src=poster_url_base+row['poster_path'], className='img-thumbnail')
                for index, row in res.iterrows()])
        ])
#####


# @app.callback(dash.dependencies.Output('page-content', 'children'),
#               [dash.dependencies.Input('url', 'pathname')])
# def display_page(pathname):
#     if pathname == '/recommendations_by_titles':
#         return rec_by_titles
#     elif pathname == '/rate_selected_movies':
#         return rate_movies
#     elif pathname == '/personalized_recommendations':
#         return per_recs
#     else:
#         return index_page




if __name__ == '__main__':
    app.run_server(debug=True)
