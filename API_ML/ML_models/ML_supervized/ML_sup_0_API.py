from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import pandas as pd
import numpy as np
import joblib
import hdbscan
from sklearn.manifold import TSNE
import pickle
import mlflow

################ SHEMAS #################
from typing import Dict, List, Any
from pydantic import BaseModel

class Data_prod(BaseModel):
    date : str
    metadata : Dict[str,Any]
    uv_data : Dict[str,Any]
    raman_data :  Dict[str,Any]

class Data_transformed(BaseModel):
    group : int
    label_tsne : List
    coord_tsne : List


app = FastAPI()
# Define the API key header
API_KEY_HEADER = APIKeyHeader(name="Unsupervized-API-Key")
# Store valid API keys (in a real application, store these securely)
SECRET_KEY_UNSUPERVIZED=["1234567", "12345678"]

def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if api_key not in SECRET_KEY_UNSUPERVIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

@app.post("/predict_mlflow", dependencies=[Depends(verify_api_key)], response_model=Data_transformed)
async def predict_mlflow(request : Data_prod):
    """fonction qui instancie le modele depuis mlflow artifacts server
    """

    import mlflow.pyfunc

    model_name = "sk-learn-random-forest-reg-model"
    model_version = 1

    model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/{model_version}")

    model.predict(data)




if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app,host="0.0.0.1", port=1000)










