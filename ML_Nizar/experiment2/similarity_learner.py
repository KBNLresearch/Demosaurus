import numpy as np
import pandas as pd
from sklearn import datasets
import seaborn as sns
from sklearn.feature_selection import RFE
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import SGDRegressor
from sklearn.linear_model import BayesianRidge
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV
from sklearn.inspection import permutation_importance
from sklearn.metrics import classification_report, recall_score, confusion_matrix
from matplotlib import pyplot as plt


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

data = pd.read_csv('C:/Users/nizar/Downloads/final_ss_5to20.csv', sep = ';')
#data = data.drop('age_when_published', axis=1)
#data = data.filter(regex='inhoud|title|datasplit|target|ppn|age|last_name')
#data = data.drop(['autobiography_w2vsim', 'age_when_published', 'role_imp_similarity'], axis=1)
#data = data[['author_ppn', 'publication_ppn', 'datasplit', 'target', 'uitgever_agg_similarity', 'title_similarity', 'jaar_van_uitgave_similarity']]
print(data.isnull().any())
print(data.dtypes)
print(data.describe())

##FOR PLOTS
#data = data.drop(['author_ppn', 'publication_ppn', 'last_name'], axis = 1)
data.columns=data.columns.str.replace('_similarity','')
data.columns=data.columns.str.replace('sim','')
data.columns=data.columns.str.replace('_titelvermelding','')
data.columns=data.columns.str.replace('_in','')
data.columns=data.columns.str.replace('length_ranges','ranges_len_title')


correlation = data.corr(method='pearson')
columns = correlation.nlargest(25, 'target').index
print(type(columns))
plt.figure(figsize=(20, 15))
correlation_map = np.corrcoef(data[columns].values.T)
sns.set(font_scale=1.4)
heatmap = sns.heatmap(correlation_map, cbar=True, annot=True, square=True, fmt='.2f', yticklabels=columns.values, xticklabels=columns.values)

plt.show()
train_df = data[data['datasplit'] == 'train']
test_df = data[data['datasplit'] == 'test']
convert_to_classification = test_df[['author_ppn', 'publication_ppn']]

def create_specific_test_set(convert_to_classification, potential_authors):
    specific_test_set = convert_to_classification[convert_to_classification.groupby('publication_ppn')['publication_ppn'].transform('size') == potential_authors]
    return specific_test_set


print(test_df.info())
train_df = train_df[columns]
test_df = test_df[columns]
print(test_df.info())
#train_df = train_df.drop(['datasplit'], axis = 1)
#test_df = test_df.drop(['datasplit'], axis = 1)

X_train =  train_df.drop('target', axis = 1)
X_test = test_df.drop('target', axis = 1)
Y_train = train_df['target']
Y_test = test_df['target']
#

process_num_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='constant', fill_value=-1))])


def compare_models(X_train, Y_train):
    pipelines = []
    pipelines.append(('SGD', Pipeline([('imputer', SimpleImputer(strategy='median')),('Scaler', StandardScaler()),('SGDml',SGDRegressor())])))
    pipelines.append(('LR', Pipeline([('imputer', SimpleImputer(strategy='median')),('Scaler', StandardScaler()),('LRml',LinearRegression())])))
    pipelines.append(('LASSO', Pipeline([('imputer', SimpleImputer(strategy='median')),('Scaler', StandardScaler()),('LASSOml', Lasso())])))
    pipelines.append(('EN', Pipeline([('imputer', SimpleImputer(strategy='median')),('Scaler', StandardScaler()),('ENml', ElasticNet())])))
    pipelines.append(('LogR', Pipeline([('imputer', SimpleImputer(strategy='median')),('Scaler', StandardScaler()),('LogRml', LogisticRegression())])))
    pipelines.append(('BR', Pipeline([('imputer', SimpleImputer(strategy='median')),('Scaler', StandardScaler()),('BRml', BayesianRidge())])))
    pipelines.append(('KNN', Pipeline([('imputer', SimpleImputer(strategy='median')),('Scaler', StandardScaler()),('KNNml', KNeighborsRegressor())])))
    pipelines.append(('DT/CART', Pipeline([('imputer', SimpleImputer(strategy='median')),('Scaler', StandardScaler()),('CARTml', DecisionTreeRegressor())])))
    pipelines.append(('ADA', Pipeline([('imputer', SimpleImputer(strategy='median')),('Scaler', StandardScaler()),('ADAml', AdaBoostRegressor())])))
    pipelines.append(('GBM', Pipeline([('imputer', SimpleImputer(strategy='median')),('Scaler', StandardScaler()),('GBMml', GradientBoostingRegressor())])))

    results = []
    names = []
    for name, model in pipelines:
       kfold = KFold(n_splits=10, random_state=42, shuffle=True)
       cv_results = cross_val_score(model, X_train, Y_train, cv=kfold, scoring='r2')
       results.append(cv_results)
       names.append(name)
       msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
       print(msg)
    fig = plt.figure()
    fig.suptitle('Similarity learners comparison')
    ax = fig.add_subplot(111)
    plt.boxplot(results)
    ax.set_xticklabels(names)
    plt.show()

#compare_models(X_train, Y_train)


def hyperparameter_tuning(X_train, Y_train):#
     rescaledX = process_num_pipeline.fit_transform(X_train)
     param_grid = dict(n_estimators=np.array([50,100,200,300,400]))
     param_grid2 = {'max_depth':range(3,16,2), 'learning_rate':[0.001, 0.01, 0.05, 0.1, 0.2, 0.5],
                    'min_samples_split':range(5,100,15), 'min_samples_leaf':range(1,20,3),
                    'criterion':['friedman_mse', 'mse','mae'], 'max_features':['sqrt', 'auto', 'log2', None], 'subsample':[0.7, 0.9, 1, 1.2, 1.5]}
     model = GradientBoostingRegressor(random_state=21)
     kfold = KFold(n_splits=10, random_state=21)
     grid = GridSearchCV(estimator=model, param_grid=param_grid2, scoring='neg_mean_squared_error', cv=kfold)
     grid_result = grid.fit(rescaledX, Y_train)

     means = grid_result.cv_results_['mean_test_score']
     stds = grid_result.cv_results_['std_test_score']
     params = grid_result.cv_results_['params']
     for mean, stdev, param in zip(means, stds, params):
         print("%f (%f) with: %r" % (mean, stdev, param))

     print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))



from sklearn.metrics import mean_squared_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import r2_score

rescaled_X_train = process_num_pipeline.fit_transform(X_train)
model = GradientBoostingRegressor(n_estimators=1000)
model.fit(rescaled_X_train, Y_train)


rescaled_X_test = process_num_pipeline.fit(X_train).transform(X_test)
predictions = model.predict(rescaled_X_test)
print ("MSE", mean_squared_error(Y_test, predictions))
print ("EVR", explained_variance_score(Y_test, predictions))
print ("R2",  r2_score(Y_test, predictions))
#convert_to_classification = create_specific_test_set(convert_to_classification, 15)
pd.set_option('display.precision',10)
compare = pd.DataFrame({'Prediction': predictions, 'True' : Y_test})
result_concat = pd.concat([compare, convert_to_classification], axis=1)
#result = result.dropna()
#print(result_concat)
result_at_one = result_concat.set_index('author_ppn').groupby('publication_ppn').idxmax()
clf_rp = classification_report(result_at_one['True'], result_at_one['Prediction'])
print(clf_rp)
# cm = confusion_matrix(result_at_one['True'], result_at_one['Prediction'])
# import seaborn as sn
# df_cm = pd.DataFrame(cm, index = [i for i in range(1, 3332)],
#                   columns = [i for i in range(1, 3332)])
# plt.figure(figsize = (10,7))
# sn.heatmap(df_cm, annot=True)

def feature_importances():
    feature_importance = model.feature_importances_
    #print(feature_importance)
    sorted_idx = np.argsort(feature_importance)
    pos = np.arange(sorted_idx.shape[0]) + .5
    fig = plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.barh(pos, feature_importance[sorted_idx], align='center')
    plt.yticks(pos, np.array(X_test.columns)[sorted_idx], fontsize=24)
    plt.xticks(fontsize=24)
    plt.title('Relative Importance', fontsize=26)
    result = permutation_importance(model, rescaled_X_test, Y_test, n_repeats=10,
                                    random_state=42, n_jobs=2)
    sorted_idx = result.importances_mean.argsort()
    plt.subplot(1, 2, 2)
    plt.boxplot(result.importances[sorted_idx].T,
                vert=False, labels=np.array(X_test.columns)[sorted_idx])
    plt.yticks(fontsize=24)
    plt.xticks(fontsize=24)
    plt.title("Permutation Importance (test set)", fontsize=26)
    fig.tight_layout()
    plt.show()

feature_importances()


def sorted_maximums(group, nlargest, upto=False):
    # get top k rated authors for
    largest_ids = group.nlargest(nlargest, "Prediction")["author_ppn"]
    index = ["pred_ID_rank_{}".format(i) for i in range(1, nlargest + 1)]

    # Drop data if we're only interested in the nlargest value
    #  and none of the IDs leading up to it
    if upto is False:
        largest_ids = largest_ids.iloc[nlargest - 1:]
        index = index[-1:]

    # get correct author_ppn
    true_val_max = group.at[group["True"].idxmax(), "author_ppn"]
    index += ["ID_true"]

    # Combine our ranked IDs based on prediction and our author_ppn
    data = [*largest_ids, true_val_max]
    return pd.Series(data, index=index)

#USE FOR OMITTING PUBLICATIONS
#result_concat = result_concat[result_concat.groupby('publication_ppn')['publication_ppn'].transform('size') > 10]


ranking = result_concat.groupby("publication_ppn").apply(sorted_maximums, nlargest= 10, upto=True).reset_index()
# pd.set_option('display.max_rows', 10)

def recall_at_k(k, ranking):
    recall_at_k = 0
    for i in range(1, k+1):
        recall_at_k += recall_score(ranking['ID_true'], ranking['pred_ID_rank_{}'.format(i)], average='weighted')
    return recall_at_k

# print(recall_at_k(5, ranking))
# print(recall_at_k(3, ranking))
# print(recall_at_k(1, ranking))
# print(recall_at_k(10, ranking))