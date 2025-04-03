from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
import pandas as pd
import json
import os
from dotenv import load_dotenv
load_dotenv()

client = TestClient(app)

from app.utils import get_maree_data, clean_data


def test_get_maree_data():   
    gde_marees = get_maree_data([2024])
    assert gde_marees.shape == (73,2)


def test_clean_data():
    data = {'Batch_XY_name': '2301A',
 'Batch_XY_date': '2023-01-04',
 'Batch_XY_Technicien': 'IT',
 'Batch_XY_XX_batch': 'K01',
 'Batch_XY_XX_masse': 5.0,
 'Batch_XY_THF_batch': 'to_fill',
 'Batch_XY_THF_Volume': 500.0,
 'Batch_XY_Temperature': 0.0,
 'Batch_XY_Agitation': 230.0,
 'Batch_XY_heure_debut': '2023-01-04 11:00:00',
 'Batch_XY_heure_fin': '2023-01-10 00:00:00',
 'Batch_XY_room_HR': 34.3,
 'Batch_XY_room_T': 20.0,
 'Batch_XY_Stock': 0.0,
 'Batch_XY_Analyses': 1}
    X_clean = clean_data(pd.Series(data))
    print(X_clean.shape)
    assert X_clean.shape == (12,)

    