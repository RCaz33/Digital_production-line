from fastapi import FastAPI,  Depends, HTTPException, status, Response
import pandas as pd
from app.utils import *
from app.utils_pipe import *
from datetime import datetime

app = FastAPI()
# Monitoring API avec prometheus
from prometheus_fastapi_instrumentator import Instrumentator, metrics
instrumentator = Instrumentator().instrument(app).expose(app)

# custom metrics to evaluate the performance of the API
from prometheus_client import Counter, Histogram, Gauge
REQUEST_KEY_COUNT = Counter('my_app_requests_total', 'Total number of requests')
REQUEST_NEW_MODEL = Counter('my_app_requests_new_model', 'Total number of requests for new model')
REQUEST_LATENCY_PREDS = Histogram('my_app_request_latency_seconds_preds', 'Request latency in seconds')
REQUEST_LATENCY_NEW_MODEL = Histogram('my_app_request_latency_seconds_new_model', 'Request latency in seconds for getting groups')
REQUEST_LATENCY_FIG1 = Histogram('my_app_request_latency_seconds_fig1', 'Request latency in seconds for fig 1')
REQUEST_LATENCY_FIG2 = Histogram('my_app_request_latency_seconds_fig2', 'Request latency in seconds for fig 2')

##### Security token
from fastapi.security import APIKeyHeader
import json
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY_HEADER = APIKeyHeader(name="Supervized-API-Key")
valid_keys = os.getenv('API_SUPERVIZED_SECRET_KEYS')

def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    REQUEST_KEY_COUNT.inc()
    if api_key not in json.loads(valid_keys):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",)

@app.get("/info")
def info():
    return {"name":"API ML","version":"1.0.0"}

@app.post("/predict/{model_type}", dependencies=[Depends(verify_api_key)],response_model=Data_group_out)
def predict(model_type:str,data:Data_In):

    if model_type == "sgdreg":
        from sklearn.linear_model import SGDRegressor

    elif model_type == 'elasticnet':
        from sklearn.linear_model import ElasticNet

    import joblib


    preprocessor = joblib.load(f'app/data/ML_sup/preprocessor.pkl')
    model = joblib.load(f'app/data/ML_sup/{model_type}_model.pkl')
    # prepare data
    X_clean = clean_data(pd.Series(data.model_dump()))
    X_transfo = preprocessor.transform(pd.DataFrame(X_clean).T)
    df_transfo = pd.DataFrame(X_transfo,columns=preprocessor.get_feature_names_out())
    print("transformed", X_transfo.shape)

    col_names = [a.replace('__','_') for a in preprocessor.get_feature_names_out()]
    # predict
    with REQUEST_LATENCY_PREDS.time():
        pred = model.predict(df_transfo)

    # ajout dans BDD ML
    date = datetime.now().isoformat()
    data = {"Prediction_date": date,  # AJOUTER DATE AUJ
            "Prediction_type": "OGD_conc",
            "Prediction_model_version": "string",
            "Prediction_data": {"sample":data.Batch_OGD_name,
                                "pred":float(pred[0]),
                                "reel":0}}


    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    response = requests.post(url='http://127.0.0.1:8000/Predictions/', headers=headers, data=json.dumps(data))  
    if response.status_code != 200:
        raise "Problem updating predictions tables in database"
    
    return {"pred":pred}

@app.get("/variable_importance", dependencies=[Depends(verify_api_key)])
def variable_importance(model_type : str ='elasticnet'):

    model = load_pickle('app/data/ML_sup/elasticnet_model.pkl')
    preprocessor = load_pickle('app/data/ML_sup/preprocessor.pkl')
    variable_importance = ({a:b for a,b in zip(preprocessor.get_feature_names_out()[model.coef_>0],model.coef_[model.coef_>0])})
    df = pd.DataFrame(variable_importance, index=[0])

    # Generate plot
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(y=df.columns,width=df.values[0])
    ax.set_title('feature importance')

    # Save plot to a BytesIO buffer
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_feat_import = base64.b64encode(img.getvalue()).decode('utf-8')

    return Response(img_feat_import)






@app.get("/restart_training_regression", dependencies=[Depends(verify_api_key)])
def restart_training_regression(where_to_log:str='local'):
    from app.utils_regr import log_best_elastic_net_model

    REQUEST_NEW_MODEL.inc()
    # shape, path = collect_data() # save updated data in folder data with date
    # print(10*"\ns")
    # print(shape,path)
    # shape, path = collect_data(dataset='analyses')
    # print(shape,path)
    try:
        with REQUEST_LATENCY_NEW_MODEL.time():
            model = log_best_elastic_net_model(where_to_log=where_to_log,algo_type='elasticnet')

        return {"training status":"success"}
    except:
        return{"training status":"failed"}



@app.get("/get_fig_uv")
def get_fig_uv():
    with REQUEST_LATENCY_FIG1.time():
        img_UV, img_RAMAN = make_chart_for_dash_produits()
        print(img_UV)
    return Response(img_UV)

@app.get("/get_fig_raman")
def get_fig_uv():
    with REQUEST_LATENCY_FIG1.time():
        img_UV, img_RAMAN = make_chart_for_dash_produits()
    return Response(img_RAMAN)



if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app,host="0.0.0.0", port=1001)


### TEST API


# {
#   "Batch_OGD_name": "2301A",
#   "Batch_OGD_date": "2023-01-04",
#   "Batch_OGD_Technicien": "IT",
#   "Batch_OGD_KC8_batch": "K01",
#   "Batch_OGD_KC8_masse": 5.0,
#   "Batch_OGD_THF_batch": "to_fill",
#   "Batch_OGD_THF_Volume": 500.0,
#   "Batch_OGD_Temperature": 0,
#   "Batch_OGD_Agitation": 230.0,
#   "Batch_OGD_heure_debut": "2023-01-04 11:00:00",
#   "Batch_OGD_heure_fin": "2023-01-10 00:00:00",
#   "Batch_OGD_room_HR": 34.3,
#   "Batch_OGD_room_T": 20.0,
#   "Batch_OGD_Stock": 0,
#   "Batch_OGD_Analyses": "1"
# }