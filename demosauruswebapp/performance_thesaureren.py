from importlib import reload
import scipy
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
import demosaurus

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

if __name__ == "__main__":
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

    TESTSET_FILE = '../data/performance/thesaureren_testset.csv'
    RESULTS_FILE = '../data/performance/performance_thesaureren_testset.csv'
    CHUNK_SIZE = 50

    try:
        testset = pd.read_csv(TESTSET_FILE, sep=';')
    except:
        with app.app_context() as context:
            with demosaurus.db.get_db() as db:
                testset = pd.read_sql_query(testset_query, con = db)
            testset.to_csv(TESTSET_FILE, sep=';', index=False)
    try:
        results = pd.read_csv(RESULTS_FILE, sep=';')
    except:
        results = pd.DataFrame({'publication_ppn':[]})

    testset = testset.loc[
        ~testset.publication_ppn.isin(results.publication_ppn)]  # only evaluate items that haven't been evaluated yet


    for start_i in range(0, len(testset), CHUNK_SIZE):
        index_slice = [j for j in range(start_i, min(len(testset), start_i + CHUNK_SIZE))]
        result = testset.iloc[index_slice].apply(score_candidates, axis=1)
        result['publication_ppn'] = testset.publication_ppn.iloc[index_slice]
        results = results.append(result)
        results.to_csv(RESULTS_FILE, sep=';', index=False)
