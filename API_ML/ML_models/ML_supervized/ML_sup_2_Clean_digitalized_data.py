# import des librairies
import os
import pickle
import json
import joblib
import click
import pandas as pd
import requests

# helper fonctions
def dump_pickle(obj, filename: str):
    """Cette fonction sers à sauvegarder un fichier pickle"""
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)

def get_maree_data(years : list):
    """Cette fonction se connecte à une API externe pour récuperer des données si elle ne sont pas déja présentes"""
    try :
        gde_marees = joblib.load("data/gde_maree.bin")
        print("Donées grandes marées disponibles")
        return gde_marees

    except:
        print("Téléchargement données grandes marées")
        gde_marees = pd.DataFrame()
        for year in years:
            url = f"https://data.stmalo-agglomeration.fr/api/explore/v2.1/catalog/datasets/grandes-marees-a-saint-malo/records?limit=20&refine=date%3A%22{year}%22"
            gde_marees = pd.concat([gde_marees,pd.DataFrame(json.loads(requests.get(url).content)['results'])],axis=0)
        # gde_marees
        gde_marees["date"] = pd.to_datetime(gde_marees["date"])
        joblib.dump(gde_marees,"data/gde_maree.bin")
        return gde_marees
    
def check_if_within_range(row, check_times):
    """
    Compte le nombre de datetimes dans check_times qui tombent dans la plage
    définie par Heure_debut et Heure_ajout2.
    """
    return sum(row["Heure_debut"] <= check_time <= row["Heure_ajout2"] for check_time in check_times)


# script de préparation des données
@click.command()
@click.option(
    "--raw_data_path", default='data/2025-02-25_data_production.csv', prompt='Raw data path',
    help="Dossier ou les données brutes sont stockées"
)
@click.option(
    "--dest_path", default = 'data/', prompt='Destination path',
    help="Dossier ou les données néttoyées seront stockées"
)


def clean_data(raw_data_path : str, dest_path : str ):

    data = pd.read_csv(raw_data_path)
    print("Dimensions données source :",  data.shape)

    # Handeling duplicates
    duplicates = data.duplicated(subset='Batch_id')
    data = data.loc[~duplicates]

    # Handeling verbose variables
    variable_verbose = ['Sediments']
    data.drop(columns=variable_verbose,inplace=True)

    # Handeling null values
    null_values = list()
    for col in data.columns:
        if data[col].isnull().sum() > data.shape[0]/3:
            null_values.append(col)
    data.drop(columns=null_values,inplace=True)

    # Handeling unique values
    variable_to_remove = list()
    count_unique = data.astype(str).describe().T

    # find columns names that have unique values or identical values (not usefull for ML model)
    for i in range(count_unique.shape[0]):
        if count_unique.iloc[i,1] == 280 or count_unique.iloc[i,1] == 1:
            variable_to_remove.append(data.columns[i])
    data[variable_to_remove].astype(str).describe()
    data.drop(columns=variable_to_remove,inplace=True)

    # Data Engineering
    data['conc_KC8'] = data['Masse_KC8'] / (data['Volume_THF'] + data['Volume_THF_ajout2'])
    data['volume_O2'] = data['Debit_air_synthetique'] * data['Temps_oxidation']
    data.drop(columns=['Masse_KC8','Volume_THF','Volume_THF_ajout2','Debit_air_synthetique','Temps_oxidation'],inplace=True)


    # Handeling time data (transform to datetime format)
    datetime_to_remove = list()
    for col in data.columns:
        if 'Heure' in col or 'Date' in col:
            data[col] = pd.to_datetime(data[col])
            datetime_to_remove.append(col)

    data['month_production'] = data['Date'].dt.month
    data['days_exfo'] = (data['Heure_ajout2'] - data['Heure_debut']).dt.days
    data['sediment_time'] = (data['Heure_fin_sedimentation'] - data['Heure_debut_sedimentation']).dt.total_seconds()

    # Ajoute data autre source
    gde_marees = get_maree_data(years = [2022,2023,2024,2025])
    data["exfo_gde_maree"] =  data.apply(lambda row: check_if_within_range(row, gde_marees['date']), axis=1)
    data.drop(columns=datetime_to_remove, inplace=True)

    # Handeling environmental variable (numerical to categorical variables)
    threshold_H2O = 0.09
    threshold_O2 = 0.09
    environ_variable = list()
    for col in data.columns:
        if 'H2O_ppm' in col:
            data[col] = data[col].apply(lambda x : 1 if x <= threshold_H2O else 0)
            environ_variable.append(col)
        elif 'O2_ppm' in col:
            data[col] = data[col].apply(lambda x : 1 if x <= threshold_O2 else 0)
            environ_variable.append(col)

    # remove data from final analysis
    data.drop(columns=['m_OGD', 'm_THF', 'Abs_800'], inplace=True)

    # Export data and target
    target = data[['QC_Conc_OGD', 'QC_Categorie']]
    target.to_csv(f'{dest_path}y.csv')
    data.drop(columns=['QC_Conc_OGD', 'QC_Categorie'],inplace=True)
    data.to_csv(f'{dest_path}X.csv')
    print("Dimensions données cleanées", data.shape)
    print(data.columns)


if __name__ == '__main__':
    clean_data()
