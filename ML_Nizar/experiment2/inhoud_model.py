from gensim.summarization import keywords
import sqlite3
import pandas as pd
from pprint import pprint
import gensim
import numpy as np
import csv
import ast

### PART 1: MAKE AUTHOR EMBEDDINGS OF CONTENT BASED ON 75% OF DATA

def get_content_data():
    con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
    cur = con.cursor()
    # INHOUD = titel + samenvatting boek (annotatie met stempel analyitisch jeugd/volwassen en/of samenvatting uit samenvatting-inhoudsopgave)
    getdatabase = cur.execute("select author_ppn, inhoud, titelvermelding_processed, datasplit from publication_inhoud inner join authorship_ggc on publication_inhoud.publication_ppn = authorship_ggc.publication_ppn left join publication_sets on publication_inhoud.publication_ppn = publication_sets.publication_ppn left join publication_basicinfo on publication_basicinfo.publication_ppn = authorship_ggc.publication_ppn where datasplit='train'")
    data = getdatabase.fetchall()
    print(len(data))
    con.commit()
    return cur, data




def create_inhoud_embedding(contentfeature, data):
    embeddings = {}
    for row in data:
        a_ppn = row[0]
        if contentfeature == 'inhoud':
            feature_val = row[1]
        else:
            feature_val = row[2]
            feature_val = ast.literal_eval(feature_val)
        if feature_val == None:
            feature_val = ''
        if a_ppn is not None:
            if a_ppn in embeddings:
                embeddings[a_ppn].append(feature_val)
            else:
                embeddings[a_ppn] = [feature_val]
    return embeddings


from nltk.tokenize import word_tokenize, sent_tokenize

file_docs = []

def tokenize_input(embeddings):
    for key, value in embeddings.items():
        gen_docs = [[w.lower() for w in word_tokenize(text)]
                    for text in value]
        embeddings[key] = gen_docs
    return embeddings

cur, data = get_content_data()
embeddings_inhoud = tokenize_input(create_inhoud_embedding('inhoud', data))
embeddings_titel = create_inhoud_embedding('titelvermelding', data)


##PART 2: GET SIMILARITY TRAININGSDATA AS EARLIER MADE
similitary_data = cur.execute("select similarity_training.publication_ppn, author_ppn, inhoud, titelvermelding_processed from similarity_training left join publication_inhoud on publication_inhoud.publication_ppn = similarity_training.publication_ppn left join publication_basicinfo on publication_basicinfo.publication_ppn = similarity_training.publication_ppn")

def replace_empty_embeddings(file_docs):
    if not file_docs[0] and len(file_docs) == 1:
        print(author_ppn)
        print(publication_ppn)
        file_docs = [['inhoudzonderbetekenis']]
    return file_docs

def create_similarity_model(documents):
    dictionary = gensim.corpora.Dictionary(documents)
    corpus = [dictionary.doc2bow(gen_doc) for gen_doc in documents]
    tf_idf = gensim.models.TfidfModel(corpus)
    # for doc in tf_idf[corpus]:
    # print([[dictionary[id], np.around(freq, decimals=2)] for id, freq in doc])
    sims = gensim.similarities.Similarity('workdir/', tf_idf[corpus],
                                          num_features=len(dictionary))
    return dictionary, tf_idf, sims


with open('inhoud_similarity5to20.csv', mode='w', newline='') as inhoud_similarity:
    fieldnames = ['publication_ppn', 'author_ppn', 'inhoud_similarity', 'title_similarity']
    inhoud_writer = csv.DictWriter(inhoud_similarity, fieldnames=fieldnames, delimiter=';')
    inhoud_writer.writeheader()

    for publication_ppn, author_ppn, publication_inhoud, publication_title in similitary_data:
        file_docs = embeddings_inhoud[author_ppn]
        file_docs2 = embeddings_titel[author_ppn]
        file_docs = replace_empty_embeddings(file_docs)
        file_docs2 = replace_empty_embeddings(file_docs2)

        dictionary, tf_idf, similarity_model_inhoud = create_similarity_model(file_docs)
        dictionary2, tf_idf2, similarity_model_titel = create_similarity_model(file_docs2)

        try:
            query_doc = [w.lower() for w in word_tokenize(publication_inhoud)]
            query_doc_bow = dictionary.doc2bow(query_doc)
            query_doc_tf_idf = tf_idf[query_doc_bow]
            sum_of_sims = (np.sum(similarity_model_inhoud[query_doc_tf_idf], dtype=np.float32))
            avg_sim_inhoud = float(sum_of_sims / len(file_docs))

            title_tokens = ast.literal_eval(publication_title)
            query_doc_bow_title = dictionary2.doc2bow(title_tokens)
            query_doc_tf_idf_title = tf_idf2[query_doc_bow_title]
            sum_of_sims = (np.sum(similarity_model_titel[query_doc_tf_idf_title], dtype=np.float32))
            avg_sim_title = float(sum_of_sims / len(file_docs))

        except Exception as e:
            print(e)
            print(len(file_docs))
            print(author_ppn)
            print(publication_ppn)
            print(file_docs)

        inhoud_writer.writerow({'publication_ppn': publication_ppn, 'author_ppn': author_ppn, 'inhoud_similarity' : avg_sim_inhoud, 'title_similarity' : avg_sim_title})

