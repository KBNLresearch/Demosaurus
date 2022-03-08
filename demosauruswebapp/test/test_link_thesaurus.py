import demosauruswebapp.demosaurus as demosaurus
from demosauruswebapp.demosaurus import link_thesaurus
import pandas as pd
from werkzeug.datastructures import MultiDict

instance_path = '/home/sara/Metadata/Thesaureren/Demosaurus/demosauruswebapp/instance'
# absolute path to dir where the instance (database, among other things) lives that you want to test against
app = demosaurus.create_app(instance_path=instance_path)


def test_candidates_with_features_query():
    cand_q, params = link_thesaurus.candidate_query(author_name='aa')
    q = link_thesaurus.candidates_with_features_query(candidates_query=cand_q)
    df = run_query(q, params)
    assert type(df) == pd.DataFrame


def test_candidate_query():
    print(app.instance_path)
    cand_q, params = link_thesaurus.candidate_query(author_name='aa')
    df = run_query(cand_q, params)
    assert type(df) == pd.DataFrame


def run_query(query, params={}):
    with app.app_context() as context:
        with link_thesaurus.get_db() as db:
            return pd.read_sql_query(query, params=params, con=db)


def test_similarity_features_query():
    cand_q, params = link_thesaurus.candidate_query(author_name='aa')
    features = ['CBK_genre', 'brinkman_vorm', 'brinkman_zaak', 'NUR_rubriek', 'NUGI_genre', 'jaar_van_uitgave']
    q = link_thesaurus.similarity_features_query(features=features, candidates_query=cand_q)
    df = run_query(q, params)
    assert type(df) == pd.DataFrame
    assert 'author_ppn' in df.dtypes.keys()
    assert 'knownPublications' in df.dtypes.keys()
    for feature in features:
        assert feature in df.dtypes.keys()


def test_obtain_candidates():
    features = ['CBK_genre', 'brinkman_vorm', 'brinkman_zaak', 'NUR_rubriek', 'NUGI_genre', 'jaar_van_uitgave']
    with app.app_context() as context:
        candidates, similarity_data = link_thesaurus.obtain_candidates(author_name='aa', features=features)
    for df in [candidates, similarity_data]:
        assert type(df) == pd.DataFrame
        assert 'author_ppn' in df.dtypes.keys()


def test_wrap_publication_info():
    request_args = MultiDict(
        [('contributor_name', 'Fabio  @Stassi'), ('contributor_role', 'aut'), ('publication_title', 'De @laatste dans'),
         ('publication_genres',
          '{"CBK_genre":[],"NUR_rubriek":[{"rank":"1","identifier":"302"}],"NUGI_genre":[],"brinkman_vorm":[{"rank":"1","identifier":"075629410","term":"romans en novellen ; vertaald"}]}'),
         ('publication_year', ' 2014'), ('extended_search', 'false'), ('_', '1643874874535')])
    wrapped_publication, features_to_obtain = link_thesaurus.wrap_publication_info(request_args)
    assert type(wrapped_publication) == pd.DataFrame
    assert wrapped_publication['this_publication'].sum() == len(
        wrapped_publication)  # every row should have a count of one
    for i in wrapped_publication.index:
        assert wrapped_publication.loc[[i]].isna().sum().sum() == (
                    len(wrapped_publication.columns) - 2)  # two columns (the relevant value and the counter) should be NaN
    assert "075629410" in wrapped_publication['brinkman_vorm'].values
    assert "302" in wrapped_publication['NUR_rubriek'].values

    # Assert features_to_obtain is a dict of dicts of list of strings
    for feature_kind in ['nominal', 'ordinal', 'textual']:
        assert feature_kind in features_to_obtain
        assert type(features_to_obtain[feature_kind]) == dict
        for feature, itemlist in features_to_obtain[feature_kind].items():
            assert type(feature) == str
            for item in itemlist:
                assert type(item) == str


def test_obtain_and_score_candidates():
    author_name = 'Liesbeth  @Dillo'
    request_args = MultiDict(
        [('contributor_name', 'Jan @Janssen'), ('contributor_role', 'aut'), ('publication_title', 'De @laatste dans'),
         ('publication_genres',
          '{"CBK_genre":[],"NUR_rubriek":[{"rank":"1","identifier":"302"}],"NUGI_genre":[],"brinkman_vorm":[{"rank":"1","identifier":"075629410","term":"romans en novellen ; vertaald"}]}'),
         ('publication_year', ' 2014'), ('extended_search', 'false'), ('_', '1643874874535')])
    wrapped_publication, features_to_obtain = link_thesaurus.wrap_publication_info(request_args)
    with app.app_context() as context:
        scored_candidates = link_thesaurus.obtain_and_score_candidates(author_name, wrapped_publication, features_to_obtain)
    assert type(scored_candidates) == pd.DataFrame

