import sqlite3
from pprint import pprint
from sklearn.feature_extraction.text import TfidfVectorizer
import ast
import pandas as pd
import csv

con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
cur = con.cursor()
#INHOUD = titel + samenvatting boek (annotatie met stempel analyitisch jeugd/volwassen en/of samenvatting uit samenvatting-inhoudsopgave)
cur.execute(
    "SELECT publication_basicinfo.ppn, titelvermelding_processed, annotatie_processed, si_processed FROM "
    "publication_basicinfo LEFT JOIN " 
    "(SELECT * FROM publication_annotatie WHERE kind = 'analytisch-jeugd' or kind = 'analytisch-volw' or kind = 'inhoud') as "
    "publication_annotatiee ON "
    "publication_annotatiee.publication_ppn = publication_basicinfo.ppn LEFT JOIN "  
    "`publication_samenvatting-inhoudsopgave` as psi ON psi.publication_ppn = publication_basicinfo.ppn")
texts = cur.fetchall()

all_content = []
tuple_content = []
for row in texts:
    ppn = row[0]
    inhoud = row[1]
    inhoud = ast.literal_eval(inhoud)
    #print(type(inhoud))
    inhoud = ' '.join(word for word in inhoud)
    #print(inhoud)
    #inhoud = inhoud.replace("[", "")
    #inhoud = inhoud.replace("]", "")
    if row[2] is not None:
        new_text = ast.literal_eval(row[2])
        #new_text = row[2].replace("[", ",")
        #new_text = new_text.replace("]", "")
        new_text = ' '.join(word for word in new_text)
        inhoud = inhoud + ' ' + new_text
        #print(inhoud)
    if row[3] is not None:
        new_text = ast.literal_eval(row[3])
        new_text = ' '.join(word for word in new_text)
        inhoud = inhoud + ' ' + new_text
        #print(inhoud)
    tuple_content.append((ppn, inhoud))
    all_content.append(inhoud)

#using tfidfvectorizer from sklearn for vectorization
tfidf_vectorizer=TfidfVectorizer(use_idf=True)
tfidf_vectorizer_vectors=tfidf_vectorizer.fit_transform(all_content)
#for getting word associated with the number in the matrix
reverse_mapping = {}
for k, v in tfidf_vectorizer.vocabulary_.items():
    reverse_mapping[v] = k

#get sparse matrix representation in an iterable form
mtrz = tfidf_vectorizer_vectors.tocoo()
iterable_matrix = zip(mtrz.row, mtrz.col, mtrz.data)
print(len(iterable_matrix))
#Write results of the tf-idf vectorization to a csv output file
with open("tfidf.csv", "w") as tfidfcsv:
    fieldnames = ['ppn', 'word', 'tf_idf' ]
    writer = csv.DictWriter(tfidfcsv, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    for i in iterable_matrix:
        ppn = tuple_content[i[0]][0]
        word = reverse_mapping.get(i[1])
        tf_idf_score = i[2]
        writer.writerow({'ppn': ppn, 'word': word, 'tf_idf': tf_idf_score})
 #   print(i)
#first_vector_tfidfvectorizer = tfidf_vectorizer_vectors[0]


# GET TD-IDF VALUES OF A PARTICULAR PUBLICATION AS A DENSE MATRIX
#
#df = pd.DataFrame(tfidf_vectorizer_vectors[0].T.todense(), index=tfidf_vectorizer.get_feature_names(), columns=['tf-idf'])
#print(df.sort_values(by=["tf-idf"],ascending=False))
