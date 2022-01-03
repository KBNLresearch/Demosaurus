import rdflib
import os
import pandas as pd
import csv_db
from demosauruswebapp.demosaurus.link_thesaurus import normalize_name


def obtain_primary_name(graph):
    name_query = """select ?uri ?label ?familyname ?name where { 
               ?uri schema:mainEntityOfPage/schema:isPartOf <http://data.bibliotheken.nl/id/dataset/persons> ;      
                    rdfs:label ?label
                  OPTIONAL
                 {
                    ?uri schema:name ?name ;
                       schema:familyName ?familyname ;
                 }
            }"""
    primary_names = pd.DataFrame([
        (uri.split('/p')[-1],
         name if name else ' '.join(label.split('(')[0].split(', ')[::-1]),
         familyname if familyname else label.split(',')[0], # familyname includes name prefix, label.split(',')[0] does not
         label.split(',')[0])
        for uri, label, familyname, name in graph.query(name_query)],
        columns=['author_ppn', 'name', 'familyname', 'searchkey'])
    return primary_names

def obtain_alternate_names(graph):
    alternate = rdflib.term.URIRef('http://schema.org/alternateName')

    alternate_names = pd.DataFrame([
        (uri.split('/p')[-1],
         ' '.join(name.split('(')[0].split(', ')[::-1]),
         name.split('(')[0].split(',')[0])
        for uri, _, name in graph.triples((None, alternate, None))],
        columns=['author_ppn', 'name', 'familyname'])
    alternate_names['searchkey'] = alternate_names['familyname']
    return alternate_names



def ingest_nta_names(chunk_dir):
    for chunk in os.listdir(chunk_dir):
        print(chunk)
        fname = os.path.join(chunk_dir,chunk)
        g = rdflib.Graph()
        g.parse(fname)
        primary_names = obtain_primary_name(g)
        alternate_names = obtain_alternate_names(g)
        all_names = primary_names.append(alternate_names).sort_values(by='author_ppn')
        all_names['name_normalized'] = all_names['name'].apply(normalize_name)
        all_names['searchkey'] = all_names['searchkey'].apply(normalize_name)
        columns = ['author_ppn', 'searchkey','name', 'name_normalized','familyname']
        csv_db.export_csv('author_name_options', all_names[columns],check_schema=True,append=True)
