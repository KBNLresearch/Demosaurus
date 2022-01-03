import pandas as pd

import read_pica
import preprocessing
import read_rdf
import csv_db
import views_and_indices
import os
import numpy as np


def ingest_publication_data(file_name):
    assert os.path.exists(file_name)
    nbd_fiction = pd.read_csv('data/NBD-pilotdata/kb_fiction_ppns.txt', names=['ppn'])
    ppn_list = list(nbd_fiction['ppn'])
    # obtain publication records: create pandas dataframes
    dfs = read_pica.obtain_dataframes(file_name, ppn_list=ppn_list)
    for table_name, table in dfs.items():
        print('Obtain', table_name)
    return dfs


def ingest_nta_names(chunk_dir):
    read_rdf.ingest_nta_names(chunk_dir)


def create_datasplits(set_name, dataset_id, heldout_file=''):
    df = csv_db.import_csv('publication_basicinfo', check_schema=False, postfix='_' + set_name)[['publication_ppn']]
    df['dataset_id'] = dataset_id
    if heldout_file:
        with open(heldout_file, 'r') as f:
            heldout_ppns = f.read().splitlines()
        df.loc[df.publication_ppn.isin(heldout_ppns), 'datasplit_id'] = 2
    tosplit = df.datasplit_id.isna()
    df.loc[tosplit, 'datasplit_id'] = (np.random.uniform(size=sum(tosplit)) > 3 / 4).astype(
        int)  # train (0) and test (1)
    csv_db.export_csv('publication_datasplits', df, postfix='_' + set_name if set_name else '')


def apply_preprocessing(dfs, postfix=''):
    # dfs['publication_basicinfo'] = preprocessing.normalize_publishers(dfs['publication_basicinfo'], postfix)
    dfs['publication_CBK_genre'] = preprocessing.CBK_genres_to_identifiers(dfs['publication_CBK_genre'])
    return dfs


def update_publisher_table(publisher_map):
    df = csv_db.import_csv('publishers', csv_db.get_schema('publishers'))
    publisher_names_canonical = set(publisher_map.values())
    # TODO: append publisher names to df
    # Write back to csv file
    # df.append()
    return df


def process_publication_info(set_name):
    # Ingest publication info and write to DB
    fname = 'data/NBD-pilotdata/picaplus_kb_ebooks_20210927.XML'
    dfs = ingest_publication_data(fname)
    dfs = apply_preprocessing(dfs, postfix='_' + set_name if set_name else '')

    for table_name, df in dfs.items():
        csv_db.export_csv(table_name, df, postfix='_' + set_name if set_name else '')


def process_thesauri():
    # TODO: implement code to ingest thesauri of subject headings and NTA
    # and write to DB
    thesauri = [
        'thesaurus_brinkmantrefwoorden',
        'thesaurus_brinkman_kinds',
        'thesaurus_CBK_genres',
        'author_NTA',
        'authorship_roles'
    ]
    for thesaurus in thesauri:
        schema = csv_db.get_schema(thesaurus)
        columns = {column['field'] for column in schema}
        df = csv_db.import_csv(thesaurus, schema)
        assert set(df.columns) == columns


if __name__ == '__main__':
    print('Start processing')
    # Assuming Thesauri are in place, check that they obey the DB scheme
    # process_thesauri()
    # ingest_nta_names('data/nta_rdf/')

    # Ingest and preprocess publication information: store in CSV files
    # process_publication_info(set_name='NBD')

    # Split into train, test, heldout
    # create_datasplits(set_name='NBD', dataset_id=1,
    #                  heldout_file = 'data/NBD-pilotdata/KB_validatieset_def.csv')

    # Obtain information from CSVs and write to database
    # for table in csv_db.schemata.keys():
    #    if table != 'author_name_options': continue
    #    csv_db.fill_table(table,db='data/demosaurus_NBD.sqlite', overwrite=True, postfix = '_NBD')

    # Build indices (+FTS5) and views for regular entries
    # views_and_indices.create_views(db='data/demosaurus_NBD.sqlite')
    # views_and_indices.create_indices(db='data/demosaurus_NBD.sqlite')
