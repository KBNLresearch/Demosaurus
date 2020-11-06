import pandas as pd
import sqlite3
import re
import nltk
import kpss_py3 as stemmer
from string import punctuation


def tokenize(text_field):
    return nltk.word_tokenize(text_field)

#Im using the most elaborate stopword list of Dutch words I could find, the one in NLTK is limited
def load_stopwords():
    stopwords = []
    stopwords_df = pd.read_csv('stopwordsDutch.txt', header=None)
    stopwords_df.columns = ['Words']
    result = [stopwords.append(x) for x in stopwords_df['Words']]
    return stopwords

def load_specialchars():
    return set(punctuation)

def stopword_removal(tokens):
    stopwords = load_stopwords()
    specialchars = load_specialchars()
    #@ seems to always be at the first word that is not een lidwoord (which gets removed anyways),
    #so I think it can be filtered out
    #specialchars.remove('@')
    cleaned_tokens = []
    for token in tokens:
        if token not in stopwords and token not in specialchars:
            cleaned_tokens.append(token)
    return cleaned_tokens

#using the Kraaij-Pohlmann stemmer (see import), which gives the best results from the stemmers I tried
def stem(tokens):
    stemmed_tokens = []
    for token in tokens:
        stemmed_tokens.append(stemmer.stem(token))
    return stemmed_tokens


def process_text(text, splitting=True, lowercase=True, token=True, stopword=True, stemming=True):
    # some special characters are glued to other words, specifying to split on those as well
    if splitting:
        text = re.split(r"[^a-zA-Z0-9\s]", text)
        text = ' '.join(word for word in text)
    ##bringing it all together
    if lowercase:
        text = text.lower()
    if token:
        text = tokenize(text)
    if stopword:
        text = stopword_removal(text)
    if stemming:
        text = stem(text)
    return text

def add_new_column(table, name):
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    try:
        addColumn = "ALTER TABLE " + str(table) + " ADD COLUMN " + str(name)
        cur.execute(addColumn)
    except:
        print("Column " + str(name) +  " already exists.")
    return(str(name))

#add_new_column("publication_basicinfo", "test")
#add_new_column("'publication_samenvatting-inhoudsopgave'", "'si_processed'")

def process_table(table, inputfeature, outputfeature):
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    cur.execute("SELECT publication_ppn, " + str(inputfeature) + " FROM " + str(table))
    rows = cur.fetchall()
    print(len(rows))
    insert_processed_text = "UPDATE " + str(table) + " SET " + str(outputfeature) + " = ? WHERE publication_ppn = ?"
    for row in rows:
        processed_text = process_text(str(row[1]))
        print(row[1])
        insert_data = (str((processed_text)), str(row[0]))
        cur.execute(insert_processed_text, insert_data)
        con.commit()
    con.close()


def process_table_with_no_unique_ppn(table, inputfeature, outputfeature):
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    cur.execute("SELECT publication_ppn, " + str(inputfeature) + " FROM " + str(table))
    rows = cur.fetchall()
    print(len(rows))
    insert_processed_text = "UPDATE " + str(table) + " SET " + str(outputfeature) + " = ? WHERE publication_ppn = ? AND annotatie = ?"
    i=0
    for row in rows:
        i = i + 1
        processed_text = process_text(str(row[1]))
        if i % 1000 == 0:
            print('nummer: ' + str(i) + ', annotatie: ' + str(row[1]))
        insert_data = (str((processed_text)), str(row[0]), str(row[1]))
        cur.execute(insert_processed_text, insert_data)
        con.commit()
    con.close()

def preprocess_publication_language():
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    insert_language_of_book = 'UPDATE publication_basicinfo SET "taal-origineel" = "taal-publicatie" WHERE "taal-origineel" IS NULL'
    cur.execute(insert_language_of_book)
    con.commit()
    con.close()

preprocess_publication_language()

#process_table("publication_basicinfo", "titelvermelding", "titelvermelding_processed")
#process_table("'publication_samenvatting-inhoudsopgave'", '"samenvatting-inhoudsopgave"', "si_processed")
#process_table_with_no_unique_ppn("publication_annotatie", "annotatie", "annotatie_processed")