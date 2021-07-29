from flask import (
     Blueprint, request)#, flash, g, redirect, render_template, get_template_attribute, url_for, jsonify
# )
# from werkzeug.exceptions import abort
import requests

# from demosaurus.db import get_db

# import pandas as pd
# from nltk.metrics import distance
# import re
# import numpy as np

bp = Blueprint('subject_headings', __name__)

base_url = 'https://kbresearch.nl/annif/v1/'

@bp.route('/annif-projects/')
def annif_projects():
    response = requests.get(base_url+'projects')
    if response.status_code == 200:
        return response.json()
    else:
        print('Unable to obtain Annif projects from', response.url)

@bp.route('/annif-suggestions/')
def annif_suggestions():
    params = dict(request.args) # turn into a mutable dictionary
    
    project = params.pop('project')
    print(params)

    url =  base_url + "projects/" + project + "/suggest"
    #print(url)
    response = requests.post(url, data = params) # Hier gaat iets mis?! Geeft error 400 "Bad request" dus er is iets malformed
    if response.status_code == 200:
        return response.json()
    else:
        print('Unable to obtain Annif suggestions from', response.url)      
        print(response.status_code)