from flask import (
    Blueprint, flash, g, redirect, render_template, get_template_attribute, request, url_for, jsonify
)
from demosauruswebapp.db import get_db
import pandas as pd
import numpy as np
from scipy.spatial import distance as spatial_distance
from scipy import stats
import json
import time
import unidecode
import string

bp = Blueprint('link_thesaurus', __name__)

punctuation_remover = str.maketrans(string.punctuation, ' '*len(string.punctuation)) #map punctuation to space
def normalize_name(name):
    name = name.split('(')[0]  # get only first bit (no life years, comments etc.)
    name = unidecode.unidecode(name)  # unicode normalization
    name = name.lower()  # lowercase
    name = name.translate(punctuation_remover)  # replace dots, apostrophes, etc. with whitespace
    name = ' '.join(name.split())  # single space separation
    return name

class NoCandidatesFoundException(Exception):
    pass

@bp.route('/thesaureer/')
def thesaureer():
    author_name = request.args.get('contributor_name', '', type=str)
    if not author_name:
        candidates = pd.DataFrame()  # Without name, cannot select candidates
    else:
        wrapped_publication = wrap_publication_info(request_args=request.args)
        candidates = obtain_and_score_candidates(author_name, wrapped_publication)
    return jsonify(json.loads(candidates.to_json(orient='records')))

def wrap_publication_info(request_args):
    publication_genres = json.loads(request_args.get('publication_genres', '', type=str))
    f_list = [(kind, item['identifier']) for kind, itemlist in publication_genres.items() for item in itemlist]
    f_list.append(('role',request_args.get('contributor_role', '', type=str)))
    try:
        f_list.append(('jaar_van_uitgave', request_args.get('publication_year', type=int)))
    except ValueError: # year is an empty string or otherwise not convertible to int
        pass # omit it in the list
    wrapped_publication = pd.DataFrame.from_records(f_list, columns=['term_description', 'term'])
    wrapped_publication['this_publication'] = 1
    return wrapped_publication

def mask(a):
    return np.ma.MaskedArray(a, mask=np.isnan(a))


FEATURE_KINDS = {}
FEATURE_KINDS.update({x:'nominal' for x in ['CBK_genre','NUGI_genre','NUR_rubriek',
                                         'brinkman_vorm','brinkman_zaak', 'role']})
FEATURE_KINDS.update({x:'ordinal' for x in ['jaar_van_uitgave']})

FEATURE_GROUPS = {}
FEATURE_GROUPS.update({x:'genre' for x in ['CBK_genre','NUGI_genre','NUR_rubriek',
                                         'brinkman_vorm']})
FEATURE_GROUPS.update({x:'subject' for x in ['brinkman_zaak']})
FEATURE_GROUPS.update({x:'role' for x in ['role']})
FEATURE_GROUPS.update({x:'year' for x in ['jaar_van_uitgave']})

def score_feature(group):
    """
    Returns a tuple (score,confidence) holding score and confidence for a given feature.

    Arguments:
    group -- a Pandas GroupBy element that corresponds to an author
             and a specific feature (e.g. Brinkman_vorm) and has columns
             'term' with the feature value (e.g. '075629402')
             'knownPublications' the number of known publications with that feature value
             'this_publication' whether this publication has this feature value (0/1)
    """
    feature_name = group.term_description.iloc[0]
    known = group.knownPublications.sum()
    if known == 0 or group.this_publication.sum() == 0:
        score = 0
        confidence = 0
    else:
        if FEATURE_KINDS[feature_name] == 'nominal':
            score = 1 - spatial_distance.cosine(group.knownPublications,
                                                group.this_publication)
        elif FEATURE_KINDS[feature_name] == 'ordinal':
            years = pd.to_numeric(group.term)
            this_value = years.loc[group.this_publication == 1].iloc[0]
            mu, sigma = stats.norm.fit(
                np.repeat(years, group.knownPublications))  # normal distrubtion fitted for author
            sigma = max(5,
                        sigma)  # sigma should be at least 5: publications are still likely (70%) 5 years from any known publication
            top = stats.norm.pdf(mu, mu,
                                 sigma)  # normalize by top of the distribution: we want a score of 1 for the mean
            score = stats.norm.pdf(this_value, mu, sigma) / top
        else:
            score = -1
        confidence = known / (known + 20)
        # need approx. 20 datapoints to make a somewhat reliable estimate (50% sure)
        # Temporary fix to get some estimate on reliability
    return pd.Series({'score': score, 'confidence': confidence, 'term_category': FEATURE_GROUPS[feature_name]})

def obtain_and_score_candidates(author_name, wrapped_publication):
    candidates, similarity_data = obtain_candidates(author_name)
    if len(candidates) == 0 or len(similarity_data) == 0:
        return candidates
    else:
        scores = score_candidates(similarity_data,wrapped_publication)
        candidates  = candidates.merge(scores,  left_on='author_ppn', right_index=True, how='left') # how='left' for all NTA entries (not just those with scores)
    return candidates.sort_values(ascending=False, by=['score','support'])


def score_candidates(similarity_data, wrapped_publication):
    scores = similarity_data.groupby('author_ppn') \
        .apply(lambda author: \
            pd.merge(wrapped_publication, author, how='outer') \
                .fillna(0).groupby(['term_description'])\
                .apply(score_feature) \
                .groupby(['term_category'])
                    .apply(lambda x:
                        pd.Series([np.average(x.score, weights=x.confidence),
                                   x.confidence.mean()],
                                index=['score', 'confidence']))
               ).unstack() # last groupby (term_categories) to column-index
    scores.columns = [i[1] + '_' + i[0] for i in scores.columns.to_flat_index()] #flatten column index

    feature_list = ['genre','year', 'role']
    score_items = [feature + '_score' for feature in feature_list]
    weight_items = [feature + '_confidence' for feature in feature_list]
    # compute overall score
    scores['score'] = scores.apply(
        lambda row: np.average(row.loc[score_items], weights=row.loc[weight_items]), axis=1)
    scores['support'] = scores.apply(
        lambda row: np.mean(row.loc[weight_items]), axis=1)
    return scores


def candidates_with_features_query(candidates_query):
    return "WITH candidates AS (" + candidates_query + """)
            SELECT author_NTA.*, t4.identifier AS isni FROM candidates 
            JOIN author_NTA ON candidates.author_ppn = author_NTA.author_ppn
            LEFT JOIN author_isni t4 ON candidates.author_ppn = t4.author_ppn 
            GROUP BY author_NTA.author_ppn;"""

def aggregated_data_query(candidates_query):
    query = f"WITH candidates AS ({candidates_query})\n"
    query += "SELECT t1.* FROM author_aggregated t1 JOIN candidates ON t1.author_ppn = candidates.author_ppn\n"
    return query

def candidate_query(author_name, train_only=False):
    # TODO: implement extended search (with specifications) - only last name, spelling variations, etc.
    q = "SELECT DISTINCT t1.author_ppn FROM author_fts5 t1"
    if train_only:
        q += " JOIN publication_contributors_train_NBD t2 ON t2.author_ppn = t1.author_ppn "
    q += " WHERE t1.name_normalized MATCH :searchkey"
    params = {'searchkey': '\"' + normalize_name(author_name)+ '\"'}
    return q, params

def obtain_candidates(author_name):
    candidates_query, params = candidate_query(author_name)
    q1 = candidates_with_features_query(candidates_query=candidates_query)
    q2 = aggregated_data_query(candidates_query=candidates_query)
    start = time.time()
    candidates = pd.read_sql_query(q1, params=params, con=get_db())
    similarity_data = pd.read_sql_query(q2, params=params, con=get_db())
    print('Obtain candidates - time elapsed:', time.time() - start)
    return candidates, similarity_data
