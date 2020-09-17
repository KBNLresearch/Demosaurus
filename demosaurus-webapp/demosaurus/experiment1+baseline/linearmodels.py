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
from sklearn.linear_model import SGDClassifier, Perceptron
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
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis, LinearDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.svm import SVC
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.base import TransformerMixin, BaseEstimator
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.calibration import CalibratedClassifierCV
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import GridSearchCV
from sklearn import model_selection
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.model_selection import KFold



def get_data():
    con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
    cur = con.cursor()
    #INHOUD = titel + samenvatting boek (annotatie met stempel analyitisch jeugd/volwassen en/of samenvatting uit samenvatting-inhoudsopgave)
    getdatabase = cur.execute(
        "SELECT "
        "publication_basicinfo.publication_ppn as p_ppn, authorship_ggc.author_ppn as ppn, inhoud, taal_publicatie as "
        "t_p, taal_origineel as t_o, "
        "land_van_uitgave as lvu, jaar_van_uitgave as jvu, number_of_authors, NUR_rubriek as nrubriek, NUGI_genre as "
        "ngenre, "
        "number_of_words_in_titelvermelding, length_of_titelvermelding, "
        "themas, genres, foaf_familyname, uitgever_agg, mean_wordlength_titelvermelding as mean_words, "
        "median_wordlength_titelvermelding as median_words, length_titelvermelding_ranges as titel_ranges FROM publication_basicinfo "
        "INNER JOIN  "  
        "authorship_ggc ON authorship_ggc.publication_ppn = publication_basicinfo.publication_ppn INNER JOIN "
        "publication_inhoud "
        "on "
        "publication_inhoud.publication_ppn = publication_basicinfo.publication_ppn INNER JOIN author_NTA on "
        "author_NTA.author_ppn = authorship_ggc.author_ppn  LEFT JOIN "
        "publication_genrelist as cbkg on "
        "cbkg.publication_ppn = publication_basicinfo.publication_ppn LEFT JOIN publication_themalist as cbkt on "
        "cbkt.publication_ppn = publication_basicinfo.publication_ppn LEFT JOIN publication_NUR_rubriek as nurr on "
        "nurr.publication_ppn = publication_basicinfo.publication_ppn LEFT JOIN publication_NUGI_genre as nugig on "
        "nugig.publication_ppn = publication_basicinfo.publication_ppn WHERE kind = 'primair' AND "
        "authorship_ggc.author_ppn in (SELECT author_ppn from authorship_ggc group by author_ppn having count(*) >1) "
        "AND foaf_familyname "
        "in (SELECT foaf_familyname from (SELECT foaf_familyname, authorship_ggc.author_ppn FROM author_NTA INNER JOIN "
        "authorship_ggc on author_NTA.author_ppn = authorship_ggc.author_ppn group by "
        "foaf_familyname, authorship_ggc.author_ppn) group by foaf_familyname having count(*) BETWEEN 5 AND 20)")

    cols = [column[0] for column in getdatabase.description]
    results= pd.DataFrame.from_records(data = getdatabase.fetchall(), columns = cols)
    print(results.dtypes)
    print(results.describe())
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
#cat_feature = ['t_p', 't_o', 'lvu', 'nrubriek', 'ngenre', 'number_of_authors']
publisher_feature = ['uitgever_agg']
num_feature = ['jvu']
#layered_features = 'genres'
#layered_features2 = 'themas'
#pubklicationdata = ['t_p']




inhoud_transformer = Pipeline(steps=[('tfidf', TfidfVectorizer())])
categorical_transformer = Pipeline(steps=[('OHE', OneHotEncoder(handle_unknown = "ignore"))])
publisher_transformer = Pipeline(steps=[('OHE', OneHotEncoder(handle_unknown = "ignore"))])
numerical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())])
layered_features_transformer = Pipeline(steps=[('cvt', CountVectorizer(analyzer=set))])

preprocessor = ColumnTransformer(
 transformers=[
        ('text', inhoud_transformer, inhoud_feature), #TfidfVectorizer accepts column name only between quotes
       # ('category', categorical_transformer, cat_feature),
        ('publisher', publisher_transformer, publisher_feature),
        ('numerical', numerical_transformer, num_feature),
       # ('layeredcat', layered_features_transformer, layered_features),
      #  ('layeredcattwo', layered_features_transformer, layered_features2),
   ],
 )


classifier = Pipeline(
    steps = [
            ('preprocessor', preprocessor),
            #('feature_selection', SelectFromModel(LinearSVC(loss='l2', penalty='l1', dual=False))),
            ('clf', LinearSVC(max_iter=10000)),
    ],
)

X = results.drop('ppn', axis=1)
Y = results['ppn']

print(X.info())

X_train, X_test, y_train, y_test = train_test_split(X, Y,
                                                 random_state=0)

class DenseTransformer(TransformerMixin):

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, y=None, **fit_params):
        return X.todense()


seed = 42
# prepare models
models = []


def compare_models(X, Y):
    models.append(('NCC', Pipeline(
        steps = [
                ('preprocessor', preprocessor),
                ('clf', NearestCentroid()),
        ],
    )))


    models.append(('PC', Pipeline(
        steps = [
                ('preprocessor', preprocessor),
                ('clf', Perceptron()),
        ],
    )))


    models.append(('NB', Pipeline(
        steps = [
                ('preprocessor', preprocessor),
                ('clf', BernoulliNB(alpha=.001)),
        ],
    )))

    models.append(('SGD', Pipeline(
        steps = [
                ('preprocessor', preprocessor),
                ('clf', SGDClassifier(loss='modified_huber', max_iter=10000)),
        ],
    )))
    models.append(('KNN', Pipeline(
        steps = [
                ('preprocessor', preprocessor),
                ('clf', KNeighborsClassifier()),
        ],
    )))
    models.append(('SVM', Pipeline(
        steps = [
                ('preprocessor', preprocessor),
                ('clf', LinearSVC(max_iter=10000)),
        ],
    )))

    models.append(('LR', Pipeline(
        steps = [
                ('preprocessor', preprocessor),
                ('clf', SGDClassifier(loss='log', max_iter=10000)),
        ],
    )))

    models.append(('DT/CART', Pipeline(
        steps = [
                ('preprocessor', preprocessor),
                ('clf', DecisionTreeClassifier(max_depth=500)),
        ],
    )))


    models.append(('RF', Pipeline(
        steps = [
                ('preprocessor', preprocessor),
                ('clf', RandomForestClassifier(max_depth=500)),
        ],
    )))





    # evaluate each model in turn
    results = []
    names = []
    scoring = 'accuracy'
    for name, model in models:
        kfold = model_selection.KFold(n_splits=10, random_state=seed)
        cv_results = model_selection.cross_val_score(model, X, Y, cv=kfold, scoring=scoring)
        results.append(cv_results)
        names.append(name)
        msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
        print(msg)
    grad_boost = np.array([0.73, 0.72, 0.69, 0.75, 0.78, 0.79, 0.80, 0.74, 0.76, 0.74])
    names.append('GB')
    results.append(grad_boost)
    # boxplot algorithm comparison
    fig = plt.figure()
    fig.suptitle('Algorithm Comparison')
    ax = fig.add_subplot(111)
    plt.boxplot(results)
    ax.set_xticklabels(names)
    plt.show()

def hyperparameter_tuning(X_train, y_train):
    rescaledX = preprocessor.fit_transform(X_train)
    #param_grid = {'penalty':['l1', 'l2'], 'loss':['hinge', 'squared_hinge'], 'dual':[True, False]}
    #param_grid2 = {'max_iter':[100, 500, 1000, 5000, 10000, 50000, 100000]}
    #param_grid3 = {'C':[0.001, 0.01, 0.1, 0.25, 0.5, 1, 10, 25, 50, 100, 1000]}
    #param_grid4 = {'tol':[0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.1, 1], 'fit_intercept':[True, False]}
    param_grid5 = {'intercept_scaling':[0.001, 0.01, 0.1, 1, 10, 100]}

    model = LinearSVC(max_iter=10000)
    kfold = KFold(n_splits=10, random_state=21)
    grid = GridSearchCV(estimator=model, param_grid=param_grid5, scoring='f1_weighted', cv=kfold)
    grid_result = grid.fit(rescaledX, y_train)

    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    for mean, stdev, param in zip(means, stds, params):
        print("%f (%f) with: %r" % (mean, stdev, param))

    print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))

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