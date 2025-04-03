from app.main import app
import json
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi.testclient import TestClient
client = TestClient(app)


def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {"name":"API ML","version":"1.0.0"}
    
# Mock data for testing
mock_data = {
    "Batch_XY_name": "2301A",
    "Batch_XY_date": "2023-01-04",
    "Batch_XY_Technicien": "IT",
    "Batch_XY_XX_batch": "K01",
    "Batch_XY_XX_masse": 5.0,
    "Batch_XY_THF_batch": "to_fill",
    "Batch_XY_THF_Volume": 500.0,
    "Batch_XY_Temperature": 0,
    "Batch_XY_Agitation": 230.0,
    "Batch_XY_heure_debut": "2023-01-04 11:00:00",
    "Batch_XY_heure_fin": "2023-01-10 00:00:00",
    "Batch_XY_room_HR": 34.3,
    "Batch_XY_room_T": 20.0,
    "Batch_XY_Stock": 0,
    "Batch_XY_Analyses": "1"
}

def test_predict_elasticnet():
    model_type = "elasticnet"
    
    headers = {
        "Supervized-API-Key":  os.getenv('API_SUPERVIZED_SECRET_KEY'), 
        "Content-Type": "application/json"
    }
    
    response = client.post(f"/predict/{model_type}", headers=headers, json=mock_data)
    
    assert response.status_code == 200
    response_data = response.json()
    assert "pred" in response_data 



def test_variable_importance():
    headers = {'Supervized-API-Key': os.getenv('API_SUPERVIZED_SECRET_KEY'),
               'Content-Type': 'application/json'}
    response = client.get("/variable_importance",headers=headers)
    assert response.status_code == 200
    assert response.json() != {}



# def test_restart_training_regression():
#     headers = {'Supervized-API-Key': os.getenv('API_SUPERVIZED_SECRET_KEY'),
#                'Content-Type': 'application/json'}
#     response = client.get("/restart_training_regression",headers=headers)
#     assert response.status_code == 200
#     assert response.json() != {}


