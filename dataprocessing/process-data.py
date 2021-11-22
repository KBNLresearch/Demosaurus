import pandas as pd

import read_pica
import preprocessing
import csv_db
import os
import numpy as np

def ingest_publication_data(file_name, new_datasplits = False, dataset_id = -1):
    assert os.path.exists(file_name)
    NBD_fiction = pd.read_csv('data/NBD-pilotdata/kb_fiction_ppns.txt', names = ['ppn'])
    ppn_list = list(NBD_fiction['ppn'])
    # obtain publication records: create pandas dataframes
    dfs = read_pica.obtain_dataframes(file_name, ppn_list=ppn_list)
    if new_datasplits:
        datasplits = dfs['publication_basicinfo'][['publication_ppn']]
        datasplits['dataset_id']=dataset_id
        datasplits['datasplit_id'] = (np.random.uniform(size=len(datasplits))>3/4).astype(int)
        dfs['publication_datasplits'] = datasplits
    for table_name, table in dfs.items():
        print('Obtain', table_name)
    return dfs

def apply_preprocessing(dfs, postfix = ''):
    #dfs['publication_basicinfo'] = preprocessing.normalize_publishers(dfs['publication_basicinfo'], postfix)
    dfs['publication_CBK_genre'] = preprocessing.CBK_genres_to_identifiers(dfs['publication_CBK_genre'])
    return dfs

def update_publisher_table(publisher_map):
    df = csv_db.import_csv('publishers', csv_db.get_schema('publishers'))
    publisher_names_canonical = set(publisher_map.values())
    # TODO: append publisher names to df
    # Write back to csv file
    #df.append()
    return df

def create_indices():
    True

def create_views():
    True


def process_publication_info(set_name, dataset_id):
    # Ingest publication info and write to DB
    fname = 'data/NBD-pilotdata/picaplus_kb_ebooks_20210927.XML'
    dfs = ingest_publication_data(fname, new_datasplits=True, dataset_id=dataset_id)
    dfs = apply_preprocessing(dfs, postfix='_'+set_name if set_name else '')
    for table_name, df in dfs.items():
        csv_db.export_csv(table_name, df, postfix='_'+set_name if set_name else '')

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
    process_thesauri()
    process_publication_info(set_name='NBD', dataset_id=1)
    create_views()
    create_indices()

    for table in csv_db.schemata.keys():
        csv_db.fill_table(table,db='data/demosaurus_NBD.sqlite', overwrite=True, postfix = '_NBD')

