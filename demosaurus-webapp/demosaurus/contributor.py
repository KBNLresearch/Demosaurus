from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

import pandas as pd
import numpy as np

from demosaurus.db import get_db

bp = Blueprint('contributor', __name__)


@bp.route('/<id>/authorpage')
def authorpage(id):
    title = request.args.get('Title', '', type=str)
    role = request.args.get('Role', '', type=str)

    db = get_db()
    author = db.execute(
        ' SELECT *, '
        '        (SELECT identifier FROM author_VIAF WHERE author_ppn = ? LIMIT 1) AS VIAF,'
        '        (SELECT identifier FROM author_ISNI WHERE author_ppn = ? LIMIT 1) AS ISNI,'
        '        (SELECT wiki_url FROM author_Wikipedia '
        '                LEFT JOIN wiki_preferred_languages ON author_Wikipedia.language = wiki_preferred_languages.language'
        '                WHERE author_Wikipedia.author_ppn = ?'
        '                ORDER BY -wiki_preferred_languages.rank desc LIMIT 1) AS WIKI'
        ' FROM author_NTA WHERE author_NTA.author_ppn = ?',
        (id,id,id,id)
    ).fetchone()  

    # Fetch all publications that this author has contributed to
    publications = pd.read_sql_query('SELECT publication_basicinfo.publication_ppn, role, kmc, titelvermelding, verantwoordelijkheidsvermelding,' 
    ' \"taal_publicatie\", \"taal_origineel\", \"land_van_uitgave\", isbn, isbn_2, \"jaar_van_uitgave\", \"uitgever\", uitgever_2,'
    ' authorship_ggc.author_ppn    '
    ' FROM authorship_ggc LEFT JOIN publication_basicinfo'
    ' ON authorship_ggc.publication_ppn = publication_basicinfo.publication_ppn'
    ' WHERE authorship_ggc.author_ppn =? ', params = [id], con = db)

    publications = publications.loc[publications.titelvermelding != title]

    if len(publications)>0:
        publications = add_scores(publications, role)
        print(publications.dtypes, len(publications))

    return render_template('contributor/authorpage.html', author=author, title= title, publications =publications.to_json(orient='records', force_ascii=False))

def add_scores(publications, role):
    publications=pd.concat((publications, publications.apply(lambda row: score_genre(None,None), axis=1)), axis=1, sort = False)
    publications=pd.concat((publications, publications.apply(lambda row: score_style(None,None), axis=1)), axis=1, sort = False)
    publications=pd.concat((publications, publications.apply(lambda row: score_subject(None,None), axis=1)), axis=1, sort = False)
    publications=pd.concat((publications, publications.apply(lambda row: score_role(row.role,role), axis=1)), axis=1, sort = False)

    features = ['role','genre','style','subject']
    scores = [feature+'_score' for feature in features]
    weights = [feature+'_confidence' for feature in features]
    publications['score']= publications.apply(lambda row: np.average(row.loc[scores], weights=row.loc[weights]), axis=1)
    publications.sort_values(by='score', ascending=False, inplace=True)
    return publications

def score_genre(publication, reference_publication):
    score=max(min(np.random.normal(0.7,0.1),1),0)
    confidence=max(min(np.random.normal(0.4, 0.1),0.9),0.1)
    return pd.Series([score, confidence], index = ['genre_score', 'genre_confidence'])

def score_style(publication, reference_publication):
    score=max(min(np.random.normal(0.5,0.1),1),0)
    confidence=max(min(np.random.normal(0.4, 0.1),0.9),0.1)
    return pd.Series([score, confidence], index = ['style_score', 'style_confidence'])

def score_subject(publication, reference_publication):
    score=max(min(np.random.normal(0.6, 0.1),1),0)
    confidence=max(min(np.random.normal(0.4, 0.1),0.9),0.1)
    return pd.Series([score, confidence], index = ['subject_score', 'subject_confidence'])

def score_role(publication, reference_publication):
    print('score_role', publication, reference_publication)
    if not reference_publication or not publication :
        score = 0
        confidence = 0
    else: 
        score=int(publication == reference_publication)
        confidence=1
    return pd.Series([score, confidence], index = ['role_score', 'role_confidence'])