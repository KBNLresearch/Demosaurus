from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


from demosaurus.db import get_db

bp = Blueprint('publication', __name__)

@bp.context_processor
def utility_processor():
    def join_names(row):
        contributors = [row['contributor_{fn}_displayname'.format(fn=str(n))] for n in range(1,5)]
        contributors = [str(contributor) for contributor in contributors if contributor != None]
        return '; '.join(contributors)   	
        #return '; '.join([row['contributor_{fn}_displayname'].format(fn=str(n)) for n in range(1,4)])
    return dict(all_names=join_names)

@bp.route('/<id>/view')
def view(id):
    db = get_db()
    publication = db.execute(
        ' SELECT *'
        ' FROM onix'
        ' WHERE onix.isbn = ?',
        (id,)
    ).fetchone()

    #contributors = [publication['contributor_{fn}_displayname'.format(fn=str(n))] for n in range(1,5)]
    return render_template('publication/view.html', publication = publication, contributors=[0,1,1])


@bp.route('/')
def overview():
    db = get_db()
    publications = db.execute(
        'SELECT * '
        ' FROM onix'
    ).fetchall()
    return render_template('publication/overview.html', publications=publications)
