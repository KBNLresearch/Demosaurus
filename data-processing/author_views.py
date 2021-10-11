import sqlite3
import pandas as pd
import os


def create_view_for_feature(feature_name, in_basicinfo=False, specifications=[], suffix='',
                            db='../data/demosaurus.sqlite'):
    """Create or replace database view for feature_name (e.g. 'CBK_genre'
       As a relation between author (author_ppn), feature_id and count(publications)
       NB: only for training split of dataset
    """
    view_name = 'author_' + feature_name + '_'+ suffix + '_count'
    column_name = feature_name
    if in_basicinfo:
        table_name = 'publication_basicinfo'
    else:
        table_name = 'publication_' + feature_name

    # statement = "CREATE VIEW IF NOT EXISTS %s AS " % view_name
    statement = "CREATE VIEW %s AS " % view_name
    statement += "\nSELECT author_ppn, %s, COUNT(authorship_ggc.publication_ppn) AS nPublications " % column_name
    statement += "\nFROM authorship_ggc"
    statement += "\nJOIN publication_datasplits ON publication_datasplits.publication_ppn = authorship_ggc.publication_ppn"
    statement += "\nJOIN %s AS tt ON tt.publication_ppn = authorship_ggc.publication_ppn" % table_name
    for table, _, _ in specifications:
        statement += "\nJOIN {table} ON {table}.ppn = tt.{column_name}".format(table=table,table_name=table_name,column_name=column_name)
    statement += "\nWHERE publication_datasplits.datasplit like \"train\""
    statement += "\nAND author_ppn IS NOT NULL"
    statement += "\nAND %s IS NOT NULL" % column_name
    for table, column, value in specifications:
        statement += "\nAND {table}.{column}={value}".format(table=table, column=column, value=value)
    statement += "\nGROUP BY author_ppn, %s;" % column_name

    #	print(statement)

    with sqlite3.connect(db) as con:
        c = con.cursor()
        c.execute('DROP VIEW IF EXISTS %s;' % view_name)
        c.execute(statement)


def set_fts5(db='../data/demosaurus.sqlite'):
    with sqlite3.connect(db) as con:
        print('Creating virtual table with FTS5..')
        # Create virtual author table for high-performance text search (obtain candidates)
        con.execute("DROP TABLE IF EXISTS `author_fts5`;")
        con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS author_fts5 USING FTS5(author_ppn, foaf_name);")
        con.execute("INSERT INTO author_fts5 SELECT author_ppn, foaf_name FROM author_NTA ;")
        print('Done. ')
    return


def main():
    # for feature in ['CBK_genre','CBK_thema','NUGI_genre','NUR_rubriek']:
    #		create_view_for_feature(feature, False)
    create_view_for_feature('brinkman', False, specifications=[('thesaurus_brinkmantrefwoorden', 'kind', '\"vorm\"')], suffix='vorm')
    create_view_for_feature('brinkman', False, specifications=[('thesaurus_brinkmantrefwoorden', 'kind', '\"zaak\"')], suffix='zaak')


#	for feature in ['jaar_van_uitgave']:
#		create_view_for_feature(feature, True)


if __name__ == "__main__":
    main()
