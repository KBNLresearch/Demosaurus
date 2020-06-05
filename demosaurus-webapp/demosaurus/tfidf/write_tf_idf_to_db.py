import csv, sqlite3

con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
cur = con.cursor()
cur.execute("CREATE TABLE publication_tfidf (ppn, word, tf_idf);")

with open('tfidf.csv','r') as publication_tfidf:
    dr = csv.DictReader(publication_tfidf, delimiter='\t')
    to_db = [(i['ppn'], i['word'] , i['tf_idf']) for i in dr]

cur.executemany("INSERT INTO publication_tfidf (ppn, word, tf_idf) VALUES (?, ?, ?);", to_db)
con.commit()
con.close()