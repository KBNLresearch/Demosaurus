import sqlite3
import pandas as pd
import os

schemata = {
	'publication_basicinfo': [
		{'field': 'publication_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL PRIMARY KEY'},
		{'field': 'isbn', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'titelvermelding', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'verantwoordelijkheidsvermelding', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'taal_publicatie', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'taal_origineel', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'land_van_uitgave', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'jaar_van_uitgave', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': ''},
		{'field': 'uitgever', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'uitgever_plaats', 'dtype': str, 'type': 'TEXT', 'constraints': ''}],
	'publication_koepeltitel': [
		{'field': 'publication_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'koepel_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'}],
	'publication_annotations': [
		{'field': 'publication_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'annotation', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'kind', 'dtype': str, 'type': 'TEXT', 'constraints': ''}],
	'publication_CBK_thema':[
		{'field': 'publication_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'term', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'rank', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': ''}],
	'publication_CBK_genre':[
		{'field': 'publication_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'}, # 'NOT NULL FOREIGN KEY REFERENCES thesaurus_brinkman_kinds.brinkman_kind_id'}],
		{'field': 'term_identifier', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'rank', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': ''}],
	'publication_brinkman':[
		{'field': 'publication_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'term_identifier', 'dtype': str, 'type': 'TEXT', 'constraints':'NOT NULL'},
		{'field': 'rank', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': ''}],
	'publication_NUGI_genre': [
		{'field': 'publication_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL PRIMARY KEY'},
		{'field': 'term_identifier', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': ''}],
	'publication_NUR_rubriek': [
		{'field': 'publication_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL PRIMARY KEY'},
		{'field': 'term_identifier', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': ''}],
	'author_NTA':  [
		{'field': 'author_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL PRIMARY KEY'},
		{'field': 'foaf_name', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'foaf_givenname', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'foaf_familyname', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'skos_preflabel', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'birthyear', 'dtype': str, 'type': 'TEXT', 'constraints': ''},  # not always numerical in NTA
		{'field': 'deathyear', 'dtype': str, 'type': 'TEXT', 'constraints': ''},  # not always numerical in NTA
		{'field': 'editorial', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'editorial_nl', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'skopenote_nl', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'related_entry_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': ''}],
	'author_isni': [
		{'field': 'author_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'identifier', 'dtype': str, 'type': 'TEXT', 'constraints': ''}],
	'author_viaf': [
		{'field': 'author_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'identifier', 'dtype': str, 'type': 'TEXT', 'constraints': ''}],
	'author_worldcat': [
		{'field': 'author_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'identifier', 'dtype': str, 'type': 'TEXT', 'constraints': ''}],
	'author_wikipedia': [
		{'field': 'author_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'wikidata_id', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'wiki_url', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'language', 'dtype': str, 'type': 'TEXT', 'constraints': ''}],
	'wiki_preferred_languages': [
		{'field': 'language', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL PRIMARY KEY'},
		{'field': 'rank', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': ''}],
	'authorship_roles': [
		{'field': 'authorship_roles_ID', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER',
		 'constraints': 'NOT NULL PRIMARY KEY'},
		{'field': 'ggc_code', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'onix_code', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'legible', 'dtype': str, 'type': 'TEXT', 'constraints': ''}],
	'publication_contributors': [
		{'field': 'publication_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'rank', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': 'NOT NULL'},
		{'field': 'title', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'firstname', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'prefix', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'familyname', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'role', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'author_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': ''}],
	'publication_datasplits': [
		{'field': 'publication_ppn', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'},
		{'field': 'dataset_id', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': ''},
		{'field': 'datasplit_id', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': ''}],
	'datasets': [
		{'field': 'dataset_id', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': 'NOT NULL PRIMARY KEY'},
		{'field': 'dataset', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'}],
	'datasplits': [
		{'field': 'datasplit_id', 'dtype': pd.Int64Dtype(), 'type': 'INTEGER', 'constraints': 'NOT NULL PRIMARY KEY'},
		{'field': 'datasplit', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL'}],
	'thesaurus_CBK_genres': [
		{'field': 'identifier', 'dtype': str, 'type': 'TEXT', 'constraints': 'NOT NULL PRIMARY KEY'},
		{'field': 'term', 'dtype': str, 'type': 'TEXT', 'constraints': ''}],
	'thesaurus_brinkmantrefwoorden': [
		{'field': 'identifier', 'dtype': str, 'type': 'TEXT', 'constraints': 'PRIMARY KEY NOT NULL'},
		{'field': 'term', 'dtype': str, 'type': 'TEXT', 'constraints': ''},
		{'field': 'brinkman_kind_id', 'dtype': pd.Int64Dtype(), 'type': 'NUMERIC',
		 'constraints': 'NOT NULL'}],
	'thesaurus_brinkman_kinds': [
		{'field': 'brinkman_kind_id', 'dtype': pd.Int64Dtype(), 'type': 'NUMERIC',
		 'constraints': 'NOT NULL PRIMARY KEY'},
		{'field': 'brinkman_kind', 'dtype': str, 'type': 'TEXT', 'constraints': ''}]
	}


def import_csv(table_name, check_schema=True, postfix=''):
	"""Obtain dataframe from file ../data/clean_csv/<table_name>.csv, obeying the dtypes specified in the schema"""
	table_loc = os.path.join('data/clean_csv',table_name+postfix+'.csv')
	if check_schema:
		dtypes = {d['field']:d['dtype'] for d in schemata[table_name]}
	else:
		dtypes = {}
	df = pd.read_csv(table_loc, sep=';', dtype = dtypes)
	return df

def export_csv(table_name, df, check_schema=True, postfix=''):
	"""Export dataframe <df> to a csv file in ../data/clean_csv/<table_name>.csv """
	#if len(df)>0:
	table_loc = os.path.join('data/clean_csv',table_name+postfix+'.csv')
	if check_schema:
		dtypes = {d['field']: d['dtype'] for d in schemata[table_name]}
		try:
			df = df.astype(dtypes)
		except:
			print('Cannot export according to schema', table_name)
			print('Schema:',dtypes)
			print('DF:', df.dtypes)
	df.to_csv(table_loc, sep=';', index = False)

def create_table(table_name, schema, db = 'data/demosaurus.sqlite'):
	"""Create or replace database table following datatypes specified in the schema"""
	statement = "CREATE TABLE IF NOT EXISTS %s (" % table_name
	for i, column in enumerate(schema):
		if i>0: statement += ','
		statement += '\n\t%s %s %s' % (column['field'], column['type'], column['constraints'])
	statement += '\n);'

	with sqlite3.connect(db) as con:
		c = con.cursor()
		c.execute('DROP TABLE IF EXISTS %s;' % table_name)
		c.execute(statement)

def fill_table(table_name, db = '../data/demosaurus.sqlite', overwrite = True, postfix=''):
	""" Fill database table with records from file ../data/clean_csv/<table_name>.csv"""
	schema = get_schema(table_name)
	if table_name[:11] != 'publication': postfix = ''
	df = import_csv(table_name, check_schema=True, postfix=postfix)
	if overwrite:
		create_table(table_name, schema, db = db)
	with sqlite3.connect(db) as con:
		try:
			df.to_sql(name=table_name,con=con, if_exists=('append' if overwrite else 'replace'), index=False)
		except Exception as e:
			print('Try to export', table_name ,'to DB')
			print(e)

def get_schema(table_name):
	"""Specification of schemas ('dtype' for pandas and 'types'  for sqlite, and sqlite constraints)"""
	return schemata[table_name]


def main():
	fill_table('publication_basicinfo')

	for subject in ['brinkman','CBK_thema','CBK_genre','NUGI_genre','NUR_rubriek']:
		fill_table('publication_'+subject)
	for authorbit in ['author_NTA','author_isni','author_viaf','author_wikipedia','author_worldcat','wiki_preferred_languages', 'authorship_roles']:
		fill_table(authorbit)
	for bit in ['thesaurus_CBK_genres','thesaurus_brinkmantrefwoorden']:
		fill_table(bit)
	fill_table('authorship_ggc')
	fill_table('publication_datasplits')
	fill_table('publication_annotations')
	fill_table('publication_titlefeatures')
	fill_table('publication_contentfeatures')



if __name__ == "__main__":
	main()