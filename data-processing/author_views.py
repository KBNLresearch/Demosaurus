import sqlite3
import pandas as pd
import os

def create_view_for_feature(feature_name, in_basicinfo = False,db = '../data/demosaurus.sqlite'):
	"""Create or replace database view for feature_name (e.g. 'CBK_genre'
	   As a relation between author (author_ppn), feature_id and count(publications)
	   NB: only for training split of dataset
	"""
	view_name = 'author_'+feature_name+'s'
	column_name = feature_name
	if in_basicinfo:
		table_name = 'publication_basicinfo'
	else: 
		table_name = 'publication_'+feature_name

	#statement = "CREATE VIEW IF NOT EXISTS %s AS " % view_name
	statement = "CREATE VIEW %s AS " % view_name
	statement += "\nSELECT author_ppn, %s, COUNT(authorship_ggc.publication_ppn) AS nPublications " % column_name
	statement += "\nFROM authorship_ggc"
	statement += "\nJOIN publication_datasplits ON publication_datasplits.publication_ppn = authorship_ggc.publication_ppn"
	statement += "\nJOIN %s AS tt ON tt.publication_ppn = authorship_ggc.publication_ppn" % table_name
	statement += "\nWHERE publication_datasplits.datasplit like \"train\""
	statement += "\nAND author_ppn IS NOT NULL"
	statement += "\nAND %s IS NOT NULL" % column_name
	statement += "\nGROUP BY author_ppn, %s;" % column_name

#	print(statement)

	with sqlite3.connect(db) as con:
		c = con.cursor()
		c.execute('DROP VIEW IF EXISTS %s;' % view_name)
		c.execute(statement)	


def set_fts5(db = '../data/demosaurus.sqlite'):
    with sqlite3.connect(db) as con:
		print('Creating virtual table with FTS5..')
		# Create virtual author table for high-performance text search (obtain candidates)
		con.execute("DROP TABLE IF EXISTS `author_fts5`;")
		con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS author_fts5 USING FTS5(author_ppn, foaf_name);")
		con.execute("INSERT INTO author_fts5 SELECT author_ppn, foaf_name FROM author_NTA ;")
		print('Done. ')
    return

def main():
	for feature in ['CBK_genre','CBK_thema','NUGI_genre','NUR_rubriek', 'brinkman']:
		create_view_for_feature(feature, False)
	for feature in ['jaar_van_uitgave']:
		create_view_for_feature(feature, True)



if __name__ == "__main__":
	main()	   