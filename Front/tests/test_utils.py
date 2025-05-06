from app.utils import predict_XY_concentration
import datetime
from unittest.mock import patch, Mock
import pandas as pd
import json
import os
from dotenv import load_dotenv
load_dotenv()


def test_predict_XY_concentration():
    # prepare fake data
    data = {'Batch_XY_name': 'XY2512', 'Batch_XY_date': '2025-03-17T00:00:00', 'Batch_XY_Technicien': 'FB', 'Batch_XY_XX_batch': 'K2450', 'Batch_XY_XX_masse': '0', 'Batch_XY_YY_batch': 'fournisseur1', 'Batch_XY_YY_Volume': '30', 'Batch_XY_Temperature': '50', 'Batch_XY_Agitation': '250', 'Batch_XY_heure_debut': '2025-03-17T22:53:00', 'Batch_XY_heure_fin': None, 'Batch_XY_room_HR': '0.09', 'Batch_XY_room_T': '25', 'Batch_XY_Stock': None, 'Batch_XY_Analyses': 'None'}
    heure_debut =  datetime.datetime.fromisoformat(data['Batch_XY_heure_debut'])
    pred = predict_XY_concentration(data,heure_debut)

    # Expected response from the API
    expected_response = {'pred': pred[0]}

    # Mock the requests.post method
    with patch('requests.post') as mock_post:
        # Configure the mock to return a response with the expected JSON data
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_post.return_value = mock_response

        # Call the function
        result = predict_XY_concentration(data, heure_debut)

        # Prepare the expected data for the assertion
        expected_data = data.copy()
        expected_data['Batch_XY_heure_fin'] = (heure_debut + pd.DateOffset(days=6)).isoformat()
        expected_data['Batch_XY_Analyses'] = "1"
        expected_data['Batch_XY_Stock'] = 0

        # Assertions
        assert result == expected_response['pred']
        mock_post.assert_called_once_with(
            url="http://127.0.0.1:8003/predict/elasticnet",
            headers={
                'Supervized-API-Key': os.getenv('API_SUPERVIZED_SECRET_KEY'),
                'Content-Type': 'application/json'
            },
            data=json.dumps(expected_data)
        )
        

