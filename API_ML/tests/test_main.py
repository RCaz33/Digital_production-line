from app.main import app
import json
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi.testclient import TestClient
client = TestClient(app)

def test_predict():
    test_data = {
    "Batch_OGD_name": "2301A",
    "Batch_OGD_date": "2023-01-04",
    "Batch_OGD_Technicien": "IT",
    "Batch_OGD_KC8_batch": "K01",
    "Batch_OGD_KC8_masse": 5.0,
    "Batch_OGD_THF_batch": "to_fill",
    "Batch_OGD_THF_Volume": 500.0,
    "Batch_OGD_Temperature": 0,
    "Batch_OGD_Agitation": 230.0,
    "Batch_OGD_heure_debut": "2023-01-04 11:00:00",
    "Batch_OGD_heure_fin": "2023-01-10 00:00:00",
    "Batch_OGD_room_HR": 34.3,
    "Batch_OGD_room_T": 20.0,
    "Batch_OGD_Stock": 0,
    "Batch_OGD_Analyses": "1"
    }
    headers = {'Supervized-API-Key': os.getenv('API_SUPERVIZED_SECRET_KEY'),
               'Content-Type': 'application/json'}
    response = client.post("/predict/elasticnet",headers=headers,data=json.dumps(test_data))
    assert response.status_code ==200
    assert 'pred' in response.json()

def test_variable_importance():
    headers = {'Supervized-API-Key': os.getenv('API_SUPERVIZED_SECRET_KEY'),
               'Content-Type': 'application/json'}
    response = client.get("/variable_importance",headers=headers)
    assert response.status_code == 200


def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {"name":"API ML","version":"1.0.0"}
