from importlib import reload
import scipy
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
import demosaurus
import os.path

import demosauruswebapp.demosaurus.link_thesaurus

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

def score_candidates(row):
    print(row.publication_ppn)
    author_name=str(row['name'])
    author_role = row.role
    publication_title = row.titelvermelding
    publication_genres={
        'CBK_genre':(str(row.CBK_genres).split(',') if row.CBK_genres else []),
        'brinkman':(str(row.Brinkman_vorm).split(',') if row.Brinkman_vorm else []) }
    publication_year= row.jaar_van_uitgave

    try:
        with app.app_context() as context:
            candidates = demosaurus.link_thesaurus.thesaureer_this(author_name,author_role, publication_title, publication_genres, publication_year)
    except:
        print('Failed to obtain candidates for', row)
        candidates = pd.DataFrame()
    nCandidates = len(candidates)
    rank_correct = -1
    score_correct = -1
    if nCandidates>0:
        candidates['rank'] = candidates['score'].rank(ascending=False)
        try:
            rank_correct = candidates.loc[candidates.author_ppn == row.author_ppn, 'rank'].iloc[0]
            score_correct = candidates.loc[candidates.author_ppn == row.author_ppn, 'score'].iloc[0]
        except:
            print('True author ('+str(row.author_ppn)+') not in candidate list for publication', row.publication_ppn)

    return pd.Series([rank_correct,nCandidates, score_correct], index=['rank_correct','nCandidates','score_correct'])


def obtain_candidates(test_items=None, outdir='NBD', overwrite = False):
    if test_items is None:
        test_items = obtain_test_items(outdir=outdir)
    names = test_items.name_normalized
    query = "SELECT * FROM "

    return

def obtain_test_items(outdir='NBD', overwrite = False, mock = True):
    t_name = 'test_items'+('_mock' if mock else '')
    if data_exists(t_name):
        test_items =  load_data(t_name,outdir=outdir)
    else:
        if mock:
            query = """SELECT t1.publication_ppn, t1.rank, t1.role,  t2.author_ppn AS candidate_author_ppn, t2.author_ppn = t1.author_ppn AS target
		FROM publication_contributors_test_NBD t1
		LEFT JOIN 
		(	
SELECT DISTINCT author_ppn FROM publication_contributors_train_NBD LIMIT 9) AS t2
UNION 
SELECT t1.publication_ppn, t1.rank, t1.role, t1.author_ppn AS candidate_author_ppn, t1.author_ppn = t1.author_ppn AS target
		FROM publication_contributors_test_NBD t1"""
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

def performance_old():
    TESTSET_FILE = '../data/performance/thesaureren_testset.csv'
    RESULTS_FILE = '../data/performance/performance_thesaureren_testset.csv'
    CHUNK_SIZE = 50

    try:
        testset = pd.read_csv(TESTSET_FILE, sep=';')
    except:
        with app.app_context() as context:
            with demosaurus.db.get_db() as db:
                testset = pd.read_sql_query(testset_query, con=db)
            testset.to_csv(TESTSET_FILE, sep=';', index=False)
    try:
        results = pd.read_csv(RESULTS_FILE, sep=';')
    except:
        results = pd.DataFrame({'publication_ppn': []})

    testset = testset.loc[
        ~testset.publication_ppn.isin(results.publication_ppn)]  # only evaluate items that haven't been evaluated yet

    for start_i in range(0, len(testset), CHUNK_SIZE):
        index_slice = [j for j in range(start_i, min(len(testset), start_i + CHUNK_SIZE))]
        result = testset.iloc[index_slice].apply(score_candidates, axis=1)
        result['publication_ppn'] = testset.publication_ppn.iloc[index_slice]
        results = results.append(result)
        results.to_csv(RESULTS_FILE, sep=';', index=False)


if __name__ == "__main__":

    similarity_data = obtain_similarity_data()
    test_items = obtain_test_items()
    #candidates = obtain_candidates(test_items)





