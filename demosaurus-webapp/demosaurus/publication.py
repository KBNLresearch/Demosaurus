from flask import (
    Blueprint, flash, g, redirect, render_template, get_template_attribute, request, url_for, jsonify
)
from werkzeug.exceptions import abort


from demosaurus.db import get_db


bp = Blueprint('publication', __name__)

@bp.route('/<id>/view')
def view(id):
    db = get_db()
    # Obtain data on publication & contributors from the database
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


    subjects = db.execute(
        ' WITH ranks AS ('
        '    SELECT rank FROM publication_brinkman '
        '    UNION SELECT rank FROM publication_CBK_genre '
        '    UNION SELECT rank FROM publication_CBK_thema'
        ' )'
        ' SELECT ranks.rank, '
        ' t1.CBK_genre AS CBK_genre_id, t1a.genre AS CBK_genre, '
        ' t2.CBK_thema, '
        ' t3.brinkman AS brinkman_id, t3a.term AS brinkman, t3a.kind AS brinkman_kind, '
        ' t4.NUGI_genre, '
        ' t5.NUR_rubriek '
        ' FROM ranks'
        ' LEFT JOIN publication_CBK_genre t1 ON t1.publication_ppn =:ppn AND ranks.rank =t1.rank '
        ' LEFT JOIN thesaurus_CBK_genres t1a ON t1a.identifier = t1.CBK_genre  '
        ' LEFT JOIN publication_CBK_thema t2 ON t2.publication_ppn =:ppn AND ranks.rank =t2.rank '
        ' LEFT JOIN publication_brinkman  t3 ON t3.publication_ppn =:ppn AND ranks.rank =t3.rank '
        ' LEFT JOIN thesaurus_brinkmantrefwoorden t3a ON t3a.ppn = t3.brinkman'
        ' LEFT JOIN publication_NUGI_genre t4 ON t4.publication_ppn =:ppn AND ranks.rank =1 '
        ' LEFT JOIN publication_NUR_rubriek t5 ON t5.publication_ppn =:ppn AND ranks.rank =1 '
        ,
        {'ppn':id}
        ).fetchall()

    # Serve the list to the client: render the template with the obtained data
    return render_template('publication/view.html', publication = publication, cover = cover_location, contributors=contributors, subjects = subjects, role_list=roles_options)



@bp.route('/')
def overview():
    db = get_db()
    # Select a random subset of publications from the test set to serve as examples
    publications = db.execute(
        ' SELECT publication_basicinfo.publication_ppn, titelvermelding, verantwoordelijkheidsvermelding'
        ' FROM publication_basicinfo'
        ' JOIN publication_datasplits ON publication_datasplits.publication_ppn = publication_basicinfo.publication_ppn'
        ' WHERE publication_datasplits.datasplit like \"test\"'
        ' ORDER BY RANDOM() LIMIT 20'
    ).fetchmany(20)
    return render_template('publication/overview.html', publications=publications)
