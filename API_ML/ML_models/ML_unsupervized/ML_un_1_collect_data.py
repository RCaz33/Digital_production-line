#  initialisation des dependences
import requests
import logging
import pandas as pd
import click
import pickle
import random
import datetime
import os
import joblib

# initialisation des connections externes
url = 'http://127.0.0.1:8000'
headers = {
'accept': 'application/json',
'Content-Type': 'application/json'}

# point de lancement
@click.command()
@click.option(
    "--dataset", prompt='Dataset type (XY/analyses):', default='XY',
    help="Collect data, can be 'OGG' or 'analyses'")
@click.option(
    "--random_seed", default=42,
    help="Rand seed to split dataset")

def collect_data(dataset : str = 'XY', split : float = 0.8, random_seed : int = 42):
    """
    Cette fonction permet de collecter les données depuis une base de données externe
    et de les sauvegarder dans un fichier
    """
   
    # regles logique pour l'extraction
    if dataset == 'XY':
        # gestion des exeptions / erreurs
        try:
            response = requests.get(f'{url}/{dataset}/', headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f" Cannot connect to database\nRequest failed: {e}")
        
        # traitement et sauvegarde pour entrainement ML 
        metadata = pd.DataFrame(response.json())

        date = datetime.datetime.now().strftime("%Y-%m-%d")
        os.makedirs(f'data/{date}', exist_ok=True)
        with open(f'data/{date}/XY_metadata.pkl', 'wb') as file: 
            pickle.dump(metadata, file) 
            print(f'Dataset XY saved in folder data/{date}')


    elif dataset == 'analyses':

        try:
            response = requests.get(f'{url}/analyses/', headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f" Cannot connect to database\nRequest failed: {e}")
        
        # sauvegarder
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        os.makedirs(f'data/{date}', exist_ok=True)

        data_UV = pd.DataFrame([pd.Series(a['Analyses_data'],name=a['Analyse_name']) for a in response.json() if a['Analyse_subname'] == 'UV'])
        with open(f'data/{date}/Analyse_uv.pkl', 'wb') as file: 
            pickle.dump(data_UV, file) 
            print(f'Dataset analyses UV saved as data/{date}/Analyse_uv.pkl')


        data_RAMAN = pd.DataFrame([pd.Series(a['Analyses_data'],name=a['Analyse_name']) for a in response.json() if a['Analyse_subname'] == 'RAMAN'])
        with open(f'data/{date}/Analyse_raman.pkl', 'wb') as file: 
            pickle.dump(data_RAMAN, file) 
            print(f'Dataset analyses RAMAN saved as data/{date}/Analyse_uv.pkl')


if __name__ == '__main__':
    collect_data()