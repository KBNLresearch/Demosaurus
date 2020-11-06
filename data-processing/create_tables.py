import sqlite3
import pandas as pd
import os

def import_table(table_name, schema):
    table_loc = os.path.join('../data/clean_csv',table_name+'.csv')
    dtypes = {d['field']:d['dtype'] for d in schema}
    df = pd.read_csv(table_loc, sep=';', dtype = dtypes)
    return df

def create_table(table_name, schema):
	
	statement = "CREATE TABLE IF NOT EXISTS %s (" % table_name
	for i, column in enumerate(schema):
		if i>0: statement += ','
		statement += '\n\t%s %s %s' % (column['field'], column['type'], column['constraints'])
	statement += '\n);'


	with sqlite3.connect('../data/demosaurus.sqlite') as con:
		c = con.cursor()
		c.execute('DROP TABLE IF EXISTS %s;' % table_name)
		c.execute(statement)
	
def fill_table(table_name):
	schema = get_schema(table_name)
	print(table_name, schema)
	df = import_table(table_name, schema)
	create_table(table_name, schema)
	with sqlite3.connect('../data/demosaurus.sqlite') as con:
		df.to_sql(name=table_name,con=con, if_exists='append', index=False)



def csv_to_sql(table_name):
    with sqlite3.connect('../data/demosaurus.sqlite') as con:
        df.to_sql(name=table_name,con=con, if_exists='append', index=False)



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

	return schema

def main():
	#fill_table('publication_basicinfo')
	#fill_table('publication_titlefeatures')
	for subject in ['brinkman','CBK_thema','CBK_genre','NUGI_genre','NUR_rubriek']:
		fill_table('publication_'+subject)

if __name__ == "__main__":
    main()	   