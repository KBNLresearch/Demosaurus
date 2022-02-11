from flask import (
    Blueprint, flash, g, redirect, render_template, get_template_attribute, request, url_for, jsonify
)
from demosauruswebapp.demosaurus.db import get_db
import pandas as pd
from nltk.metrics import distance as nl_distance
import re
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
        wrapped_publication, features_to_obtain = wrap_publication_info(request_args=request.args)
        candidates = obtain_and_score_candidates(author_name, wrapped_publication, features_to_obtain)
    return jsonify(json.loads(candidates.to_json(orient='records')))

def wrap_publication_info(request_args):
    features_to_obtain = { # scores that will be reported on in the end, plus which columns to use to compute them
        'nominal': {'role':['role']},
        'ordinal': {'year':['jaar_van_uitgave']},
        'textual': {}}
    publication_genres = json.loads(request_args.get('publication_genres', '', type=str))
    features_to_obtain['nominal']['genre'] = [genre for genre, identifiers in publication_genres.items() if len(identifiers)>0]

    publication_features = {'jaar_van_uitgave': [request_args.get('publication_year', '', type=str)],
                           'role': [request_args.get('contributor_role', '', type=str)], # might be more than one..
                           #'title':[request_args.get('publication_title', '', type=str)] # not used atm
                           }
    publication_features.update({kind:[item['identifier'] for item in itemlist] for kind, itemlist in publication_genres.items()})

    def cast_type(feature_value, feature_name):
        if feature_name in ['NUGI_genre','NUR_rubriek','jaar_van_uitgave']:
            return int(feature_value.strip())
        else:
            return feature_value.strip()

    wrapped_publication = pd.DataFrame(
        [pd.Series({feature: cast_type(value, feature), 'this_publication': 1}) for feature, value_list in publication_features.items() for
         value in value_list])

    return wrapped_publication, features_to_obtain

def mask(a):
    return np.ma.MaskedArray(a, mask=np.isnan(a))

def obtain_and_score_candidates(author_name, wrapped_publication, features_to_obtain):
    candidates, similarity_data = obtain_candidates(author_name,
        features=[f # flattened list for obtaining: interact with database just once
                for f_kind, f_dict in features_to_obtain.items()
                for f_name, f_list in f_dict.items()
                for f in f_list])
    if len(candidates) == 0:
        return candidates
    else:
        scores = score_candidates(similarity_data,wrapped_publication,features_to_obtain)
        candidates  = candidates.merge(scores,  left_on='author_ppn',  right_index=True)
    return candidates.sort_values(ascending=False, by=['score','support'])



def score_candidates(similarity_data, wrapped_publication, features_to_obtain):
    all_scores = pd.DataFrame(index=similarity_data.author_ppn.unique())
    for f_kind, f_dict in features_to_obtain.items():
        if len(f_dict) == 0:
            continue
        for feature_name, feature_list in f_dict.items():
            partial_scores = {}
            for feature in feature_list:
                feature_data = \
                    similarity_data[['author_ppn', feature, 'knownPublications']] \
                        .dropna(subset=[feature]) \
                        .merge(
                        wrapped_publication[[feature, 'this_publication']] \
                            .dropna(subset=[feature]),
                        how='outer').fillna(0)
                partial_scores[feature + '_score'], partial_scores[feature + '_confidence'] = score_functions[f_kind](
                    feature_data,feature)

            # combine partial scores into one single score for presentation
            score_items = [feature + '_score' for feature in feature_list]
            weight_items = [feature + '_confidence' for feature in feature_list]

            score_confidence = pd.DataFrame(partial_scores).apply(
                lambda row: np.average(row.loc[score_items], weights=row.loc[weight_items], returned=True) if np.sum(row.loc[weight_items])>0 else (0,0), result_type='expand', axis=1)
            # insert combined scores into candidates dataframe
            all_scores = all_scores.merge(score_confidence,left_index=True, right_index=True).rename(
                {0:feature_name+'_score', 1:feature_name + '_confidence'}, axis = 1)
    # combine scores per feature group into a single overall score for ordering candidates
    feature_list = ['genre','year']
    score_items = [feature + '_score' for feature in feature_list]
    weight_items = [feature + '_confidence' for feature in feature_list]
    all_scores['score'] = all_scores.apply(
        lambda row: np.average(row.loc[score_items], weights=row.loc[weight_items]), axis=1)
    all_scores['support'] = all_scores.apply(
        lambda row: np.sum(row.loc[weight_items]), axis=1)
    return all_scores


def score_nominal(feature_data, feature_column):
    """
        Determine score (0-1) and confidence (0-1) for an author given the publication and their known publications
        grouped:   a pandas DataFrameGroupBy with every group corresponding to an author with columns:
                    rows correspond to feature occurrences, e.g. a specific subject term
                    columns:
                    - knownPublications (int): how many publications by that author are known to have the feature occurrence
                    - this_publication (int 1/0): whether the publication under review has that feature occurrence
        """
    grouped = feature_data.groupby('author_ppn')
    score = grouped.apply(lambda author:
                1 - spatial_distance.cosine(author.knownPublications,
                                            author.this_publication))
    known = grouped['knownPublications'].sum()
    confidence = known / (known + 20)
        # need approx. 20 datapoints to make a somewhat reliable estimate (50% sure)
        # Temporary fix to get some estimate on reliability
    return score, confidence

def score_ordinal(feature_data,feature_column):
    this_value = feature_data.loc[lambda x: x.this_publication==1, feature_column].iloc[0]
    grouped = feature_data.groupby('author_ppn')
    # fit a normal distribution (described by my,sigma) for every author
    mu_sigma = grouped.apply(lambda author:
                             stats.norm.fit(np.repeat(author[feature_column], author.knownPublications)))
    # sigma should be at least 5: publications are still likely (70%) 5 years from any known publication
    # normalize by top of the distribution: we want a score of 1 for the mean
    score = mu_sigma.apply(lambda row: stats.norm.pdf(this_value, max(5,row[0]), row[1])/stats.norm.pdf(row[0], row[0], row[1]))
    known = grouped['knownPublications'].sum()
    confidence = known / (known + 20)
    return score, confidence

score_functions = {'nominal':  score_nominal, 'ordinal': score_ordinal}

def candidates_with_features_query(candidates_query):
    return "WITH candidates AS (" + candidates_query + """)
            SELECT author_NTA.*, t4.identifier AS isni FROM candidates 
            JOIN author_NTA ON candidates.author_ppn = author_NTA.author_ppn
            LEFT JOIN author_isni t4 ON candidates.author_ppn = t4.author_ppn 
            GROUP BY author_NTA.author_ppn;"""

def similarity_features_query(features, candidates_query):
    query = "WITH candidates AS (" + candidates_query + ")\n"
    for i, feature_i in enumerate(features):
        if i > 0: query += ' UNION '
        query += 'SELECT candidates.author_ppn, '
        for j, feature_j in enumerate(features):
            query += '{value} AS {feature},'.format(value= 'term_identifier' if i==j else 'NULL', feature=feature_j)
        query += 'nPublications as knownPublications '
        query += 'FROM candidates JOIN author_{feature}_NBD t{i} ON candidates.author_ppn = t{i}.author_ppn'.format(feature=feature_i, i=i)
    return query

def candidate_query(author_name, train_only=True):
    # TODO: implement extended search (with specifications) - only last name, spelling variations, etc.
    q = "SELECT DISTINCT t1.author_ppn FROM author_fts5 t1"
    if train_only:
        q += " JOIN publication_contributors_train_NBD t2 ON t2.author_ppn = t1.author_ppn "
    q += " WHERE name_normalized MATCH :searchkey"
    params = {'searchkey': '\"' + normalize_name(author_name)+ '\"'}
    return q, params

def obtain_candidates(author_name, features):
    candidates_query, params = candidate_query(author_name)
    q1 = candidates_with_features_query(candidates_query=candidates_query)
    q2 = similarity_features_query(features=features, candidates_query=candidates_query)
    start = time.time()
    candidates = pd.read_sql_query(q1, params=params, con=get_db())
    similarity_data = pd.read_sql_query(q2, params=params, con=get_db())
    print('Obtain candidates - time elapsed:', time.time() - start)
    return candidates, similarity_data

def score_names(authorshipItem, author_name):
    return pd.Series([0, 0], index=['name_score', 'name_confidence'])

    def normalized_levenshtein(s1, s2):
        # normalized Levenshtein distance: normalize by the max of the lengths
        l = float(max(len(s1), len(s2)))  # normalize by length, high score wins
        return (l - nl_distance.edit_distance(s1, s2)) / l

    def obtain_name_options(author_ppn):
        query = "SELECT * FROM author_name_options WHERE author_ppn = :author_ppn"
        return pd.read_sql_query(query, params={'author_ppn': author_ppn}, con=get_db())

    name_options = obtain_name_options(authorshipItem.author_ppn)
    name_options['fullnamescore'] = name_options['name'].apply(
        lambda x: normalized_levenshtein(x, author_name.replace('@', '')))
    if max(name_options['fullnamescore']) == 1:
        name_score = 1
        confidence = 1
    else:
        normalized_name = normalize_name(author_name.replace('@', ''))
        confidence = normalized_name(normalized_name, author_name.replace('@', ''))
        name_options['normalizedscore'] = name_options['name_normalized'].apply(
            lambda x: normalized_levenshtein(x, normalized_name))
        name_score = max(name_options['normalizedscore'])
        if max(name_options['normalizedscore']) == 1:
            name_score = .95
            confidence = 1
        else:
            True

    # family name should be rather similar: check levenshtein distance and normalize by length
    if '@' in author_name:
        nameparts = author_name.split('@')
    else:
        nameparts = author_name.split()
    family_name = nameparts[-1]
    given_name = ' '.join(nameparts[:-1])

    familyNameScore = normalized_levenshtein(authorshipItem['foaf_familyname'], family_name)

    confidence = 1
    firstNameScore = 1
    try:  # convert given name(s) to list
        # an for author name, cn for candidate name
        an, cn = [list(filter(None, re.split('\.|\s+', name))) for name in
                  [authorshipItem['foaf_givenname'], given_name]]
        firstNameScore *= 1 if len(an) == len(cn) else .8  # if number of given names differs, lower score
    except:  # no reliable first name(s)
        an, cn = [[], []]
        firstNameScore = .5
        confidence *= 0.5

    for i in range(min(len(an), len(cn))):
        if len(an[i]) == 1 or len(
                cn[i]) == 1:  # Just initials: compare first letter only
            firstNameScore *= 1 if an[i][0] == cn[i][0] else .5
            confidence *= 0.8  # Gives less reliable score: confidence penalty
        else:
            firstNameScore *= normalized_levenshtein(an[i], cn[i])
    return pd.Series([.5 * familyNameScore + .5 * firstNameScore, confidence], index=['name_score', 'name_confidence'])