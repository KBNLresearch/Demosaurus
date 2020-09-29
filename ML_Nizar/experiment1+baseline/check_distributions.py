import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statistics

con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
cur = con.cursor()
getdatabase = cur.execute(
    "SELECT number_of_words_in_titelvermelding, length_of_titelvermelding, authorship_ggc.age_author_at_publication as age, `jaar-van-uitgave` as jvu  "
    "FROM publication_basicinfo INNER JOIN authorship_ggc ON "
    "publication_basicinfo.ppn = authorship_ggc.publication_ppn")
#numerical_data = cur.fetchall()

cols = [column[0] for column in getdatabase.description]
results = pd.DataFrame.from_records(data=getdatabase.fetchall(), columns=cols)
jvu = results['jvu'].to_list()
jvu_2 = [int(x) for x in jvu if "X" not in x]
age = results['age'].to_list()
age_2 = [int(x) for x in age if x is not None and int(x) < 200 and int(x) > 0]
results = results.drop('age', axis=1)
results = results.drop('jvu', axis=1)
print(statistics.median(age_2) )

f, axes = plt.subplots(2, 2, figsize=(20, 20))
for ax, feature in zip(axes.flat, results.columns):
    sns.distplot(results[feature], color="skyblue", bins=30, ax=ax)
print(type(age_2))
sns.distplot(age_2, color="skyblue", axlabel = 'age', ax = axes[1,0])
sns.distplot(jvu_2, color="skyblue", axlabel = 'jaar_van_uitgave', ax = axes[1,1])
plt.show()





