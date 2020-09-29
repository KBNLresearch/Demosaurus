import sqlite3
import pandas as pd

with open('AT.sql', 'r') as sql_file:
    sql_script = sql_file.read()

con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
cur = con.cursor()
df = pd.read_sql(sql_script, con)

df.to_csv('Allresults.csv', index=False, sep=';')

counts = df['publication_ppn'].value_counts(sort=False)
df_filtered1 = df[df['publication_ppn'].isin(counts.index[(counts >= 5) & (counts <= 20)])]
df_filtered2 = df[df['publication_ppn'].isin(counts.index[(counts >= 5) & (counts <= 15)])]
df_filtered1.to_csv('Formodel520.csv', index=False, sep=';')
df_filtered2.to_csv('Formodel515.csv', index=False, sep=';')


## verkrijgen van een dataset met publicaties met alleen 2 auteurs (voor experiment)
data = pd.read_csv("Allresults.csv")
data = data[data.groupby('publication_ppn')['publication_ppn'].transform('size') == 2]
print(data)