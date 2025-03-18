# import des librairies
import os
import pickle
import json
import joblib
import click
import pandas as pd
import requests

from dotenv import load_dotenv
import os
load_dotenv()


# helper fonctions
def dump_pickle(obj, filename: str):
    """Cette fonction sers à sauvegarder un fichier pickle"""
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)


def get_technician_dict():
    """Cette fonction sers à se connecter à une BDD pour récuperer les informations d'anonymisation de techniciens"""
    import mysql.connector as bdd_connect

    BDD_CW = bdd_connect.connect(host='localhost',
                                user=os.getenv('LOCAL_DB_USER'),
                                password=os.getenv('LOCAL_DB_PASS'),
                                database=os.getenv('CW_DB_NAME'),
                                port=3306)
    curseur = BDD_CW.cursor()

    # Query avec docstring pour eviter SQL insertion
    to_execute = f"SELECT Technicien_id, Initiales_tech FROM Techniciens"
    curseur.execute(to_execute)

    # Fetch data 
    rows=curseur.fetchall()
    curseur.close()
    BDD_CW.close()

    # Export
    df = dict(pd.DataFrame(rows, columns=[i[0] for i in curseur.description]).values)

    return df





# script de préparation des données
@click.command()
@click.option(
    "--raw_data_path", default="data/2025-03-13_data_production.csv", prompt='Raw data path',
    help="Dossier ou les données brutes sont stockées"
)



def transfer_data(raw_data_path : str ):

    data = pd.read_csv(raw_data_path)
    print("Dimensions données source :",  data.shape)

    # Select given columns
    new_data = data[['Batch_name','Date','Technicien_id','Batch_KC8','Masse_KC8','Batch_THF_ref','Volume_THF',
      'BaG_T','Vitesse_agitation',
      'Heure_debut','Heure_ajout2','Lab_HR','Lab_T','QC_Conc_OGD','QC_Categorie']]

    # Rename columns to fit new database
    new_data.columns = ['Batch_OGD_name','Batch_OGD_date','Batch_OGD_Technicien','Batch_OGD_KC8_batch',
                    'Batch_OGD_KC8_masse','Batch_OGD_THF_batch','Batch_OGD_THF_Volume','Batch_OGD_Temperature',
                    'Batch_OGD_Agitation','Batch_OGD_heure_debut','Batch_OGD_heure_fin',
                    'Batch_OGD_room_HR','Batch_OGD_room_T','Batch_OGD_Stock','Batch_OGD_Analyses']
    new_data.loc[:,'Batch_OGD_Stock'] = 0
    
    # Get id of technicians
    df = get_technician_dict()
    # df = {str(k):v for k,v in df.items()}

    # Readjust columns types
    new_data.loc[:,'Batch_OGD_Technicien'] = new_data['Batch_OGD_Technicien'].apply(lambda x : df[(x)]).astype(str).tolist()
    new_data.loc[:,'Batch_OGD_Analyses'] = data.Centrifugation.astype(str).tolist()
    new_data.loc[:,'Batch_OGD_THF_batch'] = 'to_fill'

    # export to new database
    import json
    import requests

    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'}

    for i in range(new_data.shape[0]):
        to_bdd = new_data.iloc[i,:].fillna(0).to_dict()

        response = requests.post('http://127.0.0.1:8000/OGD/', headers=headers, data=json.dumps(to_bdd))

        if response.status_code != 200:
            print("ERROR", response.content)

    
    new_data.to_csv("data/new_data.csv")

    target = data[['QC_Conc_OGD', 'QC_Categorie']]
    target.to_csv(f'data/y.csv')

if __name__ == '__main__':
    transfer_data()
