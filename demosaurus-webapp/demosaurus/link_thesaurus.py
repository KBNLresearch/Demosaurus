from flask import (
    Blueprint, flash, g, redirect, render_template, get_template_attribute, request, url_for
)
from werkzeug.exceptions import abort


from demosaurus.db import get_db

import nltk

bp = Blueprint('link_thesaurus', __name__)

@bp.route('/thesaureer/', defaults={'authorshipID': None})
@bp.route('/<authorshipID>/thesaureer/')



def thesaureer(authorshipID):
    if not authorshipID: return render_template('base.html')

    db = get_db()
    thisAuthor = db.execute(
        ' SELECT *'
        ' FROM authorship'
        ' WHERE authorship.authorshipID =?',
        (authorshipID,)).fetchone()

    author_name = thisAuthor['familyName']

    author_options = db.execute(
        ' SELECT *'
        ' FROM contributor'
        ' WHERE contributor.foaf_name LIKE ?',
        ('%'+author_name+'%',) #mogelijk gevoelig voor opzoeken hoe wild cards in queries (escapen?)
        ).fetchall()

    return render_template('link_thesaurus/authorlist.html', author_name = author_name, author_options=author_options)
   
    
    
#    thesaureer =  get_template_attribute('publication/partials/thesaurus-block', 'thesaureer')
#   return thesaureer('Corstius')
