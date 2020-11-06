import sqlite3
import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span
import matplotlib.pyplot as plt
from pandas import DataFrame
import pandas
import networkx as nx
import pprint
import numpy as np

from itertools import groupby
from operator import itemgetter
import collections

con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
cur = con.cursor()
cur.execute(
    "SELECT publication_basicinfo.ppn, foaf_name FROM publication_basicinfo INNER JOIN authorship_ggc ON "
    "publication_basicinfo.ppn = authorship_ggc.publication_ppn INNER JOIN NTA on NTA.ppn = authorship_ggc.ppn WHERE "
    "authorship_ggc.ppn in (SELECT ppn from authorship_ggc group by ppn having count(*) > 400) order by "
    "publication_basicinfo.ppn")
author_books = cur.fetchall()

publications = [(k, list(list(zip(*g))[1])) for k, g in groupby(author_books, itemgetter(0))]
all_collaborations = []
for row in publications:
    number_of_authors = len(row[1])
    if number_of_authors == 1:
        pass
    else:
        for i in row[1]:
            index = row[1].index(i)
            for author in range(number_of_authors):
                if author > index and index is not (number_of_authors-1):
                    all_collaborations.append((i, row[1][author]))

#pprint.pprint(len(all_collaborations))

flag = False
val = collections.Counter(all_collaborations)
uniqueList = list(set(all_collaborations))
collaborations_weighted = []
for i in uniqueList:
    i += (np.log(val[i]),)
    collaborations_weighted.append(i)

#print(len(collaborations_weighted))

df = DataFrame(collaborations_weighted)
df.columns = ['author1', 'author2', 'weight']


collaborationrelation = 'worked with'
relations = []
for i in range(len(df)):
    relations.append(collaborationrelation)

df['Relationship'] = relations
print(df.sort_values(by=['weight']))

G=nx.from_pandas_edgelist(df, 'author1', 'author2',
                          edge_attr=True, create_using=nx.DiGraph())

edges,weights = zip(*nx.get_edge_attributes(G,'weight').items())

plt.figure(figsize=(20,20))
pos = nx.spring_layout(G, k=5)
nx.draw(G, with_labels=True, edgelist=edges, edge_color=weights, node_color='red', node_size=400, font_size = 8,  width=2.0, edge_cmap=plt.cm.Blues, pos = pos, arrowstyle='fancy')
plt.show()

#evt for fitting texts inside the box:
#bbox=dict(facecolor='skyblue', edgecolor='black',  boxstyle='round,pad=0.2')

