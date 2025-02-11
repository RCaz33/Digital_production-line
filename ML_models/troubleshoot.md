# Simplon project ML_Flow (ALTERNANCE Semaine 09)


https://anaconda.org/sfe1ed40/azureml-mlflow

https://learn.microsoft.com/en-us/python/api/overview/azure/ml/?view=azure-ml-py


https://learn.microsoft.com/fr-fr/azure/machine-learning/concept-mlflow?view=azureml-api-2




#### celui ci est celui utilise en cours
https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-mlflow-configure-tracking?view=azureml-api-2&tabs=python%2Cmlflow


https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-mlflow-cli-runs?view=azureml-api-2&tabs=interactive%2Ccli



## Homework

The goal of this homework is to get familiar with MLflow, the tool for experiment tracking and
model management.


## Q1. Install MLflow

## Q2. Download and preprocess the data

The script will:

* load the data from the folder `<Data>` (the folder where you have created the data from ../test_ml.ipynb),
* fit a scaler and one hot encoder 
* save the preprocessed datasets and the scaler + one hot encoder to disk.

Use librairy click to pass argument for the script
```
python preprocess_data.py --raw_data_path <TAXI_DATA_FOLDER> --dest_path ./output
```

## Q3. Train a model with autolog (LOGGING EXPERIMENT in DATABASE-> tracking uri : Metadata (parameters, metrics, etc.))

We will train a `Kmeans` (from Scikit-Learn) on the dataset.

The script will:

* load the datasets produced by the previous step,
* train the model on the training set,
* assign groups on the test set,
* calculate the rand_score score on the cross-section of datasets.

The script enable **autologging** with MLflow, launch the MLflow UI / Azure ML workspace to check that the experiment run was properly tracked.


## Q4. Launch the tracking server locally (TRACKING MODELS in FOLDER/CLOUD --> artifact folder (models, files, etc.))


* launch the tracking server on your local machine,
* select a SQLite db for the backend store and a folder called `artifacts` for the artifacts store.

In addition to `backend-store-uri`, what else do you need to pass to properly configure the server?

* `default-artifact-root`
* `serve-artifacts`
* `artifacts-only`
* `artifacts-destination` --> path to store

mlflow server \
  --backend-store-uri mysql+pymysql://user:pass@host/mlflow_db \
  --default-artifact-root s3://mlflow-artifacts \
  --serve-artifacts
  
1. --backend-store-uri
        Local: sqlite:///path/to/db.sqlite
        Remote Databases: mysql+pymysql://user:password@host/dbname
        File-based: file:/path/to/mlruns (
2. --default-artifact-root
        Local path: file:/path/to/artifacts
        Cloud storage: s3://bucket-name/path, gs://bucket-name, azure://container-name

## Q6. Promote the best model to the model registry

The results from the hyperparameter optimization are quite good. So, we can assume that we are ready to test some of these models in production.
In this exercise, you'll promote the best model to the model registry. We have prepared a script called `register_model.py`, which will check the results from the previous step and select the top 5 runs.
After that, it will calculate the RMSE of those models on the test set (March 2023 data) and save the results to a new experiment called `random-forest-best-models`.

Your task is to update the script `register_model.py` so that it selects the model with the lowest RMSE on the test set and registers it to the model registry.

Tip 1: you can use the method `search_runs` from the `MlflowClient` to get the model with the lowest RMSE,

Tip 2: to register the model you can use the method `mlflow.register_model` and you will need to pass the right `model_uri` in the form of a string that looks like this: `"runs:/<RUN_ID>/model"`, and the name of the model (make sure to choose a good one!).

What is the test RMSE of the best model?

* 5.060
* 5.567
* 6.061
* 6.568

## Q7. Reproduce the same workflow as done in Scenario 3, but on Azure Cloud

Scenario 3 uses AWS to host the tracking server and the database used for the backend store, and s3 to store the artifacts. Try to do the same (set an experiment, start and log a run, register a model) but on Azure Cloud.

Tip 1: Azure Machine Learning provides a lot of resources and integrations with common tools like MLflow.

Tip 2: Maybe there is Azure documentation on the matter?



## Congratulations!
