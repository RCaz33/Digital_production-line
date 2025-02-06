# initialisation des dependences
import requests
import logging
import pandas as pd
import click
import pickle


# initialisation des connections externes
url = 'http://127.0.0.1:8000'
headers = {
'accept': 'application/json',
'Content-Type': 'application/json'}

# point de lancement
@click.command()
@click.option(
    "--dataset",
    help="Collect data, can be OGG or analyses_UV"
)


def collect_data(dataset : str = 'OGD'):

    # regles logique pour l'extraction
    if dataset == 'OGD':
        # gestion des exeptions / erreurs
        try:
            response = requests.get(f'{url}/{dataset}/', headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f" Cannot connect to database\nRequest failed: {e}")
        
        # traitement des données
        metadata = pd.DataFrame(response.json())
        # sauvegarde pour entrainement ML
        with open('data/train.pkl', 'wb') as file: 
            pickle.dump(metadata.iloc[:120,2:], file) 
        with open("data/test.pkl", 'wb') as file: 
            pickle.dump(metadata.iloc[40:,2:], file) 

    elif dataset == 'UV':
        try:
            response = requests.get(f'{url}/analyses_UV/', headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f" Cannot connect to database\nRequest failed: {e}")

        
        data = pd.DataFrame([pd.Series(a['Analyses_UV_data'],name=a['Analyse_UV_name']) for a in response.json()])
        with open('data/Analyse_uv.pkl', 'wb') as file: 
            pickle.dump(data, file) 

if __name__ == '__main__':
    collect_data()