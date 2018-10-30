import pandas as pd
import numpy as np
# import seaborn as sns
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from nltk.stem.snowball import SnowballStemmer

def get_tops_by_genres(df, *genres, intersect=True, top=10):
    if not genres:
        return df.head(top)
    elif not intersect:
        return df[df['genres'].apply(lambda x: not set(genres).isdisjoint(x))].head(top)
    else:
        return df[df['genres'].apply(lambda x: set(genres).issubset(x))].head(top)

def get_tops_by_years(df, years, top=10):
    return df[np.isin(df.year, years)].head(top)

def get_recommendation_by_title(df, title, top=10):
    title_to_idx = {title: idx for title, idx in zip(df.title, range(df.shape[0]))}
    idx = title_to_idx[title]
    tf2 = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
    tfidf_matrix2 = tf2.fit_transform(df['mixed_credits'])
    cosine_sim = cosine_similarity(tfidf_matrix2, tfidf_matrix2)
    scores = sorted(list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True)
    movie_indices = list(map(lambda x: x[0], scores[1:top+1]))
    return df.iloc[movie_indices].sort_values('weighted_rating', ascending=False)

def get_recommendation_by_titles(df, titles, top=10):
    rec_titles = set([])
    # print(get_recommendation_by_title(df, 'Toy Story').title)
    for title in titles:
        print(title)
        recs = set(get_recommendation_by_title(df, title)['title'].values)
        print(recs)
        rec_titles = rec_titles.union(recs)
    res = df[np.isin(df['title'], list(rec_titles))].sort_values('weighted_rating', ascending=False)
    return res


# df = pd.read_csv('./data/processed.csv')
# print(get_recommendation_by_title(df, 'The Dark Knight').title)
