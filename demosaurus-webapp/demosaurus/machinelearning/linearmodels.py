import sqlite3
from sklearn import svm
from sklearn import datasets
from pprint import pprint
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import csv
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import FunctionTransformer
from sklearn.svm import LinearSVC
from sklearn.preprocessing import FunctionTransformer
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from matplotlib import pyplot as plt
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.base import TransformerMixin, BaseEstimator
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.calibration import CalibratedClassifierCV
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import GridSearchCV


def get_data():
    con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
    cur = con.cursor()
    #INHOUD = titel + samenvatting boek (annotatie met stempel analyitisch jeugd/volwassen en/of samenvatting uit samenvatting-inhoudsopgave)
    getdatabase = cur.execute(
        "SELECT "
        "  publication_basicinfo.ppn as p_ppn, authorship_ggc.ppn as ppn, inhoud, `taal-publicatie` as t_p, `taal-origineel` as t_o, "
        "`land-van-uitgave` as lvu, `jaar-van-uitgave` as jvu, number_of_authors, `NUR-rubriek` as nrubriek, `NUGI-genre` as ngenre, "
        "number_of_words_in_titelvermelding, length_of_titelvermelding, "
        "themas, genres, foaf_familyname, uitgever_agg FROM publication_basicinfo "
        "INNER JOIN  "  
        "`authorship_ggc` ON authorship_ggc.publication_ppn = publication_basicinfo.ppn INNER JOIN publication_inhoud "
        "on "
        "publication_inhoud.ppn = publication_basicinfo.ppn INNER JOIN NTA on NTA.ppn = authorship_ggc.ppn  LEFT JOIN "
        "ppn_genrelist as cbkg on "
        "cbkg.publication_ppn = publication_basicinfo.ppn LEFT JOIN ppn_themalist as cbkt on "
        "cbkt.publication_ppn = publication_basicinfo.ppn LEFT JOIN `publication_NUR-rubriek` as nurr on "
        "nurr.publication_ppn = publication_basicinfo.ppn LEFT JOIN `publication_NUGI-genre` as nugig on "
        "nugig.publication_ppn = publication_basicinfo.ppn WHERE kind = 'primair' AND "
        "authorship_ggc.ppn in (SELECT ppn from authorship_ggc group by ppn having count(*) >1) AND foaf_familyname "
        "in (SELECT foaf_familyname from (SELECT foaf_familyname, authorship_ggc.ppn FROM NTA INNER JOIN "
        "authorship_ggc on NTA.ppn = authorship_ggc.ppn where kind = 'primair' group by foaf_familyname, authorship_ggc.ppn having count(*) "
        "> 1) group by foaf_familyname having count(*) > 1)")

    cols = [column[0] for column in getdatabase.description]
    results= pd.DataFrame.from_records(data = getdatabase.fetchall(), columns = cols)
    results.themas.fillna(value="['onbekend']", inplace=True)
    results.foaf_familyname.fillna(value='onbekend', inplace=True)
    results.genres.fillna(value="['onbekend']", inplace=True)
    results.nrubriek.fillna(value='onbekend', inplace=True)
    results.ngenre.fillna(value='onbekend', inplace=True)
    results.genres = results.genres.apply(literal_eval)
    results.themas = results.themas.apply(literal_eval)
    results['jvu'] = results['jvu'].str.replace('XX', '50')
    results['jvu'] = results['jvu'].str.replace('X', '5')
    #mlb = MultiLabelBinarizer()
    #encoded = pd.DataFrame(mlb.fit_transform(results['genres']), columns=mlb.classes_, index=results.index)
    #results2 = pd.concat([results,encoded], axis=1)
    #encoded2 = pd.DataFrame(mlb.fit_transform(results2['themas']), columns=mlb.classes_, index=results2.index)
    #result = pd.concat([results2,encoded2], axis=1)
    #result["genres"] = pd.to_numeric(result["genres"])
    #result["themas"] = pd.to_numeric(result["themas"])
    #pd.options.display.max_columns= 15
    #cv = CountVectorizer(analyzer=set)
    #encoded = pd.DataFrame(cv.fit_transform(results['genres']), index=results.index)
    #print(cv.vocabulary_)
    #results2 = pd.concat([results,encoded], axis=1)
    return results


results = get_data()
print(results)

inhoud_feature = 'inhoud'
cat_feature = ['foaf_familyname', 't_p', 't_o', 'lvu', 'nrubriek', 'ngenre']
publisher_feature = ['uitgever_agg']
num_feature = ['number_of_words_in_titelvermelding', 'length_of_titelvermelding', 'number_of_authors', 'jvu']
layered_features = 'genres'
layered_features2 = 'themas'
#pubklicationdata = ['t_p']




inhoud_transformer = Pipeline(steps=[('tfidf', TfidfVectorizer())])
categorical_transformer = Pipeline(steps=[('OHE', OneHotEncoder(handle_unknown = "ignore"))])
publisher_transformer = Pipeline(steps=[('OHE', OneHotEncoder(handle_unknown = "ignore")),
                                        ('SVD', TruncatedSVD(n_components=1000))])
numerical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())])
layered_features_transformer = Pipeline(steps=[('cvt', CountVectorizer(analyzer=set))])

preprocessor = ColumnTransformer(
 transformers=[
        ('text', inhoud_transformer, inhoud_feature), #TfidfVectorizer accepts column name only between quotes
        ('category', categorical_transformer, cat_feature),
        ('publisher', publisher_transformer, publisher_feature),
        ('numerical', numerical_transformer, num_feature),
        ('layeredcat', layered_features_transformer, layered_features),
        ('layeredcattwo', layered_features_transformer, layered_features2),
   ],
 )


classifier = Pipeline(
    steps = [
            ('preprocessor', preprocessor),
            #('feature_selection', SelectFromModel(LinearSVC(loss='l2', penalty='l1', dual=False))),
            ('clf', SGDClassifier(loss='modified_huber', alpha=0.00009)),
    ],
)

X_train = results.drop('ppn', axis=1)
y_train = results['ppn']

print(X_train.info())

X_train, X_test, y_train, y_test = train_test_split(X_train, y_train,
                                                 random_state=0)


###GRIDSEARCH, nog doen

#param_grid = {
 #   'clf__loss': ['modified_huber'],
 #   'clf__penalty': ['elasticnet'],
  #  'clf__max_iter':(2000,),
  #  'clf__alpha': [10 ** x for x in range(-6, 1)],
  #  'clf__l1_ratio': [0, 0.05, 0.1, 0.2, 0.5, 0.8, 0.9, 0.95, 1],
#}

#grid_search = GridSearchCV(classifier, param_grid, n_jobs=-1, verbose=1)


def classification(X_train, X_test, y_train, y_test):
    classifier.fit(X_train, y_train)
    #svmclf = classifier.named_steps['clf']
    #print(classifier.named_steps['preprocessor'].transformers_[2][1].named_steps['scaler'].get_feature_names(num_feature))
    #print(classifier.info())
    y_pred_class = classifier.predict(X_test)
    return classification_report(y_test, y_pred_class)


def regression_ranking(X_train, X_test, y_train, y_test):
    classifier.fit(X_train, y_train)
    y_pred_class = classifier.predict_log_proba(X_test)
    preds_idx = np.argsort(y_pred_class, axis=1)[:,-10:]
    for i,d in enumerate(y_test):
        print(d + " =>")
        for p in preds_idx[i]:
            print(classifier.classes_[p],"(",y_pred_class [i][p],")")



report = classification(X_train, X_test, y_train, y_test)
pprint(report)