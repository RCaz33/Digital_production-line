# App fastAPI pour servir les modeles ML

Application qui permet entrainement et mise à disposition les modeles Ml:
Tracking avec ML-Flow, stockés local ou Azure blob.
Les données sont aggrégées avec des script "click" disponible dans le dossier 'ML_models"



/!\ App Flask - page Materiaux
Pour que l'application fonctionne, le modele entrainé et le preprocessor fitté doivent etre disponible dans le dossier /app/data/ML_sup. Pour cela, lancer les script python du dossier app/ML_models/ML_supervized :
- ML_sup_1_Collect_digitalized_data.py [--> <date>_data_production.csv]
- ML_sup_6_Send_raw_data_to_new_db.py [--> new_data.csv]
**IMPORTANT: DEMARRER UN SERVEUR MLFLOW**
- ML_sup_7_Test_models.py [--> new_X.csv y.csv]
- ML_sup_8_Tune_model_and_log.py [--> model to copy to app/data/ML_sup]
**IMPORTANT: RENOMMER model.pkl==>elasticnet_model.pkl ET <date>_preprocessor.pkl==>preprocessor.pkl**

**GITHUB ACTION REGARDE CE DOSSIER ET RECOMPOSE L'IMAGE DOCKER APRES MISE A JOUR DE FICHIERS**

/!\ App Flask - page Produits
Pour que les propriete de batch soient visibles, le modele kmeans entrainé doit etre disponible dans le dossier app/data. Pour cela, lancer les script python du dossier app/ML_models/ML_unsupervized :
ATTENTION, les données de caractérisation doivent etre disponible dans la table Analyses de la BDD (pour démo utiliser les script de /Z_1_populate_db.ipynb)


* **/app**
*    |---/data : modeles ML sauvegardés
*    |---main.py : définition des routes
*    |---utils_regr.py : entrainement regr supervisé
*    |---utils_class.py : entrainement class supervisé
*    |---utils_pipe : classification non supervisé
* **/ML-models** [Librairies : os, dotenv, click, logging, pandas, mysql.connector, datetime,
                                            pickle, json, requests, sklearn, mlflow, itertools]
*    |---xxx.py : scripts aggregation / nettoyage / train ml-flow
*    |---xxx.ipynb : tests avant scripts
*    |---/ML_supervised : scripts et analyses 
*    |---|--- 1-4 : 1-digitalize_data, 2-clean_data, 3-train_model, 4-log_model  
*    |---|--- 6-8 : 6-transfer_data, 7-train_model, 8_log_model
*    |---/ML_unsupervized : scripts et analyses
* **/tests** : test des point de terminaison

```
Les routes sont:
@app.get("/info") 
    --> pour vérifier santé app
@app.post("/predict/{model_type}", dependencies=[Depends(verify_api_key)],response_model=Data_group_out)  
    --> faire des prédictions en regression
@app.get("/variable_importance", dependencies=[Depends(verify_api_key)])
    --> analyser l'importance des paramètres du modele de regression
@app.get("/restart_training_regression", dependencies=[Depends(verify_api_key)])
    --> entrainer nouveau modele de regression
@app.get("/get_fig_uv")
    --> resulat classification données analytiques spectrales 1
@app.get("/get_fig_raman")
    --> resulat classification données analytiques spectrales 2```

