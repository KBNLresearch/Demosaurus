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
        ' SELECT *, '
        '        (SELECT identifier FROM VIAF WHERE ppn = ? LIMIT 1) AS VIAF,'
        '        (SELECT identifier FROM ISNI WHERE ppn = ? LIMIT 1) AS ISNI,'
        '        (SELECT identifier FROM Wikipedia '
        '                LEFT JOIN Wiki_languages ON Wikipedia.language = Wiki_languages.language'
        '                WHERE Wikipedia.ppn = ?'
        '                ORDER BY -Wiki_languages.rank desc LIMIT 1) AS WIKI'
        ' FROM contributor WHERE contributor.ppn = ?',
        (id,id,id,id)
    ).fetchone()  
    
    return render_template('contributor/authorpage.html', author=author, publications = [])


