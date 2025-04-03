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
    data = {'Batch_OGD_name': '2301A',
 'Batch_OGD_date': '2023-01-04',
 'Batch_OGD_Technicien': 'IT',
 'Batch_OGD_KC8_batch': 'K01',
 'Batch_OGD_KC8_masse': 5.0,
 'Batch_OGD_THF_batch': 'to_fill',
 'Batch_OGD_THF_Volume': 500.0,
 'Batch_OGD_Temperature': 0.0,
 'Batch_OGD_Agitation': 230.0,
 'Batch_OGD_heure_debut': '2023-01-04 11:00:00',
 'Batch_OGD_heure_fin': '2023-01-10 00:00:00',
 'Batch_OGD_room_HR': 34.3,
 'Batch_OGD_room_T': 20.0,
 'Batch_OGD_Stock': 0.0,
 'Batch_OGD_Analyses': 1}
    X_clean = clean_data(pd.Series(data))
    print(X_clean.shape)
    assert X_clean.shape == (12,)

    