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

    return render_template('contributor/authorpage.html', author=author, title= title, role = role, publications =publications.to_json(orient='records', force_ascii=False))

