import sqlite3
import csv_db

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

def create_indices(db = '../data/demosaurus.sqlite'):

	for table_name in csv_db.schemata.keys():
		if 'publication_' in table_name:
			create_index(table_name, ['publication_ppn'], db=db)  # Common entry: look up by publication
		if 'author_' in table_name:
			create_index(table_name, ['author_ppn'], db=db)  # Common entry: look up by author
	create_index('publication_contributors', ['author_ppn'],
				 db=db)  # Common entry for authorship: look up publications by author
	set_fts5(db=db) # To speed-up retrieval of candidates
