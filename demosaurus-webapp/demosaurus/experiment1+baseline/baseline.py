import sqlite3
from sklearn import svm
from sklearn import datasets
from pprint import pprint
import pandas as pd
from sklearn.metrics import classification_report

def get_data():
    con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
    cur = con.cursor()
    #INHOUD = titel + samenvatting boek (annotatie met stempel analyitisch jeugd/volwassen en/of samenvatting uit samenvatting-inhoudsopgave)
    getdatabase = cur.execute(
        "SELECT authorship_ggc.ppn as ppn, publication_basicinfo.ppn as p_ppn,  "
        "skos_preflabel, foaf_familyname FROM authorship_ggc "
        "INNER JOIN NTA ON "
        "NTA.ppn = authorship_ggc.ppn INNER JOIN "  
        "`publication_basicinfo` ON authorship_ggc.publication_ppn = publication_basicinfo.ppn WHERE kind = 'primair' AND "
        "authorship_ggc.ppn in (SELECT ppn from authorship_ggc group by ppn having count(*) > 1) AND foaf_familyname "
        "in (SELECT foaf_familyname from (SELECT foaf_familyname, authorship_ggc.ppn FROM NTA INNER JOIN "
        "authorship_ggc on NTA.ppn = authorship_ggc.ppn group by foaf_familyname, authorship_ggc.ppn having count(*) "
        "> 1) group by foaf_familyname having count(*) > 1)")

    cols = [column[0] for column in getdatabase.description]
    results= pd.DataFrame.from_records(data = getdatabase.fetchall(), columns = cols)
    results['replacenull'] = ''
    results.loc[results.replacenull == '', 'replacenull'] = results.skos_preflabel.str.split().str.get(0).str.replace(',', '')
    results["foaf_familyname"] = results["foaf_familyname"].fillna(results["replacenull"])
    results.drop('skos_preflabel', axis=1)
    results2 = results[results.groupby('foaf_familyname').ppn.transform('count') > 1]
    return results2


print(get_data())

def predict_simple(df):
    #predict author for a given name based on the ppn for that name that has the most publications linked
    df['prediction'] = df.groupby('foaf_familyname').ppn.transform(lambda x : x.mode().iloc[0])
    return classification_report(df['ppn'], df['prediction'])

def predict_simple2(df):
    #predict author based on the first returned result
    df['prediction'] = ""
    df_b = df.groupby('foaf_familyname').first().reset_index()
    df_b.rename(columns={'ppn': 'prediction'})
    dict_pred = pd.Series(df_b.ppn.values,index=df_b.foaf_familyname).to_dict()
    #print(dict_pred)
    df['prediction'] = df['foaf_familyname'].map(dict_pred)
    #print(df.loc[df['foaf_familyname'] == 'Tromp'])
    return classification_report(df['ppn'], df['prediction'])
   # return classification_report(df['ppn'], df['prediction'])


pprint(predict_simple(get_data()))
pprint(predict_simple2(get_data()))