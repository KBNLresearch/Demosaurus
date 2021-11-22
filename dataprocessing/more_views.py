import sqlite3
import pandas as pd
import os

def train_test_view(db = '../data/demosaurus.sqlite'):
	"""Create database views for train and test set of authorship_ggc table
	"""

	statements = []
	from_table = 'authorship_ggc'
	for split in ['train', 'test']:
		view_name = '_'.join([from_table, split])
		statement = "CREATE VIEW IF NOT EXISTS %s AS " % view_name
		statement += "\nSELECT %s.* FROM %s JOIN publication_datasplits WHERE datasplit LIKE\"%s\"" %(from_table, from_table, split)
		statements.append(statement)
	
#	print(statement)

	with sqlite3.connect(db) as con:
		c = con.cursor()
		for statement in statements:			
			c.execute(statement)	


def main():
	train_test_view()



if __name__ == "__main__":
	main()	   