import pytest
import pandas as pd
from sklearn.linear_model import ElasticNetCV, SGDRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib
import os

# Mocking the necessary functions and classes
def mock_load_data(raw_data_path):
    # Create a mock dataset
    X = pd.DataFrame({
        'Batch_XY_Technicien': ['A', 'B'],
        'Batch_XY_XX_batch': ['X', 'Y'],
        'Batch_XY_Analyses': ['M', 'N'],
        'month_production': [1, 2],
        'day_production_start': [1, 2],
        'exfo_gde_maree': ['high', 'low'],
        'Batch_XY_Temperature': [25.0, 30.0],
        'Batch_XY_Agitation': [100, 150],
        'Batch_XY_room_HR': [50, 60],
        'conc_XX': [0.5, 0.6],
        'Batch_XY_room_T': [22.0, 23.0],
        'days_exfo': [5, 6]
    })
    y = pd.Series([1.0, 2.0], name='QC_Conc_XY')
    return X, y

def mock_set_preprocessor(X):
    categorical_columns = ['Batch_XY_Technicien', 'Batch_XY_XX_batch', 'Batch_XY_Analyses',
                           'month_production', 'day_production_start', 'exfo_gde_maree']
    numerical_columns = ['Batch_XY_Temperature', 'Batch_XY_Agitation', 'Batch_XY_room_HR',
                         'conc_XX', 'Batch_XY_room_T', 'days_exfo']
    preprocessor = ColumnTransformer(
        transformers=[
            ('numerical', StandardScaler(), numerical_columns),
            ('categorical', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), categorical_columns)
        ])
    preprocessor.fit(X)
    return preprocessor

def test_load_data():
    X, y = mock_load_data('mock_path')
    print(y.shape)
    assert X.shape == (2, 12), "Loaded X data has incorrect shape"
    assert y.shape == (2,), "Loaded y data has incorrect shape"

test_load_data()
def test_set_preprocessor():
    X, _ = mock_load_data('mock_path')
    preprocessor = mock_set_preprocessor(X)
    X_transformed = preprocessor.transform(X)
    assert X_transformed.shape[0] == X.shape[0], "Number of rows changed after preprocessing"
