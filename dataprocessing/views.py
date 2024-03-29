import sqlite3

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

def author_aggregated_query(ignore = []):
	feature_specs = {'CBK_genre':{},
					 'NUGI_genre':{},
					 'NUR_rubriek':{},
					 'brinkman_zaak':{'table_name':'publication_brinkman',
								 'specifications':[('thesaurus_brinkmantrefwoorden', 'brinkman_kind_id', 1)]},
					 'brinkman_vorm': {'table_name':'publication_brinkman',
								  'specifications': [('thesaurus_brinkmantrefwoorden', 'brinkman_kind_id', 0)]},
					 'jaar_van_uitgave': {'table_name':'publication_basicinfo', 'feature_column': 'jaar_van_uitgave'},
					 'role':{'table_name':'publication_contributors', 'feature_column':'role'}
					 }
	for feaure in ignore:
		del feature_specs[feaure]
	query = f"""WITH publication_subset AS(
			SELECT t0.publication_ppn, t0.author_ppn
			FROM publication_contributors_train_NBD t0
			WHERE t0.author_ppn IS NOT NULL)"""
	for i, (feature_name, specs) in enumerate(feature_specs.items()):
		if i>0: query += "\nUNION"
		table_name = specs['table_name'] if 'table_name' in specs else 'publication_'+feature_name
		feature_column = specs['feature_column'] if 'feature_column' in specs else 'term_identifier'
		suffix = specs['suffix'] if 'suffix' in specs else ''
		query += f"""
SELECT 
	t1.author_ppn, 
	t2.{feature_column} AS term, 						
	'{feature_name}{suffix}' AS term_description, 
	COUNT(t1.publication_ppn) AS knownPublications
FROM publication_subset t1
JOIN {table_name} t2 
	ON t2.publication_ppn = t1.publication_ppn 
	AND t2.{feature_column} IS NOT NULL"""
		if 'specifications' in specs:
			for table, column, value in specs['specifications']:
				query += f"\nJOIN {table} ON {table}.identifier = t2.term_identifier AND {table}.{column}={value}"
		query += f"\nGROUP BY t1.author_ppn, t2.{feature_column}"
	return query


def create_views(db = '../data/demosaurus.sqlite'):
	statements = {'author_aggregated':f'CREATE VIEW author_aggregated AS {author_aggregated_query()}'}
	#statements.update(train_test_views(dataset='NBD'))

	with sqlite3.connect(db) as con:
		c = con.cursor()
		for view_name, statement in statements.items():
			c.execute('DROP VIEW IF EXISTS %s;' % view_name)
			print(view_name, statement)
			c.execute(statement)

