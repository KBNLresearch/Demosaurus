from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


from demosaurus.db import get_db

bp = Blueprint('contributor', __name__)


@bp.route('/<id>/authorpage')
def authorpage(id):
    db = get_db()
    author = db.execute(
        ' SELECT *'
        ' FROM contributor'
        ' WHERE contributor.ppn = ?',
        (id,)
    ).fetchone()

    # publications = db.execute(
    #      ' SELECT *'
    #      ' FROM publication'
    #      ' JOIN authorship'
    #      ' ON authorship.publication_isbn == publication.isbn'
    #      ' WHERE authorship.contributor_ppn = ?',
    #      (id,)
    #  ).fetchall() 
    
    return render_template('contributor/authorpage.html', author=author, publications = [])


