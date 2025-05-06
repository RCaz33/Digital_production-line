


import os

def test_collect_data():
    from app.utils_pipe import collect_data
    shape, path = collect_data()
    assert shape[0] > 0
    assert os.path.exists(path)

def test_collect_data_abalyses():
    from app.utils_pipe import collect_data
    shape, path = collect_data(dataset='analyses')
    assert shape[0] > 0
    assert os.path.exists(path)

def test_run_optimisation():
    from app.utils_pipe import run_optimisation, collect_data
    shape, path = collect_data()
    shape, path = collect_data(dataset='analyses')
    _ = run_optimisation(path,'test',0.8,'pca')
    assert os.path.exists('app/data/ML_sup/model.pkl')
    assert os.path.exists('app/data/ML_sup/weights_UV.joblib')
    assert os.path.exists('app/data/ML_sup/weights_RAMAN.joblib')
    assert os.path.exists('app/data/ML_sup/sc_UV.joblib')
    assert os.path.exists('app/data/ML_sup/sc_RAMAN.joblib')
    assert os.path.exists('app/data/ML_sup/indicator_UV.joblib')
    assert os.path.exists('app/data/ML_sup/indicator_RAMAN.joblib')
    assert os.path.exists('app/data/ML_sup/pca_UV.joblib')
    assert os.path.exists('app/data/ML_sup/pca_RAMAN.joblib')
    assert os.path.exists('app/data/ML_sup/kmeans_UV.joblib')
    assert os.path.exists('app/data/ML_sup/kmeans_RAMAN.joblib')