from flask import (
    Blueprint, flash, g, redirect, render_template, get_template_attribute, request, url_for, jsonify
)
from werkzeug.exceptions import abort


from demosaurus.db import get_db

import pandas as pd
from nltk.metrics import distance
import re
import numpy as np

bp = Blueprint('link_thesaurus', __name__)


@bp.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)


@bp.route('/thesaureer/')
def thesaureer():
    author_name = request.args.get('contributor_name', '', type=str)
    author_role = request.args.get('contributor_role', '', type=str)

    if not author_name: 
        author_options = pd.DataFrame()

    else:
        db = get_db()
        nameparts = author_name.split('@')
        
        author_options = pd.read_sql_query('''SELECT author_NTA.author_ppn, foaf_name, foaf_givenname, 
            foaf_familyname, skos_preflabel, birthyear, deathyear, 
            editorial_nl, editorial, skopenote_nl, related_entry_ppn,
            author_ISNI.identifier AS isni
            FROM author_NTA 
            LEFT JOIN author_ISNI ON author_NTA.author_ppn = author_ISNI.author_ppn 
            WHERE foaf_name LIKE \'%'''+nameparts[-1]+'%\'', con = db)
        print(author_options.dtypes)

        if len(author_options)>0:
            author_options=pd.concat((author_options, author_options.apply(lambda row: score_names(row, nameparts[0], nameparts[-1]), axis=1)), axis=1)
            author_options=pd.concat((author_options, author_options.apply(lambda row: score_genre(None,None), axis=1)), axis=1)
            author_options=pd.concat((author_options, author_options.apply(lambda row: score_style(None,None), axis=1)), axis=1)
            author_options=pd.concat((author_options, author_options.apply(lambda row: score_topic(None,None), axis=1)), axis=1)
            author_options=pd.concat((author_options, author_options.apply(lambda row: score_role(None,author_role), axis=1)), axis=1)


            features = ['name','genre','style','topic']

            scores = [feature+'_score' for feature in features]
            weights = [feature+'_confidence' for feature in features]

            author_options['score']= author_options.apply(lambda row: np.average(row.loc[scores], weights=row.loc[weights]), axis=1)


            author_options.sort_values(by='score', ascending=False, inplace=True)

    return author_options.to_json(orient = 'records')


def normalized_levenshtein(s1,s2):
    # normalized Levenshtein distance: normalize by the max of the lengths
    l = float(max(len(s1), len(s2))) # normalize by length, high score wins
    return  (l - distance.edit_distance(s1, s2)) / l         
    

def score_names(authorshipItem, given_name, family_name):
    familyNameScore =  normalized_levenshtein(authorshipItem['foaf_familyname'],family_name)   
    confidence = 1
    firstNameScore = 1
    try: 
        an,cn= [list(filter(None,re.split('\.|\s+', name))) for name in [authorshipItem['foaf_givenname'],given_name]]
        firstNameScore *= 1 if len(an)==len(cn) else .8
        confidence *= 0.8
    except: 
        #print ('Cant score firstname(s)')
        #print (contributorItem, contributorItem.dtype)
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

def score_genre(author_record, author_context):
    score=max(min(np.random.normal(0.7,0.1),1),0)
    confidence=max(min(np.random.normal(0.4, 0.1),0.9),0.1)
    return pd.Series([score, confidence], index = ['genre_score', 'genre_confidence'])

def score_style(author_record, author_context):
    score=max(min(np.random.normal(0.5,0.1),1),0)
    confidence=max(min(np.random.normal(0.4, 0.1),0.9),0.1)
    return pd.Series([score, confidence], index = ['style_score', 'style_confidence'])

def score_topic(author_record, author_context):
    score=max(min(np.random.normal(0.6, 0.1),1),0)
    confidence=max(min(np.random.normal(0.4, 0.1),0.9),0.1)
    return pd.Series([score, confidence], index = ['topic_score', 'topic_confidence'])

def score_role(author_record, author_context):
    if not author_context or not author_record :
        score = 0
        confidence = 0
    else:
        score=max(min(np.random.normal(0.7, 0.1),1),0)
        confidence=max(min(np.random.normal(0.4, 0.1),0.9),0.1)
    return pd.Series([score, confidence], index = ['role_score', 'role_confidence'])

