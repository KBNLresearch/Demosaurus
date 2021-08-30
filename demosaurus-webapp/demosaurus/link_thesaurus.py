from flask import (
    Blueprint, flash, g, redirect, render_template, get_template_attribute, request, url_for, jsonify
)
from demosaurus.db import get_db
import pandas as pd
from nltk.metrics import distance as nl_distance
import re
import numpy as np
from scipy.spatial import distance as spatial_distance
from scipy import stats
import json
import time

bp = Blueprint('link_thesaurus', __name__)

@bp.route('/thesaureer/')
def thesaureer():
    author_name = request.args.get('contributor_name', '', type=str)
    author_role = request.args.get('contributor_role', '', type=str)
    publiction_title = request.args.get('publication_title', '', type=str)
    publication_genres = json.loads(request.args.get('publication_genres', '', type=str))
    publication_year = {'jaar_van_uitgave': [request.args.get('publication_year', '', type=str)]}

    if not author_name:
        author_options = pd.DataFrame() # Without name, cannot select candidates
    else:
        db = get_db()
        nameparts = author_name.split('@')
        familyname = nameparts[-1]
        firstname = '' if len(nameparts)<2 else nameparts[0]
        if len(nameparts)>2: print('More than two nameparts for', author_name, )

        start = time.time()
        author_options = pd.read_sql_query("""
        WITH candidates AS (SELECT author_ppn FROM author_fts5 WHERE foaf_name MATCH :name)
        SELECT author_NTA.* FROM candidates JOIN author_NTA ON candidates.author_ppn = author_NTA.author_ppn;
        """, params={'name':'\"'+familyname+'\"'}, con = db)
        end = time.time()
        print('Obtain candidates - time elapsed:', end-start)

        # Add scores to the candidates
        if len(author_options)>0:
            author_options=pd.concat((author_options, author_options.apply(
                lambda row: score_names(row, firstname, familyname), axis=1)), axis=1)
            author_options=pd.concat((author_options, author_options.apply(
                lambda row: score_class_based(row['author_ppn'], publication_genres, 'genre'), axis=1)), axis=1)
            #author_options = pd.concat((author_options, author_options.apply(
#                lambda row: score_class_based(row['author_ppn'], publication_year, 'jvu'), axis=1)), axis=1)
            author_options=pd.concat((author_options, author_options.apply(
                lambda row: score_year(row['author_ppn'], publication_year), axis=1)), axis=1)
            author_options = pd.concat((author_options, author_options.apply(
                lambda row: score_style(None, None), axis=1)), axis=1)
            author_options=pd.concat((author_options, author_options.apply(
                lambda row: score_role(None,author_role), axis=1)), axis=1)

            # Determine overall score for candidate: linear combination of scores, weighted by confidence
            features = ['name','genre', 'jvu']
            scores = [feature+'_score' for feature in features]
            weights = [feature+'_confidence' for feature in features]
            author_options['score']= author_options.apply(lambda row: np.average(row.loc[scores], weights=row.loc[weights]), axis=1)

            # Sort candidates by score
            author_options.sort_values(by='score', ascending=False, inplace=True)

    return author_options.to_json(orient = 'records')


def normalized_levenshtein(s1,s2):
    # normalized Levenshtein distance: normalize by the max of the lengths
    l = float(max(len(s1), len(s2))) # normalize by length, high score wins
    return  (l - nl_distance.edit_distance(s1, s2)) / l         
    

def score_names(authorshipItem, given_name, family_name):
    # family name should be rather similar: check levenshtein distance and normalize by length
    familyNameScore =  normalized_levenshtein(authorshipItem['foaf_familyname'],family_name)

    confidence = 1
    firstNameScore = 1
    try: # convert given name(s) to list
        # an for author name, cn for candidate name
        an,cn= [list(filter(None,re.split('\.|\s+', name))) for name in [authorshipItem['foaf_givenname'],given_name]]
        firstNameScore *= 1 if len(an)==len(cn) else .8 # if number of given names differs, lower score
    except: # no reliable first name(s)
        an, cn = [[],[]]
        firstNameScore=.5
        confidence *= 0.5
    
    for i in range(min(len(an),len(cn))):
        if len(an[i])==1 or len(cn[i])==1: # Just initials: compare first letter only                                        
            firstNameScore *= 1 if an[i][0] == cn[i][0] else .5
            confidence *= 0.8 # Gives less reliable score: confidence penalty 
        else:
            firstNameScore *= normalized_levenshtein(an[i],cn[i])
    return pd.Series([.5*familyNameScore+.5*firstNameScore, confidence], index = ['name_score', 'name_confidence'])


def obtain_similarity_data(author_ppn, features):
    # obtain accumulated data for author
    # from author views (see repo/data-processing/author_views.py)
    #try:
    query = ''
    for i, feature_i in enumerate(features):
        if i > 0: query += ' UNION '
        query += 'SELECT '
        for j, feature_j in enumerate(features):
            if i == j:
                query += feature_j + ','
            else:
                query += 'NULL AS ' + feature_j + ','
        query += 'nPublications as knownPublications '
        query += 'FROM ' + 'author_' + feature_i + 's '
        query += 'WHERE author_ppn = :author_ppn'
    data = pd.read_sql_query(query, params={'author_ppn':author_ppn}, con = get_db())       
    #except e:
    #    print('PROBLEM', e) 
    #TODO: proper exception handling (return exception to caller!)
    return data

def score_class_based(author_ppn, publication_classes, name):
    """
    Determine score (0-1) and confidence (0-1) for an author given the publication and their known publications
    Based on information in fields corresponding to items in publication_classes (e.g. genres, subjects, ...)
    author_ppn: the pica identifier of the candidate author (string)
    publication_classes: the information of the publication to be compared to
                         a dictionary of lists: 
                            keys are class names that correspond to database information (e.g. "CBK_genre")
                            values are a list of identifiers that correspond to publication (e.g. ["330", "135", "322", "334"])
    name: a string that indicates how to interpret the score (e.g. "genre")
    """
    if sum([len(v) for k,v in publication_classes.items()]) == 0:
        # Nothing to base score on. Return zero or something else?
        score = 0
        confidence = 0 
    else: 
        # Obtain a list of known publication counts from the database
        known_info = obtain_similarity_data(author_ppn, publication_classes.keys())
        if len(known_info) == 0:
            # no information available to make a sane comparison
            score = 0
            confidence = 0
        else: 
            # Add a column with the new publication to compare with
            for c,l in publication_classes.items():
                for v in l:
                    if type(v)== dict:
                        try: known_info.loc[known_info[c]==v['identifier'],'newPublication']=1
                        except: print('Cannot add publication info to dataframe for comparison')
                    else:
                        try: known_info.loc[known_info[c]==v,'newPublication']=1
                        except: print('Cannot add publication info to dataframe for comparison')
            # score = 1- cosine distance between array of known publications and new publication
            # intuition:
            # if there are no overlapping genres, distance = 1 so score is 0
            # if there is little overlap, the score is close to 0
            # if the new publication is very similar to known publications, the score is close to 1       
            known_info = known_info.fillna(0)

            try:
                score = 1 - spatial_distance.cosine(known_info.knownPublications, known_info.newPublication)
                assert not np.isnan(score)
                known = known_info.knownPublications.sum()
                confidence= known/(known+20) # need approx. 20 datapoints to make a somewhat reliable estimate (50% sure)
                # Temporary fix to get some estimate on reliability
            except:
                #print('class based score is undefined for', author_ppn, publication_classes)
                score = 0
                confidence = 0

    return pd.Series([score, confidence], index = [name+'_score', name+'_confidence'])
    
def score_style(author_record, author_context):
    #score=max(min(np.random.normal(0.5,0.1),1),0)
    #confidence=max(min(np.random.normal(0.4, 0.1),0.9),0.1)
    score = 0
    confidence = 0 
    return pd.Series([score, confidence], index = ['style_score', 'style_confidence'])


def score_role(author_record, author_context):
    if not author_context or not author_record :
        score = 0
        confidence = 0
    else:
        score = 0
        confidence = 0 
        # score=max(min(np.random.normal(0.7, 0.1),1),0)
        # confidence=max(min(np.random.normal(0.4, 0.1),0.9),0.1)
    return pd.Series([score, confidence], index = ['role_score', 'role_confidence'])

def score_year(author_ppn, publication_year):

    try:
        year = int (publication_year['jaar_van_uitgave'][0])
        known_info = obtain_similarity_data(author_ppn, publication_year)
    except:
        known_info = pd.DataFrame([])

    if len(known_info) == 0:
        # no information available to make a sane comparison
        score = 0
        confidence = 0
    else:
        # fit a normal distribution to the data points
        mu, sigma = stats.norm.fit(np.repeat(known_info.jaar_van_uitgave, known_info.knownPublications))
        sigma = max(sigma, 5) # sigma should be at least 5: publications are still likely (70%) 5 years from any known publication
        top = stats.norm.pdf(mu, mu, sigma) # determine top
        score = stats.norm.pdf(year, mu, sigma)/top # normalize by top: we want a score of 1 for the mean
        # estimate confidence:
        known = known_info.knownPublications.sum()
        confidence= known/(known+20) # need approx. 20 datapoints to make a somewhat reliable estimate (50% sure)

    return pd.Series([score, confidence], index=['jvu_score', 'jvu_confidence'])

