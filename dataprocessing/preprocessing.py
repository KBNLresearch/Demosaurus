import os.path
import re
from unidecode import unidecode
import difflib
import nltk
from collections import Counter
import pickle
import csv_db
from demosauruswebapp.link_thesaurus import normalize_name

"""For text processing, obtain stop word list from file and initialize tokenizer"""
with open('dataprocessing/stopwordsDutch.txt','r') as f:
    stopwords = [x.strip() for x in f.readlines()]
tokenizer = nltk.tokenize.WordPunctTokenizer()


class ReflectDict(dict):
    '''Subclass of dictionary which returns the key itself for missing keys.
    Used for publisher mapping '''
    def __init__(self, content = None):
        if content is None:
            super().__init__()
        else:
            super().__init__(content)
    def __missing__(self, x):
        return x

def closest_match(thesaurus, term):
    try:
        identifier = thesaurus.loc[thesaurus['term'] == term, 'identifier'][0]
    except:
        thesaurus['match'] = thesaurus['term'].apply(lambda x: difflib.SequenceMatcher(None, x.strip().lower(), term.strip().lower()).ratio())
        identifier = thesaurus.iloc[thesaurus['match'].idxmax()]['identifier']
    return identifier

def CBK_genres_to_identifiers(CBK_genres):
    if len(CBK_genres)>0:
        thesaurus = csv_db.import_csv('thesaurus_CBK_genres', True)
        CBK_genres['term_identifier'] = CBK_genres['term'].apply(lambda x: closest_match(thesaurus,x))
    else:
        CBK_genres.rename(columns={'term':'term_identifier'})
    return CBK_genres[['publication_ppn','term_identifier','rank']]

def normalize_author_names(publication_contributors):
    publication_contributors['name_normalized'] = publication_contributors.apply(lambda row: normalize_name(' '.join([i for i in [row.firstname, row.prefix, row.familyname] if type(i)==str])), axis = 1)
    return publication_contributors

def normalize_publishers(basicinfo, postfix):
    # map publishers to canonical form
    uitgevers = basicinfo['uitgever'].unique()
    publisher_map = publisher_mapping(uitgevers, postfix)
    #update_publisher_table(publisher_map)
    basicinfo['uitgever'] = \
        basicinfo['uitgever'].map(publisher_map) # instead, use identifier from table
    return basicinfo

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

def publisher_mapping(publishers, postfix=''):
    """Obtain a mapping for spelling variations of publisher names to a 'standard form'
    Compare publisher names in the list and map similar ones to the more frequently occuring version
    (NB store mapping to file in order to allow quicker data processing)
    """
    fname = 'dataprocessing/publisher_map'+('_'+postfix if postfix else '')+'.pick'
    if os.path.exists(fname):
        with open(fname, 'rb') as f:
            mapping = pickle.load(f)
    else:
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
                        entity = mapping[entity] # find the most frequent form (might involve several rewrites)
                    mapping[entity_2] = entity
        with open(fname, 'wb') as f:
            pickle.dump(mapping, f)
    return ReflectDict(mapping)  # Make the mapping return key itself for unknown key