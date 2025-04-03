# App fastAPI pour servir les modeles ML

Application qui permet entrainement et mise à disposition les modeles Ml:
Tracking avec ML-Flow, stockés local ou Azure blob


/app
    |-/data : modeles ML sauvegardés
    |-main.py : définition des routes
    |-utils_regr.py : entrainement regr supervisé
    |-utils_class.py : entrainement class supervisé
    |-utils_pipe : classification non supervisé
/ML-models
    |-xxx.py : scripts aggregation / nettoyage / train ml-flow
    |-xxx.ipynb : tests avant scripts
    |-/ML_supervised : scripts et analyses 
        | 0-4 : digitalized data
        | 6-8 : data in new db form
    |-/ML_unsupervized : scripts et analyses
        | h gfc         |-xxx.ipynb : tests avant scripts
        |-xxx.ipynb : tests avant scripts
        |-xxx.ipynb : tests avant scripts
        |-xxx.ipynb : tests avant scripts
        |-xxx.ipynb : tests avant scripts
        |-xxx.ipynb : tests avant scripts
        |-xxx.ipynb : tests avant scripts
        |-xxx.ipynb : tests avant scripts
vvv                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   c bbv vccxf
/tests : test des point de terminaison


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
    --> resulat classification données analytiques spectrales 2
