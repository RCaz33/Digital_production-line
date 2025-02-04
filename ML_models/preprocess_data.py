import os
import pickle
import click
import pandas as pd
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder


def dump_pickle(obj, filename: str):
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)


# def read_dataframe(filename: str):

#     url = 'http://127.0.0.1:8000/'
#     headers = {
#     'accept': 'application/json',
#     'Content-Type': 'application/json'}
#     response = requests.get('http://127.0.0.1:8000/OGD/', headers=headers)
#     metadata = pd.DataFrame(response.json())
#     time_columns = ['Batch_OGD_date','Batch_OGD_heure_debut','Batch_OGD_heure_fin']
#     timed = metadata[time_columns]
#     for col in timed.columns:
#         timed.loc[:,col] = pd.to_datetime(timed[col])

#     timed['year'] = pd.DatetimeIndex(timed['Batch_OGD_date']).year.astype(str)
#     timed['month'] = pd.DatetimeIndex(timed['Batch_OGD_date']).month.astype(str)
#     timed['time_exfo'] = (timed['Batch_OGD_heure_fin'] - timed['Batch_OGD_heure_debut']) / pd.Timedelta(hours=1)
#     metadata_timed = pd.concat([metadata,timed],axis=1)
#     return metadata_timed


def preprocess(metadata: pd.DataFrame, sc: StandardScaler, ohe: OneHotEncoder, fit_dv : bool = False):
    
    time_columns = ['Batch_OGD_date','Batch_OGD_heure_debut','Batch_OGD_heure_fin']
    timed = metadata[time_columns]
    for col in timed.columns:
        timed.loc[:,col] = pd.to_datetime(timed[col])

    timed['year'] = pd.DatetimeIndex(timed['Batch_OGD_date']).year.astype(str)
    timed['month'] = pd.DatetimeIndex(timed['Batch_OGD_date']).month.astype(str)
    timed['time_exfo'] = (timed['Batch_OGD_heure_fin'] - timed['Batch_OGD_heure_debut']) / pd.Timedelta(hours=1)
    metadata_timed = pd.concat([metadata,timed],axis=1)

    numerical_columns = ['Batch_OGD_KC8_masse',
                        'Batch_OGD_Temperature',
                        'Batch_OGD_Agitation',
                        'Batch_OGD_room_HR',
                        'Batch_OGD_room_T',
                        'time_exfo']
    categorical_columns = ['Batch_OGD_Technicien',
                            'Batch_OGD_KC8_batch',
                            'Batch_OGD_THF_batch',
                            'year',
                            'month']
    print(metadata_timed.columns)

    if fit_dv:
        scaled = sc.fit_transform(metadata_timed[numerical_columns])
        scaled = pd.DataFrame(scaled, columns=numerical_columns)
        onehotencoded = ohe.fit_transform(metadata_timed[categorical_columns])
        onehotencoded = pd.DataFrame(onehotencoded, columns = [a for b in ohe.categories_ for a in b])
    else:
        scaled = sc.transform(metadata_timed[numerical_columns])
        scaled = pd.DataFrame(scaled, columns=numerical_columns)
        onehotencoded = ohe.transform(metadata_timed[categorical_columns])
        onehotencoded = pd.DataFrame(onehotencoded, columns = [a for b in ohe.categories_ for a in b])

    metadata_ready = pd.concat([scaled,onehotencoded],axis=1)

    return metadata_ready, sc, ohe


@click.command()
@click.option(
    "--raw_data_path",
    help="Location where the raw data was saved"
)
@click.option(
    "--dest_path",
    help="Location where the resulting files will be saved"
)
def run_data_prep(raw_data_path: str, dest_path: str, dataset: str = "green"):


    # raw_data_path = 'ML_Models/data'


    with open(f'{raw_data_path}/train.pkl', 'rb') as file: 
        df_train = pickle.load(file) 
    with open(f'{raw_data_path}/test.pkl', 'rb') as file: 
        df_test = pickle.load(file) 


    # Fit the kmeans and preprocess data
    sc = StandardScaler()
    ohe = OneHotEncoder(sparse_output=False,handle_unknown='ignore')
    X_train, sc, ohe = preprocess(df_train, sc, ohe, fit_dv=True)
    X_test, _, _ = preprocess(df_test, sc, ohe, fit_dv=False)

    # Create dest_path folder unless it already exists
    os.makedirs(dest_path, exist_ok=True)

    # Save DictVectorizer and datasets
    dump_pickle(sc, os.path.join(dest_path, "sc.pkl"))
    dump_pickle(ohe, os.path.join(dest_path, "ohe.pkl"))
    dump_pickle((X_train), os.path.join(dest_path, "train_.pkl"))
    dump_pickle((X_test), os.path.join(dest_path, "test_.pkl"))


#### POSSIBLE MAKE A TEST HERE
# def test_one_sampel


if __name__ == '__main__':
    run_data_prep()
