from flask import (
    Blueprint, flash, g, redirect, render_template, get_template_attribute, request, url_for, jsonify
)
from werkzeug.exceptions import abort


from demosaurus.db import get_db


bp = Blueprint('publication', __name__)

@bp.context_processor
def utility_processor():    
    def list_of_roles():
        db = get_db()
        roles = db.execute(
            ' SELECT author_rolesID, legible, ggc_code'
            ' FROM authorship_roles'
        ).fetchall()
        print(roles)
        return json.dump(list_of_roles)
    return dict(list_of_roles=list_of_roles)

@bp.route('/<id>/view')
def view(id):
    db = get_db()
    publication = db.execute(
        ' WITH annotations AS ('
        '     SELECT publication_ppn, group_concat(annotation) AS annotations from publication_annotations'
        '     WHERE publication_annotations.publication_ppn = ?'
        '     AND kind in ("samenvatting_inhoudsopgave", "analytisch_volw", "analytisch_jeugd")'
        '     GROUP BY publication_ppn)'
        ' SELECT *'
        ' FROM publication_basicinfo'
        ' LEFT JOIN annotations'
        ' ON publication_basicinfo.publication_ppn = annotations.publication_ppn'
        ' WHERE publication_basicinfo.publication_ppn = ?',
        (id,id)
    ).fetchone()

    print(publication.keys)

    contributors = db.execute(
        ' SELECT *'
        ' FROM authorship_ggc'
        ' LEFT JOIN authorship_roles'
        ' ON authorship_ggc.role = authorship_roles.ggc_code'
        ' WHERE authorship_ggc.publication_ppn = ?',
        (id,)
    ).fetchall()

    roles_options = db.execute(
            ' SELECT authorship_roles_ID, legible, ggc_code'
            ' FROM authorship_roles'
        ).fetchall()

    try:
        cover_location = db.execute(
            ' SELECT *'
            ' FROM "covers"'
            ' WHERE publication_ppn = ?'
            ' AND side = "front"',
            (id,)
        ).fetchone()
    except:
        cover_location = None


    print(len(contributors),  'contributor records')
    try: print(contributors[0].keys())
    except: True

    return render_template('publication/view.html', publication = publication, cover = cover_location, contributors=contributors, role_list=roles_options)



@bp.route('/')
def overview():
    db = get_db()
    publications = db.execute(
        ' SELECT publication_ppn, titelvermelding, verantwoordelijkheidsvermelding'
        ' FROM publication_basicinfo'
        ' ORDER BY RANDOM() LIMIT 20'
    ).fetchmany(20)
    return render_template('publication/overview.html', publications=publications)
