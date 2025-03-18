



If server not started (NOT RECOMMENDED) 
    mlflow.set_experiment()
    mlflow.start_run() 
=> save files on current directory 'mlruns'
=> save model_info in current directory 'models'



With server Locally
mlflow server --host 127.0.0.1 --port 8080
    --> setting the uri:
    * --backend-store-uri file:relative_path
    * --backend-store-uri file:///path/absolute
    * --backend-store-uri sqlite:///ML_Flow_db.db
    * --backend-store-uri mysql+pymysql://{user}:{password}@localhost/{db}'
    --> setting default-artifact-root when using db


--backend-store-uri ==> **mlflow.set_tracking_uri()** (if not using Databricks)
    * mlflow.set_tracking_uri('file:relative_path')
    * mlflow.set_tracking_uri('sqlite:///ML_Flow_db.db')
    * mlflow.set_tracking_uri(uri="http://<host>:<port>")


WHEN using DB, MUST SET :
/!\ --default-artifact-root (pour les modele au lieu de /mlruns)
    --artifacts-destination (pour retrouver les articats)

/!\ avec un nouveau run, get_artifact_uri correspond au run

SI artifact root est Azure --> artifcat stored on azure

With server remote
mlflow server --backend-store-uri sqlite:///ML_FLow_db 
              --default-artifcat-root S3:/bucket_name
              --host remote_host 


Starting a server with AZURE