


# 🧪 MLflow Troubleshooting Guide

## 🚫 If Server is *Not* Started (NOT RECOMMENDED FOR PRODUCTION)

```python
mlflow.set_experiment("my_experiment")
with mlflow.start_run():
    ...
```

* Artifacts (e.g., metrics, params) are saved in the local directory: ./mlruns

* Model files are saved in: ./mlruns/.../artifacts or ./models (depending on usage)

# ✅ Running MLflow Server Locally
```bash
mlflow server \
  --host 127.0.0.1 \
  --port 8080 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns
```

## 🔧 Options for --backend-store-uri

    file:relative_path → Relative local path

    file:///absolute/path → Absolute path

    sqlite:///mlflow.db → SQLite database

    mysql+pymysql://<user>:<password>@localhost/<db> → MySQL database

## 📍 Set Tracking URI in Code

```python
mlflow.set_tracking_uri("http://127.0.0.1:8080")
```

## ⚠️ Important Notes

    If using a database, you must set:

        ```bash
        --default-artifact-root → Where artifacts will be stored (e.g., ./mlruns, s3://..., or azure://...)
        ```

   * mlflow.get_artifact_uri() reflects the configured artifact location

   * If artifact root is on Azure or S3, artifacts will be stored accordingly

# 🌍 Running MLflow Server Remotely

```bash
mlflow server \
  --host <remote_host> \
  --port 8080 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root s3://bucket_name
```
## 📍 Set Tracking URI in Code
```python
mlflow.set_tracking_uri("http://<remote_host>:8080")
```

# ☁️ Running MLflow Server with Azure Blob Storage
```bash
mlflow server \
  --host 0.0.0.0 \
  --port 8080 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root wasbs://<container>@<account>.blob.core.windows.net/<path>
```

## 🔐 Required Azure Credentials

Make sure these environment variables are set:
```bash
export AZURE_STORAGE_ACCOUNT_NAME=<your_account>
export AZURE_STORAGE_ACCOUNT_KEY=<your_key>
```

## 📍 Set Tracking URI in Code


With server Locally
```bash
mlflow server --host 127.0.0.1 --port 8080
    --> setting the uri:
    * --backend-store-uri file:relative_path
    * --backend-store-uri file:///path/absolute
    * --backend-store-uri sqlite:///ML_Flow_db.db
    * --backend-store-uri mysql+pymysql://{user}:{password}@localhost/{db}'
    --> setting default-artifact-root when using db
```

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