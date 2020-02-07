from flask import (
    Blueprint, flash, g, redirect, render_template, get_template_attribute, request, url_for
)
from werkzeug.exceptions import abort


from demosaurus.db import get_db

import pandas as pd
from nltk.metrics import distance
import re

bp = Blueprint('link_thesaurus', __name__)

@bp.route('/thesaureer_alt/', defaults={'author_name': 'Pietje @Puk'})
@bp.route('/<author_name>/thesaureer_alt/')
def thesaureer_alt(author_name):
    db = get_db()
    nameparts = author_name.split('@')
    
    author_options = pd.read_sql_query('SELECT * FROM contributor WHERE contributor.foaf_name LIKE \'%'+nameparts[-1]+'%\'', con = db)
    author_options['name_score']=author_options.apply(lambda row: score_names(row, nameparts[0], nameparts[-1]), axis=1)
    author_options.sort_values(by='name_score', ascending=False, inplace=True)
    print(author_options['name_score'])
    return render_template('link_thesaurus/authorlist.html', author_name = author_name, author_options=list(author_options.itertuples()))    


def normalized_levenshtein(s1,s2):
    # normalized Levenshtein distance: normalize by the max of the lengths
    l = float(max(len(s1), len(s2))) # normalize by length, high score wins
    return  (l - distance.edit_distance(s1, s2)) / l         
    

def score_names(authorshipItem, given_name, family_name):
    familyNameScore =  normalized_levenshtein(authorshipItem['foaf_familyname'],family_name)   
    firstNameScore = 1
    try: 
        an,cn= [list(filter(None,re.split('\.|\s+', name))) for name in [authorshipItem['foaf_givenname'],given_name]]
        firstNameScore *= 1 if len(an)==len(cn) else .8
    except: 
        #print ('Cant score firstname(s)')
        #print (contributorItem, contributorItem.dtype)
        an, cn = [[],[]]
        firstNameScore=.5
    
    for i in range(min(len(an),len(cn))):
        if len(an[i])==1 or len(cn[i])==1: # Just initials: compare first letter only
                                           # Gives less reliable score: make it 0.9 to account for confidence loss 
            firstNameScore *= 0.9 if an[i][0] == cn[i][0] else .5
        else:
            firstNameScore *= normalized_levenshtein(an[i],cn[i])
    return (50*familyNameScore+50*firstNameScore)