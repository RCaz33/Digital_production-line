

## Running MLFLOW locally :
```mlflow server --host 127.0.0.1 
            --port 8080 
            --backend-store-uri file:store (auto ml_runs)         ** save info     
            --default-artifact-root file:artifacts                ** save models
            --serve-artifacts```
==> create folder store at the start of server
==> create folder artifcat only if registering model

in store there is :     -run_name/artifcats
                                /inputs
                                /metrics
                                /params
                                /tags
                        -models/model_name/version-1
                                          /version-2
in artifact there is:   -data/model ()model.pkl
                        -model (model.pkl)




## Running MLFlow in a database :
mlflow server --host 127.0.0.1 --port 8080 --backend-store-uri mysql+pymysql://{user}:{password}@localhost/{db}' --default-artifact-root file:artifacts_RC --serve-artifacts

mlflow server --host 127.0.0.1 --port 8080 --backend-store-uri sqlite:///ML_Flow_db.db --default-artifact-root file:artifacts_RC --serve-artifacts


## Running MLFlow for dev :
mlflow server --host 127.0.0.1 --port 8080 --backend-store-uri file:store_RC --default-artifact-root file:artifacts_RC --serve-artifacts

