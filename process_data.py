import pandas as pd
import numpy as np
import seaborn as sns
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from nltk.stem.snowball import SnowballStemmer

movie_md = pd.read_csv('./data/movies_metadata.csv', low_memory=False)
df = movie_md.copy()

def process_genres(df):
    '''
    process genres column using liter_eval to convert string to python object
    '''
    df['genres'] = df['genres'].fillna('[]').apply(literal_eval)
    # extract the 'name' value of genres
    df['genres'] = df['genres'].apply(lambda x: [i['name'] for i in x])

process_genres(df)
df['year'] = df['release_date'].apply(lambda x: str(x)[:4] if x != 'NaN' else np.nan)

def process_vote(df, vote_count_cutoff_percentile=0.95):
    df = df.dropna(subset=['vote_count', 'vote_average'])
    df.vote_count = df.vote_count.astype('int')
    df.vote_average = df.vote_average.astype('int')
    print(df.shape)
    mean_vote_average = df.vote_average.mean()
    vote_count_cutoff = df.vote_count.quantile(vote_count_cutoff_percentile)
    df = df.loc[df['vote_count'] >= vote_count_cutoff]
    df['weighted_rating'] = (df.vote_average * df.vote_count/(df.vote_count + vote_count_cutoff)) + \
                            (mean_vote_average * vote_count_cutoff/(df.vote_count + vote_count_cutoff))
    df = df.sort_values('weighted_rating', ascending=False)
    return df

df = process_vote(df)
FEATURES = ['title', 'year', 'vote_count', 'vote_average', 'popularity',
            'genres', 'weighted_rating', 'tagline', 'overview', 'id',
            'poster_path']
df = df[FEATURES]

def get_tops_by_genres(df, *genres, intersect=True, top=10):
    if not genres:
        return df.head(top)
    elif not intersect:
        return df[df['genres'].apply(lambda x: not set(genres).isdisjoint(x))].head(top)
    else:
        return df[df['genres'].apply(lambda x: set(genres).issubset(x))].head(top)

def get_tops_by_year(df, year, top=10):
    return df[df.year == str(year)].head(top)

df.tagline.fillna('', inplace=True)
df.overview.fillna('', inplace=True)
df['description'] = df.overview + df.tagline

title_to_idx = {title: idx for title, idx in zip(df.title, range(df.shape[0]))}
title_to_idx['Inception']

def get_recommendation_by_title(df, title, cosine_sim, top=10):
    idx = title_to_idx[title]
    scores = sorted(list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True)
    movie_indices = list(map(lambda x: x[0], scores[1:top+1]))
    return df.iloc[movie_indices].sort_values('weighted_rating', ascending=False)

credits = pd.read_csv('./data/credits.csv')
keywords = pd.read_csv('./data/keywords.csv')

df['id'] = df['id'].astype(int)
df = df.merge(credits, on='id')
df = df.merge(keywords, on='id')
df['cast'] = df['cast'].fillna('[]').apply(lambda x: [str.lower(i['name'].replace(" ","")) for i in literal_eval(x)][:3])
def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return [str.lower(i['name'].replace(' ', ''))]
    return np.nan

df['crew'] = df['crew'].fillna('[]').apply(lambda x: get_director(literal_eval(x)))
# process keywords

stemmer = SnowballStemmer('english')
df['keywords'] = df['keywords'].fillna('[]').apply(lambda x: [str.lower(stemmer.stem(i['name'].replace(' ', ''))) for i in literal_eval(x)])
df['mixed_credits'] = df['genres'] + df['cast'] + df['crew'] * 3 + df['keywords']
df['mixed_credits'] = df['mixed_credits'].apply(lambda x: ' '.join(x))

tf2 = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
tfidf_matrix2 = tf2.fit_transform(df['mixed_credits'])

cosine_sim_mixed = cosine_similarity(tfidf_matrix2, tfidf_matrix2)
# print(get_recommendation_by_title(df, 'The Dark Knight', cosine_sim_mixed))

df.to_csv('./data/processed.csv')
