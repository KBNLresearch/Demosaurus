import sqlite3
import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span
import matplotlib.pyplot as plt
from pandas import DataFrame
import pandas as pd
import networkx as nx
import numpy as np

con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
cur = con.cursor()
cur.execute(
    "SELECT foaf_name, uitgever_agg FROM publication_basicinfo INNER JOIN authorship_ggc ON "
    "publication_basicinfo.ppn = authorship_ggc.publication_ppn INNER JOIN NTA on NTA.ppn = authorship_ggc.ppn WHERE "
    "authorship_ggc.ppn in (SELECT ppn from authorship_ggc group by ppn having count(*) > 500) and "
    "publication_basicinfo.uitgever_agg in (SELECT uitgever_agg from publication_basicinfo group by uitgever_agg "
    "having count(*) > 1000)")
author_publishers = cur.fetchall()

df = DataFrame(author_publishers)
df.columns = ['name', 'uitgever_agg']

cur.execute(
    "SELECT foaf_name, uitgever_2_agg FROM publication_basicinfo INNER JOIN authorship_ggc ON "
    "publication_basicinfo.ppn = authorship_ggc.publication_ppn INNER JOIN NTA on NTA.ppn = authorship_ggc.ppn WHERE "
    "authorship_ggc.ppn in (SELECT ppn from authorship_ggc group by ppn having count(*) > 500) and "
    "publication_basicinfo.uitgever_agg in (SELECT uitgever_agg from publication_basicinfo group by uitgever_agg "
    "having count(*) > 1000) and uitgever_2_agg IS NOT NULL")
author_publishers2 = cur.fetchall()
df2 = DataFrame(author_publishers2)
df2.columns = ['name', 'uitgever_agg']



df3 = pd.concat([df, df2])

publisherrelation = 'work has been published by'

df3 = df3.groupby(df.columns.tolist()).size().reset_index().\
    rename(columns={0:'weight'})

relations = []
for i in range(len(df3)):
    relations.append(publisherrelation)
df3['Relationship'] = relations
#df3['weight'] = np.log(df3['weight'])
print(df3.sort_values(by=['weight']))
G=nx.from_pandas_edgelist(df3, "name", "uitgever_agg",
                          edge_attr=True, create_using=nx.MultiDiGraph())

edges,weights = zip(*nx.get_edge_attributes(G,'weight').items())

diff_colors = []
for node in G:
    if node in df3["name"].values:
        diff_colors.append("red")
    else: diff_colors.append("green")

plt.figure(figsize=(20,20))
pos = nx.spring_layout(G, k=1)
nx.draw(G, with_labels=True, edgelist=edges, edge_color=weights, node_shape='s', node_color=diff_colors, font_size=8, edge_cmap=plt.cm.YlOrRd, pos = pos, arrowstyle='fancy')
plt.show()