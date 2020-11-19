import pandas as pd
import numpy as np
import sqlite3
import random 
import re
import nltk
import csv
from unidecode import unidecode
import difflib
import os, sys
from collections import Counter
import pickle
from fuzzywuzzy import process


def export_table(table_name, df):
    assert len(df)>0    
    table_loc = os.path.join('../data/clean_csv',table_name+'.csv')
    df.to_csv(table_loc, sep=';', index = False)

def import_table(table_name, columns = []):
    table_loc = os.path.join('../data/clean_csv',table_name+'.csv')
    df = pd.read_csv(table_loc, sep=';')
    if len(columns)>0: 
        df = df[columns]
    return df

with open('stopwordsDutch.txt','r') as f:
    stopwords = [x.strip() for x in f.readlines()]
tokenizer = nltk.tokenize.WordPunctTokenizer()    

def process_text(text, utf= True, lowercase=True, tokenize=True, stopword=True, stemming=True, alphanumeric = True):
    if utf:
        text = unidecode(text)
    if lowercase: 
        text = text.lower()
    if tokenize:
        tokens = tokenizer.tokenize(text)
    if stopword:
        assert tokenize
        tokens = [token for token in tokens if token not in stopwords]
    if stemming:
        assert tokenize
        tokens = [stemmer.stem(token) for token in tokens]
    if alphanumeric:
        assert tokenize
        tokens = [token for token in tokens if token.isalnum()]
    return tokens if tokenize else text


def title_features():
    table = import_table('publication_basicinfo', ['publication_ppn', 'titel_verantwoordelijkheidsvermelding'])
    table.loc[:,'titelvermelding'] = table['titel_verantwoordelijkheidsvermelding'].apply(lambda x: x.split('/')[0])
    table.loc[:,'titellengte'] = table['titelvermelding'].apply(lambda x: len(x))
    bins_lengths = [0,5,10,15,20,25,30,35,40,45,50,60,70,80,90,100,150,250,1000]
    label_ranges = ['0_5', '6_10', '11_15', '16_20', '21_25', '26_30', '31_35', '36_40', '41_45', '46_50', '51_60',
               '61_70', '71_80', '81_90', '91_100', '101_150', '151_250', '251_1000']
    table.loc[:,'titellengte_ranges'] = pd.cut(table['titellengte'], bins=bins_lengths, right=True, labels=label_ranges)
    table.loc[:,'titelwoorden'] = table['titelvermelding'].apply(lambda x: process_text(x, stopword=False, stemming = False))
    table.loc[:,'titellengte_Nwoorden'] = table['titelwoorden'].apply(lambda x: len(x))
    table.loc[:,'woordlengte_gem'] = table['titelwoorden'].apply(lambda x: np.mean([len(w) for w in x]))
    table.loc[:,'woordlengte_gem_rond'] = table['woordlengte_gem'].apply(lambda x: round(x*2)/2)
    table.loc[:,'woordlengte_med'] = table['titelwoorden'].apply(lambda x: np.median([len(w) for w in x]))
    table.drop(columns = ['titel_verantwoordelijkheidsvermelding'], inplace = True)
    export_table('publication_titlefeatures', table)    

def content_features():
    content = ['title']


def main():
    title_features()
    content_features()


if __name__ == "__main__":
    main()