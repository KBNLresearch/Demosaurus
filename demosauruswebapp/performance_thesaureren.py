from importlib import reload
import scipy

import warnings
warnings.simplefilter('ignore',FutureWarning)
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd

#import dataprocessing.views_and_indices as views
import demosaurus
import os.path

from dataprocessing.views import author_aggregated_query

def f_name(name, outdir = 'NBD'):
    return os.path.join(outdir, f'{name}.csv')

def data_exists(name, outdir = 'NBD'):
    return os.path.exists(f_name(name, outdir = outdir))

def load_data(name, outdir = 'NBD'):
    fname = f'{name}.csv'
    df = pd.read_csv(os.path.join(outdir, fname))
    return df

def save_data(df, name, outdir = 'NBD', overwrite=False):
    if not overwrite and data_exists(name, outdir = outdir):
        print('Not overwriting', f_name(name, outdir=outdir))
        pass
    else:
        df.to_csv(f_name(name, outdir=outdir), index=False)

def query_to_df(query):
    with app.app_context() as context:
        with demosaurus.db.get_db() as con:
            df = pd.read_sql_query(query, con=con)
    return df

app = demosaurus.create_app()


def obtain_candidates(test_items=None, outdir='NBD', overwrite = False):
    if test_items is None:
        test_items = obtain_test_items(outdir=outdir)
    names = test_items.name_normalized
    query = "SELECT * FROM "

    return

def obtain_test_items(outdir='NBD', overwrite = False, mock = 0):
    t_name = 'test_items'+('_mock'+str(mock) if mock else '')
    if data_exists(t_name):
        test_items =  load_data(t_name,outdir=outdir)
    else:
        if mock:
            query = """SELECT publication_ppn, rank, role, author_ppn FROM publication_contributors_test_NBD WHERE author_ppn IS NOT NULL"""
            true_items = query_to_df(query)
            test_items = pd.concat(9*[true_items], ignore_index = True)
            test_items['candidate_ppn'] = true_items.author_ppn.sample(len(test_items), replace = True).values # sample 9 random authors from the test set
            test_items['target'] = test_items.apply(lambda row: int(row.author_ppn == row.candidate_ppn), axis =1)
            true_items['candidate_ppn'] = true_items['author_ppn']
            true_items['target'] = 1
            test_items = pd.concat([test_items,true_items], ignore_index = True) # add the true author to the candidates
        else:
            query = """SELECT t1.publication_ppn, t1.rank, t1.author_ppn, t1.name_normalized, t2.author_ppn AS candidate_author_ppn, t2.author_ppn = t1.author_ppn AS target
            FROM publication_contributors_test_NBD t1
            LEFT JOIN 
            (	SELECT t3.* FROM author_name_options t3
                JOIN publication_contributors_train_NBD t4 ON t3.author_ppn = t4.author_ppn) AS t2
                ON t2.name_normalized = t1.name_normalized
            GROUP BY t1.publication_ppn, t1.rank, t2.author_ppn"""
            test_items = query_to_df(query)
        save_data(test_items, t_name, outdir=outdir)
    return test_items



def obtain_similarity_data(outdir='NBD'):
    if data_exists('author_aggregated'):
        df = load_data('author_aggregated', outdir=outdir)
    else:
        query = "SELECT * FROM author_aggregated"
        df = query_to_df(query)
        save_data(df, 'author_aggregated', outdir=outdir)
    return df
#name: "{{contributor['title'] if contributor['title']}}{{' '.join([contributor['firstname'] or '',contributor['prefix'] or '','@' + contributor['familyname'] or ''])}}",

def testset_query():

    testset_query = """
    SELECT t1.*, t2.titelvermelding, t2.jaar_van_uitgave,
    group_concat(DISTINCT t3.CBK_genre) AS CBK_genres,
    group_concat(DISTINCT t4.brinkman) AS Brinkman_vorm 
    FROM authorship_ggc_test t1
    JOIN publication_basicinfo t2 on t2.publication_ppn = t1.publication_ppn 
    LEFT JOIN publication_CBK_genre t3 on t3.publication_ppn = t1.publication_ppn 
    LEFT JOIN publication_brinkman t4 on t4.publication_ppn = t1.publication_ppn 
    LEFT JOIN thesaurus_brinkmantrefwoorden t5 ON t4.brinkman = t5.ppn AND t5.kind=='vorm'
    GROUP BY t1.publication_ppn 
    LIMIT 250
    """

def obtain_publication_data(outdir='NBD'):
    if data_exists('publications_wrapped', outdir=outdir):
        df = load_data('publications_wrapped', outdir=outdir)
    else:
        # Like views_and_indices aggregated_author_query with the following changes:
        #q = dataprocessing.views_and_indices.author_aggregated_query(ignore=['role'])
        q = author_aggregated_query(ignore=['role'])
        q = q.replace('publication_contributors_train_NBD',
                      'publication_contributors_test_NBD')  # use test data as selection criterion
        q = q.replace('SELECT t0.publication_ppn, t0.author_ppn',
                      'SELECT DISTINCT t0.publication_ppn')  # (aggregate on publication level rather than author level)
        q = q.replace('t1.author_ppn',
                      't1.publication_ppn')  # (aggregate on publication level rather than author level)
        q = q.replace('AS knownPublications', 'AS this_publication')
        q = q.replace('WHERE t0.author_ppn IS NOT NULL', '')
        df = query_to_df(q)
        save_data(df, 'publications_wrapped', outdir=outdir)
    return df

def score_itemset(test_item_set, wrapped_publication, similarity_data):
    """
    Compute performance for a set of test items with
    """
    #assert test_item_set.name
    wrapped_publication = pd.concat([wrapped_publication,
        pd.DataFrame.from_dict({'publication_ppn':[test_item_set.name],
                    'term': [test_item_set.role.iloc[0]],
                    'term_description': ['role'],
                    'this_publication': [1]
                  })])
    scores = test_item_set.groupby('candidate_ppn').apply(
        lambda author: \
            pd.merge(wrapped_publication, # this merge raises a FutureWarning that I don't understand
                     similarity_data.loc[similarity_data.author_ppn == author.name],
                     how='outer') \
            .fillna(0).groupby(['term_description'])\
                .apply(demosaurus.link_thesaurus.score_feature) \
                .groupby(['term_category'])
                    .apply(lambda x:
                        pd.Series([np.average(x.score, weights=x.confidence),
                                   x.confidence.mean()] if sum(x.confidence)>0 else [0,0],
                                index=['score', 'confidence']))
               ).unstack()
    scores.columns = [i[1] + '_' + i[0] for i in scores.columns.to_flat_index()]  # flatten column index
    feature_list = ['genre', 'year', 'role']
    score_items = [feature + '_score' for feature in feature_list]
    weight_items = [feature + '_confidence' for feature in feature_list]
    scores['score'] = scores.apply(
        lambda row: np.average(row.loc[score_items], weights=row.loc[weight_items]) if sum(
            row.loc[weight_items]) > 0 else 0, axis=1)
    scores['support'] = scores.apply(
        lambda row: np.mean(row.loc[weight_items]), axis=1)
    return scores

def score_test_items(test_items, similarity_data, publication_data, filename, outdir='NBD', overwrite = True):
    if data_exists(filename, outdir=outdir):
        scores = load_data(filename, outdir=outdir)
    else:
        scores = test_items.merge(test_items.groupby(['publication_ppn', 'author_ppn']).apply(
            lambda test_item_set: score_itemset(
                test_item_set,
                publication_data.loc[publication_data.publication_ppn == test_item_set.name[0]],
                similarity_data)),
            left_on=['publication_ppn', 'author_ppn', 'candidate_ppn'], right_index=True)
        save_data(scores, filename, outdir=outdir)
    return scores

def compute_performance(scores):
    scores['rank_score'] = scores.groupby(['publication_ppn', 'author_ppn'])['score'].rank(ascending=False)
    scores['rank_genre'] = scores.groupby(['publication_ppn', 'author_ppn'])['genre_score'].rank(ascending=False)
    scores['rank_role'] = scores.groupby(['publication_ppn', 'author_ppn'])['role_score'].rank(ascending=False)
    scores['rank_year'] = scores.groupby(['publication_ppn', 'author_ppn'])['year_score'].rank(ascending=False)

    target_scores_all = scores.loc[scores.target == 1]
    no_info = len(target_scores_all.loc[target_scores_all.support == 0])
    target_scores = target_scores_all.loc[target_scores_all.support > 0]

    features = {'Overall': 'rank_score', 'Genre': 'rank_genre', 'Role': 'rank_role', 'Year': 'rank_year'}
    recalls = pd.DataFrame({feat: {
        f'recall@{i}': len(target_scores.loc[target_scores[feat_col] <= i]) / len(target_scores)
            for i in range(1, 11)}
            for feat, feat_col in features.items()})
    precisions = {feat: {
        f'precision@{i}': len(target_scores.loc[target_scores[feat_col] <= i]) / len(scores.loc[scores[feat_col] <= i])
        for i in range(1, 11)}
        for feat, feat_col in features.items()}

    print(f"""Since the dataset is quite limited, also in terms of ambiguity for authors,
    we chose to perform an analysis with synthetic data: for every (real) author attribution 
    in the test set, we randomly sampled 9 other authors from the test set as artificial candidates 
    to perform a ranking with. 
    Note that we do not consider author names in the scoring procedure, only in the candidate selection step.

    There are {no_info} cases ({round(100 * no_info / len(target_scores_all))}%) \
    where no contextual information about the true author (earlier publications) was known. 
    In those cases, it is impossible for the tool to correctly rank those authors, 
    so we leave them out from the rest of the analysis. 
    Of course, the same holds for the artificial candidates, 
    so the actual (informed) ranked list consists of slightly over 8 candidates on average.

    In {round(100 * recalls['Overall']['recall@1'])}% of the cases, the correct author is the top candidate in the ranking. 
    In {round(100 * recalls['Overall']['recall@2'])}%, the correct author is amongst the top three. 

    The dataset is quite homogeneous: the variety year of publishing is limited. 
    This means that the authors are hard to distinguish based on this feature.
    The role, on the other hand, is as distinguishing a feature as anytime, 
    but is limited in general, because the majority of contributors are in fact Author.
    It turns out that genre is the best distinguishing feature in this case, 
    partly because the set contains both children's books and adult material. 
    """)

    return recalls, precisions

if __name__ == "__main__":
    mock=10
    test_items = obtain_test_items(mock=mock).sort_values(by=['publication_ppn','author_ppn'])
    similarity_data = obtain_similarity_data()
    publication_data = obtain_publication_data()
    scores = score_test_items(test_items, similarity_data, publication_data, filename='test_items_scored'+('_mock'+str(mock) if mock else ''))
    recalls, precisions = compute_performance(scores)
    #grouped_data = merge_and_group(test_items, similarity_data, publication_data)



