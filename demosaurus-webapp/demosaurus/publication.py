from flask import (
    Blueprint, flash, g, redirect, render_template, get_template_attribute, request, url_for
)
from werkzeug.exceptions import abort


from demosaurus.db import get_db

bp = Blueprint('publication', __name__)


@bp.route('/<id>/view')
def view(id):
    db = get_db()
    publication = db.execute(
        ' SELECT *'
        ' FROM onix'
        ' WHERE onix.isbn = ?',
        (id,)
    ).fetchone()
    contributors = db.execute(
        ' SELECT *'
        ' FROM authorship'
        ' JOIN author_roles'
        ' ON authorship.role = author_roles.author_rolesID'
        ' WHERE authorship.publication_isbn = ?',
        (id,)
    ).fetchall()

    print(len(contributors),  'contributor records')
    print(contributors[0].keys())  

    return render_template('publication/view.html', publication = publication, contributors=contributors)




@bp.route('/')
def overview():
    db = get_db()
    publications = db.execute(
        'SELECT * '
        ' FROM onix'
        ' JOIN authorship'
        ' ON onix.isbn = authorship.publication_isbn'
        ' WHERE authorship.seq_nr = 1'
        ' AND authorship.source = \'Onix\''
    ).fetchall()
    return render_template('publication/overview.html', publications=publications)


