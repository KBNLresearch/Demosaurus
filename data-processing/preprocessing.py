import pandas as pd
import numpy as np
import sqlite3
import random 
import re
import nltk
import csv
from unidecode import unidecode
import difflib
import os, sys
from collections import Counter
import pickle
from fuzzywuzzy import process

def export_table(table_name, df):
    """Export dataframe <df> to a csv file in ../data/clean_csv/<table_name>.csv """
    assert len(df)>0    
    table_loc = os.path.join('../data/clean_csv',table_name+'.csv')
    df.to_csv(table_loc, sep=';', index = False)

def import_table(table_name):
    """Import and return dataframe from a csv file in ../data/clean_csv/<table_name>.csv """
    table_loc = os.path.join('../data/clean_csv',table_name+'.csv')
    return pd.read_csv(table_loc, sep=';')


def match_4000parts(kmc_4000):
    """Subroutinre for parsing title/author records from kmc 4000"""
    parts = kmc_4000.split(' / ')
    titlebit = parts[0]
    if len(parts)>1: authorbit = ' / '.join(parts[1:])
    else: authorbit = ''
    return pd.Series([titlebit, authorbit],
            index= ['titelvermelding','verantwoordelijkheidsvermelding'])

def read_ggc_data(filename, sep, skiprows=[]):
    """Obtain ggc data from csv file. Convert column names to interpretable names."""
    ggc_data = pd.read_csv(filename, sep=sep, skiprows = skiprows, dtype=str)
    ggc_data.rename(columns={
        'kmc_0100':'publication_ppn',      
#        'maa1':'maa1', 'maa2':'maa2',      
        'status':'status_publicatie',      
        'kmc_0500':'status_beschrijving',      
        'kmc_1100':'jaar_van_uitgave',     
        'kmc_1121':'unescocode_1', 'kmc_1122':'unescocode_2',      
        'kmc_1500_a':'taal_publicatie',      
        'kmc_1500_c':'taal_origineel',      
        'kmc_1700':'land_van_uitgave',     
        'kmc_2000':'isbn', 'kmc_2001':'isbn_2',      
        #'kmc_3000':'auteur_primair',     # Fobid interpretations 
        #'kmc_3001':'auteur_co_1',      
        #'kmc_3002':'auteur_co_2',      
        #'kmc_3003':'auteur_co_3',     
        #'kmc_301x_1':'auteur_sec_1',     
        #'kmc_301x_2':'auteur_sec_2',      
        #'kmc_301x_3':'auteur_sec_3',     
        #'kmc_301x_4':'auteur_sec_4',     
        'kmc_301x_1':'kmc_3011',
        'kmc_301x_2':'kmc_3012',
        'kmc_301x_3':'kmc_3013',
        'kmc_301x_4':'kmc_3014',
        #'kmc_4000':'titel_verantwoordelijkheidsvermelding',     
        'kmc_4030':'uitgever',      
        'kmc_4031':'uitgever_2',      
        'kmc_4061':'annotatie_illustratie',      
        'kmc_4200':'deelvermelding',      
        'kmc_4201':'annotatie_alg','kmc_4202':'annotatie_alg2',     
        'kmc_4203':'annotatie_editie',      
        'kmc_4204':'annotatie_bibliografie',      
        'kmc_4205':'annotatie_inhoud',      
        'kmc_4206':'annotatie_taal',      
        'kmc_4207':'annotatie_samenvatting_inhoudsopgave',     
        'kmc_4208':'annotatie_verschijningsfrequentie',     
        'kmc_4209':'annotatie_karakteriserendegegevens',      
        'kmc_4600':'annotatie_analytisch_volw',     
        'kmc_4601':'annotatie_analytisch_jeugd',
        'kmc_5060':'NUGI_genre',      
        'kmc_5061':'NUR_rubriek',     
        'kmc_520x_1':'brinkman_1','kmc_520x_2':'brinkman_2','kmc_520x_3':'brinkman_3','kmc_520x_4':'brinkman_4',     
        'kmc_556x_1':'CBK_thema_1','kmc_556x_2':'CBK_thema_2','kmc_556x_3':'CBK_thema_3','kmc_556x_4':'CBK_thema_4',     
        'kmc_557x_1':'CBK_genre_1','kmc_557x_2':'CBK_genre_2','kmc_557x_3':'CBK_genre_3','kmc_557x_4':'CBK_genre_4'
        }, inplace=True)

    ggc_data[['titelvermelding', 'verantwoordelijkheidsvermelding']]= ggc_data.apply(lambda x: match_4000parts(x['kmc_4000']), axis=1)     


    print('Parsed ggc_data. Number of records:', len(ggc_data))
    return ggc_data

"""For text processing, obtain stop word list from file and initialize tokenizer"""
with open('stopwordsDutch.txt','r') as f:
    stopwords = [x.strip() for x in f.readlines()]
tokenizer = nltk.tokenize.WordPunctTokenizer()    

def clean_publisher(publisher):
    """Rewrite publisher name ommitting standard formulations and stopwords, aimed at more uniformity"""
    if not isinstance(publisher,str) : return ''
    throwaway = ['uitgeverij', 'uitgevers', 'uitgever', 'drukkerij', 'uitgegeven', 'boekdrukkerij', 'uitgeversmaatschappij', 
         'uitgeversmij', 'n.v.', 'uitgevers-maatschappij', 'maatschappij', '-maatschappij', '-', 'uitgevers-mij', 
         'gebr', '.', ']', '[', 'gebroeders', 'stichting', 'n.v', 'b.v', 'b.v.', 'be', 'uitgeversmij', 'mij.', 
         '-mij', '-mij.', 'uitg.', 'mij', 'amsterdam', 'holland', '.]', '[.', ')', '.)', '(', '(.', ';', ':', 'nv', 
         "'", 'distr', 'distributie', 'vof', 'v.o.f.']
    publisher = unidecode(publisher).lower()
    publisher = re.sub('^.*?: ', '', publisher)
    tokens = tokenizer.tokenize(publisher)
    tokens = [token for token in tokens if token not in stopwords and token not in throwaway]
    return ' '.join(tokens)

def publisher_mapping(publishers):
    """Obtain a mapping for spelling variations of publisher names to a 'standard form'
    Compare publisher names in the list and map similar ones to the more frequently occuring version
    (NB store mapping to file in order to allow quicker data processing)
    """
    publishers = Counter(publishers)
    mapping = {}
    for i, (entity_1, _) in enumerate(publishers.most_common()):
        if i%500 == 0: print(i)
        for j, (entity_2,_) in enumerate(publishers.most_common()):
            if j<=i: continue 
            if entity_2 in mapping: continue
            bonus = 0.5 if entity_1 + " " in entity_2 or entity_2.endswith(" " + entity_1) else 0
            #add bonus if publisher's name appears fully in the value of comparison
            if (difflib.SequenceMatcher(None, entity_1, entity_2).ratio() + bonus) > 0.88:
                entity = entity_1
                while entity in mapping:
                    entity = mapping[entity] # find the most frequent form (might involve several rewrights)
                mapping[entity_2] = entity
    return mapping


def export_basic_info(ggc_data):
    """Create a table with basic bibliographic info per publication and output to file """

    # set taal_origineel to taal_publicatie where taal_origineel is None
    nolang = pd.isnull(ggc_data['taal_origineel'])
    ggc_data.loc[nolang, 'taal_origineel'] = ggc_data.loc[nolang, 'taal_publicatie']

    # Process publishers: apply some cleaning and group similar items together
    print('Before cleaning:', len(ggc_data['uitgever'].unique()),'publishers.')
    ggc_data['uitgever'] = ggc_data['uitgever'].apply(clean_publisher)
    ggc_data['uitgever_2'] = ggc_data['uitgever_2'].apply(clean_publisher) 
    print('After cleaning:', len(ggc_data['uitgever'].unique()),'publishers.')
    try:
        with open('publisher_map.pkl','rb') as f:
            publisher_map = pickle.load(f)
    except:  
        publisher_map = publisher_mapping(list(ggc_data['uitgever'].dropna()) + list(ggc_data['uitgever_2'].dropna()))
        with open('publisher_map.pkl','wb') as f:
            pickle.dump(publisher_map, f)
    ggc_data['uitgever'] = ggc_data['uitgever'].map(publisher_map)
    ggc_data['uitgever_2'] = ggc_data['uitgever_2'].map(publisher_map)
    print('After grouping:', len(ggc_data['uitgever'].unique()), 'publishers.')

    # Convert publishing year to number: replace uncertainties ('X') with '5'
    ggc_data['jaar_van_uitgave'] = ggc_data['jaar_van_uitgave'].str.replace('X','5') 

    # select columns for basic info
    table = ggc_data[['publication_ppn', 'titelvermelding', 'verantwoordelijkheidsvermelding',
    'taal_publicatie', 'taal_origineel', 'land_van_uitgave', 
    'isbn', 'isbn_2',
    'jaar_van_uitgave', 'uitgever', 'uitgever_2']]
    export_table('publication_basicinfo', table)

def find_most_similar_thesaurus_item(x, thesaurus, column, threshold = 90): 
    """ Find matching thesaurus item for term x.
    Obtain the closest match and return if it is above the threshold  """
    item, score, index = process.extract(x, thesaurus[column], limit = 1)[0]
    if score >= threshold: 
        return thesaurus.loc[index,'identifier']   

def export_subjects(ggc_data, subset = []):
    """ Export subject indexing: relation between publication and subject term
    If a subset is provided, only run for those subject indexing schemes listed
    If a thesaurus is available, provide foreignkey to that table rather than the spelled out term
    Maintain order (ranking) of the indexing for a subset of subjects
    Export to tables per subject indexing scheme
    """
    ranked_subjects = ['brinkman','CBK_thema','CBK_genre','unescocode']
    nonranked_subjects = ['NUGI_genre','NUR_rubriek']
    for subject in (subset if subset != [] else ranked_subjects + nonranked_subjects):
        assert subject in ranked_subjects or subject in nonranked_subjects
        if subject in ranked_subjects:
            table = pd.DataFrame()
            for c in [c for c in ggc_data.columns if subject in c]:
                bit = ggc_data[['publication_ppn', c]].rename(columns={c:subject}).dropna()
                bit['rank'] = c.split('_')[-1]                
                table = table.append(bit, sort=False)
        else:
            table = ggc_data[['publication_ppn', subject]]
        if subject == 'CBK_genre':       
            thesaurus = import_table('thesaurus_CBK_genres')                         
            thesaurus['CBK_genre'] = thesaurus.genre.str.strip().str.lower()
            # Merge with thesaurus (ignore casing and omit trailing whitespace/punctuation)
            # to obtain identifiers
            df = table.merge(thesaurus, how='left', 
                left_on=table['CBK_genre'].str.lower().str.strip(' !\',+:'), 
                right_on=thesaurus['CBK_genre'])
            # Try to match items that weren't linked successfully with fuzzy matching
            df.loc[df['identifier'].isna(),'identifier'] = df.loc[df['identifier'].isna(),'CBK_genre_x'].apply(
                lambda x:find_most_similar_thesaurus_item(x, thesaurus, 'CBK_genre'))
            # get relevant columns and drop unmatched items 
            table = df[['publication_ppn','identifier','rank']].dropna() 
            # cast identifier back to integer (became float due to NAN's when merging)
            table.loc[:,'identifier'] = table.identifier.astype(pd.Int64Dtype())
            # rename column 
            table.rename(columns={'identifier':'CBK_genre'})
        export_table('publication_'+subject, table)

def export_annotations(ggc_data):
    """ Export a table with annotations on publications """
    df = pd.DataFrame()
    for c in [c for c in ggc_data.columns if 'annotatie' in c]:
        bit = ggc_data[['publication_ppn', c]].rename(columns={c:'annotation'}).dropna()
        bit['kind'] = '_'.join(c.split('_')[1:])
        df = df.append(bit, sort=False)
    export_table('publication_annotations', df)


def match_authorparts(author):
    """Subroutinre for parsing author records from kmcs 300X and 301X"""
    ppn = '(!(?P<author_ppn>[^!]+)!)?'
    role = '(\$(?P<role>[^!]+)\$)?'
    title = '(#(?P<title>[^#]+)#)?'
    name = '(?P<name>[^#$!]+)'
    match = re.match(title+name+role+ppn, author)
    index= ['title','name','role','author_ppn']

    if not match:
        print('Cannot match parts for', author)
        items = [None for i in index]
    else:
        items = [match.group(i) for i in index]
    return pd.Series(items, index= ['title','name','role','author_ppn'])

def export_authorship(ggc_data):
    """Export indexed authors as a relation between publication and author record. 
    Maintain KMC number to be able to interpret author role in publication
    """
    table = pd.DataFrame()

    for kmc in [3000,3001,3002,3003,3011,3012,3013,3014]:
        column = 'kmc_'+str(kmc)
        bit = ggc_data[['publication_ppn', column]].dropna()
        bit[['title','name','role','author_ppn']] = bit.apply(lambda x: match_authorparts(x[column]),axis=1)       
        bit['kmc'] = kmc
        table = table.append(bit.drop(columns=[column]), sort=False)
        
    export_table('authorship_ggc', table)



def main():
    if not os.path.isdir('../data/clean_csv'):
        os.makedirs('../data/clean_csv')
    
    filename = '../data/kb_kinderboeken_20200320.txt'
    # Some rows in this specific file have issues, e.g. there is a tab inside a field 
    # See file '../data/Data-issues' for more info
    # Since there were not that many, I decided to not bother and just skip those rows
    rows_with_issues  = [13463, 52313, 80849, 147033, 156969, 171677, 189676, 195328]
    ggc_data = read_ggc_data(filename, sep='\t', skiprows=rows_with_issues)   

    print('Basic info')
    export_basic_info(ggc_data)
    print('Subject indexing')
    export_subjects(ggc_data)
    print('Author indexing')
    export_authorship(ggc_data)
    print('Annotations')
    export_annotations(ggc_data)


if __name__ == "__main__":
    main()