from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}




# in shcemas
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
class UV_spectra(BaseModel):
    data : Dict[str:Any]


# in main
import joblib
@app.get("/PCA_transform")
async def get_new_coodinates(data=UV_spectra):
    # call to api azure storage / $
    pca=joblib.load("../save_on_cloud_pca.joblib")


    return pca.transform()

# test.py




