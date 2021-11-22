import sqlite3
import pandas as pd
import os

def train_test_view(db = '../data/demosaurus.sqlite'):
	"""Create database views for train and test set of authorship_ggc table
	"""
	statements = []
	from_table = 'authorship_ggc'
	match_column = 'publication_ppn'
	for split in ['train', 'test']:
		view_name = '_'.join([from_table, split])
		statement =  "CREATE VIEW IF NOT EXISTS %s AS " % view_name
		statement += "\nSELECT %s.* FROM %s JOIN publication_datasplits" %(from_table, from_table)
		statement += "\nON %s.%s = publication_datasplits.%s" %(from_table,match_column, match_column)
		statement += "\nWHERE datasplit LIKE\"%s\"" %split
		statements.append(statement)
	
	with sqlite3.connect(db) as con:
		c = con.cursor()
		for statement in statements:			
			c.execute(statement)	


def create_index(table, columns,db = '../data/demosaurus.sqlite'):
	"""General function for creating indices on specified table for specified columns
	"""
	statement = "CREATE INDEX IF NOT EXISTS %s" % '_'.join([table]+columns)
	statement += "\nON %s(%s)" % (table, ','.join(columns))

	with sqlite3.connect(db) as con:
		c = con.cursor()
		c.execute(statement)	


def main():
	train_test_view()
	create_index('authorship_ggc',['author_ppn']) # Common entry for authorship: look up publications by author
	create_index('authorship_ggc',['publication_ppn']) # Common entry for authorship: look up specific publication
	create_index('author_NTA',['foaf_name']) # To speed-up retrieval of candidates


if __name__ == "__main__":
	main()	   