



* First get real OGD data from root/ML_supervized/Test_recup.ipynb and put them in cw_bdd_new

ML_sup_1 ==> Collect : connect to digitalized data and export as csv

ML_sup_1 ==> Send : Digitalized data to new DB

ML_sup_2 ==> clean dataset & API call to add grandes marées data and export as csv




* Second, generate analysis for those sample in root/populate_db.ipynb


ML_un_1 ==> connect to database and get all the data for OGD
            arg 'OGD' -> output metadata
            arg 'analyses' -> output 2 files, one for each analyses


ML_un_2 ==> Get metadata, split and encode columns
        ==> Get Spectral, get splits and reduce data to 10 components


ML_un_3 ==> Train hdbscan on different hyperparams (itertools.product)
        ==> create group and if groups > 1 : quantify clusturing with silhouette score on train and on validation data
        ==> get best model (silhouette score pour le train) and register it as slearn model


ML_un_4 ==> fetch best model with experiment name (identified by date)




MLFLOW:

Experiment 1 : search best params

Experiment 2 : save model








HOW TO TEST :


populate DB with fake data within 2020 - 2023

run ML_un_1
run ML_un_2
run ML_un_3
run ML_un_4


populate DB with fake data within 2024-2025

run ML_un_1 (will extract data)
run ML_un_2 ()
run ML_un_3
run ML_un_4


