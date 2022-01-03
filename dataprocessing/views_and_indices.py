import sqlite3
import csv_db

def train_test_views(dataset=''):
	"""Create database views for train and test set of authorship_ggc table
	"""
	statements = {}
	for split in ['train', 'test']:
		view_name = '_'.join(['publication_contributors', split, dataset])
		statement =  f"CREATE VIEW {view_name} AS ".format(view_name = view_name)
		statement += "\nSELECT t1.* FROM publication_contributors t1"
		statement += "\nJOIN publication_datasplits t2 ON t1.publication_ppn = t2.publication_ppn"
		statement += "\n JOIN datasplits ON datasplits.datasplit_id = t2.datasplit_id"
		statement += "\n JOIN datasets ON datasets.dataset_id = t2.dataset_id"
		statement += "\nWHERE datasplit LIKE \"{split}\"".format(split=split)
		statements[view_name] = statement
	return statements

def create_index(table, columns,db = '../data/demosaurus.sqlite'):
	"""General function for creating indices on specified table for specified columns
	"""
	statement = "CREATE INDEX IF NOT EXISTS %s" % '_'.join([table]+columns)
	statement += "\nON %s(%s)" % (table, ','.join(columns))

	with sqlite3.connect(db) as con:
		c = con.cursor()
		c.execute(statement)	

def set_fts5(db='../data/demosaurus.sqlite'):
	with sqlite3.connect(db) as con:
		# Create virtual author table for high-performance text search (obtain candidates)
		con.execute("DROP TABLE IF EXISTS `author_fts5`;")
		con.execute("CREATE VIRTUAL TABLE author_fts5 USING FTS5(author_ppn, searchkey, name, name_normalized, familyname);")
		con.execute("INSERT INTO author_fts5 SELECT author_ppn, searchkey, name, name_normalized, familyname FROM author_name_options ;")
	return

def author_view_for_feature(feature_name, specifications=[], suffix='', dataset = ''):
	"""Create statement for database view for feature_name (e.g. 'CBK_genre')
	   As a relation between author (author_ppn), feature_id and count(publications)
	   NB: only for training split of dataset
	"""
	view_name = 'author_' + feature_name + suffix + '_'+dataset
	table_name = 'publication_' + feature_name

	statement = f"CREATE VIEW {view_name} AS ".format(view_name=view_name)
	statement += "\nSELECT author_ppn, term_identifier, COUNT(t1.publication_ppn) AS nPublications "
	statement += "\nFROM publication_contributors_train_{dataset} t1".format(dataset=dataset)
	statement += "\nJOIN {table_name} t2 ON t2.publication_ppn = t1.publication_ppn".format(table_name=table_name)
	for table, _, _ in specifications:
		statement += "\nJOIN {table} ON {table}.identifier = t2.term_identifier".format(table=table)
	statement += "\nWHERE author_ppn IS NOT NULL"
	statement += "\nAND t2.term_identifier IS NOT NULL"
	for table, column, value in specifications:
		statement += "\nAND {table}.{column}={value}".format(table=table, column=column, value=value)
	statement += "\nGROUP BY author_ppn, term_identifier;"
	return (view_name, statement)

def author_views(dataset):
	statements = {}
	for feature in ['CBK_genre','NUGI_genre','NUR_rubriek']:
		view_name, statement = author_view_for_feature(feature, dataset=dataset)
		statements[view_name] = statement
	view_name, statement = author_view_for_feature('brinkman', specifications=[('thesaurus_brinkmantrefwoorden', 'brinkman_kind_id', 0)],
							suffix='_vorm', dataset=dataset)
	statements[view_name] = statement
	view_name, statement = author_view_for_feature('brinkman', specifications=[('thesaurus_brinkmantrefwoorden', 'brinkman_kind_id', 1)],
							suffix='_zaak', dataset=dataset)
	statements[view_name] = statement
	return statements

def create_views(db = '../data/demosaurus.sqlite'):
	statements = {}
	statements.update(train_test_views(dataset='NBD'))
	statements.update(author_views(dataset='NBD'))

	with sqlite3.connect(db) as con:
		c = con.cursor()
		for view_name, statement in statements.items():
			c.execute('DROP VIEW IF EXISTS %s;' % view_name)
			c.execute(statement)

def create_indices(db = '../data/demosaurus.sqlite'):

	for table_name in csv_db.schemata.keys():
		if 'publication_' in table_name:
			create_index(table_name, ['publication_ppn'], db=db)  # Common entry: look up by publication
		if 'author_' in table_name:
			create_index(table_name, ['author_ppn'], db=db)  # Common entry: look up by author
	create_index('publication_contributors', ['author_ppn'],
				 db=db)  # Common entry for authorship: look up publications by author
	set_fts5(db=db) # To speed-up retrieval of candidates
