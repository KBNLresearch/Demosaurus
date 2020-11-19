import sqlite3
import pandas as pd
import os

def import_table(table_name, schema):
    table_loc = os.path.join('../data/clean_csv',table_name+'.csv')
    df = pd.read_csv(table_loc, sep=';', dtype = {d['field']:d['dtype'] for d in schema})
    return df

def create_table(table_name, schema, db = '../data/demosaurus.sqlite'):
	
	statement = "CREATE TABLE IF NOT EXISTS %s (" % table_name
	for i, column in enumerate(schema):
		if i>0: statement += ','
		statement += '\n\t%s %s %s' % (column['field'], column['type'], column['constraints'])
	statement += '\n);'

	with sqlite3.connect(db) as con:
		c = con.cursor()
		c.execute('DROP TABLE IF EXISTS %s;' % table_name)
		c.execute(statement)
	
def fill_table(table_name, db = '../data/demosaurus.sqlite', overwrite = True):
	schema = get_schema(table_name)
	print(table_name, schema)
	df = import_table(table_name, schema)
	if overwrite:
		create_table(table_name, schema)
	with sqlite3.connect(db) as con:
		df.to_sql(name=table_name,con=con, if_exists=('append' if overwrite else 'replace'), index=False)

def get_schema(table_name):
	if table_name == 'publication_basicinfo':
		schema = [
			{'field': 'publication_ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL PRIMARY KEY'},
			{'field': 'titel_verantwoordelijkheidsvermelding', 'dtype':str, 'type':'TEXT','constraints':''},
	    	{'field': 'taal_publicatie', 'dtype':str, 'type': 'TEXT', 'constraints':''},
	    	{'field': 'taal_origineel', 'dtype':str, 'type': 'TEXT', 'constraints':''},
	    	{'field': 'land_van_uitgave', 'dtype':str, 'type': 'TEXT', 'constraints':''},
	    	{'field': 'isbn', 'dtype':pd.Int64Dtype(), 'type': 'INTEGER', 'constraints':''},
	    	{'field': 'isbn_2', 'dtype':pd.Int64Dtype(), 'type': 'INTEGER','constraints':''},
	    	{'field': 'jaar_van_uitgave', 'dtype':pd.Int64Dtype(), 'type': 'INTEGER', 'constraints':''},
	    	{'field': 'uitgever', 'dtype':str, 'type': 'TEXT', 'constraints':''},
	    	{'field': 'uitgever_2', 'dtype':str, 'type': 'TEXT', 'constraints':''}]
	elif table_name == 'publication_titlefeatures':
		schema = [
			{'field': 'publication_ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL PRIMARY KEY'},
			{'field':'titelvermelding', 'dtype':str, 'type':'TEXT','constraints':''},
			{'field':'titellengte', 'dtype':pd.Int64Dtype(), 'type': 'INTEGER','constraints':''},
			{'field':'titellengte_ranges', 'dtype':str, 'type': 'TEXT','constraints':''},
			{'field':'titelwoorden', 'dtype':str, 'type': 'TEXT','constraints':''},
			{'field':'titellengte_Nwoorden', 'dtype':pd.Int64Dtype(), 'type': 'INTEGER','constraints':''},
			{'field':'woordlengte_gem', 'dtype':float, 'type': 'REAL','constraints':''},
			{'field':'woordlengte_gem_rond', 'dtype':float, 'type': 'REAL','constraints':''},
			{'field':'woordlengte_med', 'dtype':float, 'type': 'REAL','constraints':''}]
	elif table_name == 'publication_annotations':
		schema = [
			{'field': 'publication_ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL'},
			{'field': 'annotation', 'dtype':str, 'type':'TEXT','constraints':''},
			{'field': 'kind', 'dtype':str, 'type':'TEXT','constraints':''}
			]	
	elif table_name in ['publication_'+subject for subject in ['brinkman','CBK_thema','CBK_genre']]:
		subject = '_'.join(table_name.split('_')[1:])
		schema = [
			{'field': 'publication_ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL'},
			{'field':subject, 'dtype':str, 'type':'TEXT','constraints':''},
			{'field':'rank', 'dtype':pd.Int64Dtype(), 'type': 'INTEGER','constraints':''}
			]			
	elif table_name in ['publication_'+subject for subject in ['NUGI_genre','NUR_rubriek']]:
		subject = '_'.join(table_name.split('_')[1:])
		schema = [
			{'field': 'publication_ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL PRIMARY KEY'},
			{'field':subject, 'dtype':str, 'type':'TEXT','constraints':''}
			]	
	elif table_name == 'author_NTA':
		schema = [
			{'field': 'author_ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL PRIMARY KEY'},
			{'field': 'foaf_name', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'foaf_givenname', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'foaf_familyname', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'skos_preflabel', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'birthyear', 'dtype':str, 'type':'TEXT', 'constraints':''}, # not always numerical in NTA
			{'field': 'deathyear', 'dtype':str, 'type':'TEXT', 'constraints':''}, # not always numerical in NTA
			{'field': 'editorial', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'editorial_nl', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'skopenote_nl', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'related_entry_ppn', 'dtype':str, 'type':'TEXT', 'constraints':''}]
	elif table_name in ['author_isni','author_viaf','author_worldcat']:
		schema = [
			{'field': 'author_ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL'},
			{'field': 'identifier', 'dtype':str, 'type':'TEXT', 'constraints':''}]
	elif table_name == 'author_wikipedia':
		schema = [
			{'field': 'author_ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL'},
			{'field': 'wikidata_id', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'wiki_url', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'language', 'dtype':str, 'type':'TEXT', 'constraints':''}]			
	elif table_name == 'wiki_preferred_languages':
		schema = [
			{'field': 'language', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL PRIMARY KEY'},
			{'field': 'rank', 'dtype':pd.Int64Dtype(), 'type': 'INTEGER', 'constraints':''}
			]
	elif table_name == 'authorship_roles':
		schema = [
			{'field': 'authorship_roles_ID', 'dtype':pd.Int64Dtype(), 'type': 'INTEGER', 'constraints':'NOT NULL PRIMARY KEY'},
			{'field': 'ggc_code', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'onix_code', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'legible', 'dtype':str, 'type':'TEXT', 'constraints':''},
			]
	elif table_name == 'authorship_ggc':
		schema = [
			{'field': 'publication_ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL'},
			{'field': 'kmc', 'dtype':pd.Int64Dtype(), 'type': 'INTEGER', 'constraints':'NOT NULL'},
			{'field': 'title', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'name', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'role', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'author_ppn', 'dtype':str, 'type':'TEXT', 'constraints':''}]	
	elif table_name == 'publication_datasplits':
		schema = [
			{'field': 'publication_ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL PRIMARY KEY'},
			{'field': 'datasplit', 'dtype':str, 'type':'TEXT', 'constraints':''}]
	elif table_name == 'thesaurus_CBK_genres':
		schema = [
			{'field': 'identifier', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL PRIMARY KEY'},
			{'field': 'genre', 'dtype':str, 'type':'TEXT', 'constraints':''}]
	elif table_name == 'thesaurus_brinkmantrefwoorden':
		schema = [
			{'field': 'ppn', 'dtype':str, 'type':'TEXT', 'constraints':'NOT NULL'},
			{'field': 'term', 'dtype':str, 'type':'TEXT', 'constraints':''},
			{'field': 'kind', 'dtype':str, 'type':'TEXT', 'constraints':''}]
	return schema


def main():
	#fill_table('publication_basicinfo')
	
	#for subject in ['brinkman','CBK_thema','CBK_genre','NUGI_genre','NUR_rubriek']:
	#	fill_table('publication_'+subject)
	#for authorbit in ['author_NTA','author_isni','author_viaf','author_wikipedia','author_worldcat','wiki_preferred_languages', 'authorship_roles']:
	#	fill_table(authorbit)
	#fill_table('publication_CBK_genre')
	#for bit in ['thesaurus_CBK_genres','thesaurus_brinkmantrefwoorden']:
#		fill_table(bit)
	#fill_table('authorship_ggc')
	#fill_table('publication_datasplits')
	#fill_table('publication_annotations')
	fill_table('publication_titlefeatures')



if __name__ == "__main__":
    main()	   