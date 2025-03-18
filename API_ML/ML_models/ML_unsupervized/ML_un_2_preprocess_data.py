import os
import pickle
import click
import pandas as pd
import numpy as np
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
import random

def dump_pickle(obj, filename: str):
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)



def preprocess(metadata: pd.DataFrame, sc: StandardScaler, ohe: OneHotEncoder(sparse_output=False), fit_dv : bool = False):
    
    time_columns = ['Batch_OGD_date','Batch_OGD_heure_debut','Batch_OGD_heure_fin']
    timed = metadata[time_columns].copy()
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


    if fit_dv:
        scaled = sc.fit_transform(metadata_timed[numerical_columns])
        scaled = pd.DataFrame(scaled, columns=numerical_columns, index=metadata.Batch_OGD_name)
        onehotencoded = ohe.fit_transform(metadata_timed[categorical_columns])
        onehotencoded = pd.DataFrame(onehotencoded, columns = [a for b in ohe.categories_ for a in b], index=metadata.Batch_OGD_name)
    else:
        scaled = sc.transform(metadata_timed[numerical_columns])
        scaled = pd.DataFrame(scaled, columns=numerical_columns, index=metadata.Batch_OGD_name)
        onehotencoded = ohe.transform(metadata_timed[categorical_columns])
        onehotencoded = pd.DataFrame(onehotencoded, columns = [a for b in ohe.categories_ for a in b], index=metadata.Batch_OGD_name)

    metadata_ready = pd.concat([scaled,onehotencoded],axis=1)


    return metadata_ready, sc, ohe

def preprocess_spectral(idx_train, idx_val, data_raman, data_uv, mode='pca'):

    data_raman_train = data_raman[data_raman.index.isin(idx_train)].sort_index()
    data_raman_val = data_raman[data_raman.index.isin(idx_val)].sort_index()    
    
    data_uv_train = data_uv[data_uv.index.isin(idx_train)].sort_index()
    data_uv_val = data_uv[data_uv.index.isin(idx_val)].sort_index()


    if mode == 'pca':
        from sklearn.decomposition import PCA
        reduce_r = PCA(n_components=10)
        data_raman_train_weights = reduce_r.fit_transform(data_raman_train)
        data_raman_val_weights = reduce_r.transform(data_raman_val)
        reduce_uv = PCA(n_components=10)
        data_uv_train_weights = reduce_uv.fit_transform(data_uv_train)
        data_uv_val_weights = reduce_uv.transform(data_uv_val)

    elif mode == 'tsne':
        from sklearn.manifold import TSNE
        reduce_r = TSNE(n_components=10)
        data_raman_train_weights = reduce_r.fit_transform(data_raman_train)
        data_raman_val_weights = reduce_r.transform(data_raman_val)
        reduce_uv = TSNE(n_components=10)
        data_uv_train_weights = reduce_uv.fit_transform(data_uv_train)
        data_uv_val_weights = reduce_uv.transform(data_uv_val)

    elif mode == 'fastica':
        from sklearn.decomposition import FastICA
        reduce_r = FastICA(n_components=10)
        data_raman_train_weights = reduce_r.fit_transform(data_raman_train)
        data_raman_val_weights = reduce_r.transform(data_raman_val)
        reduce_uv = FastICA(n_components=10)
        data_uv_train_weights = reduce_uv.fit_transform(data_uv_train)
        data_uv_val_weights = reduce_uv.transform(data_uv_val)


    out_train = pd.DataFrame(np.concatenate([data_uv_train_weights,
                                             data_raman_train_weights],axis=1),
                                             index=data_raman_train.index)
    out_val = pd.DataFrame(np.concatenate([data_uv_val_weights,
                                            data_raman_val_weights],axis=1),
                                            index=data_raman_val.index)  

    return out_train, out_val, reduce_r, reduce_uv







@click.command()
@click.option(
    "--raw_data_path",
    prompt="Location where the raw data was saved", default='data/2025-02-28'
)
@click.option(
    "--dest_path",
    help="Location where the resulting files will be saved"
)
@click.option(
    "--mode",  default='pca', prompt='Mode of spectral reduction', help="Mode of spectral reduction"
)
@click.option(
    "--split",  default=0.8, prompt='split of dataset train/val'
)
@click.option(
    "--save",  default=True, prompt='Saving artifcat locally?'
)


def run_data_prep(raw_data_path: str, dest_path: str, mode: str, split : float, save : str = False):


    # raw_data_path = 'ML_Models/data'
    dir_path = os.path.join(raw_data_path,)
    os.makedirs(dir_path, exist_ok=True)

    with open(f'{raw_data_path}/OGD_metadata.pkl', 'rb') as file: 
        df = pickle.load(file)
        df.loc[:,'Batch_OGD_date'] = pd.to_datetime(df['Batch_OGD_date'].copy())
        df.sort_values(by='Batch_OGD_date',inplace=True)

    split_idx  = round(df.shape[0]*split)
    df_train = df.iloc[:split_idx,:]
    df_val = df.iloc[split_idx:,:]


    with open(f'{raw_data_path}/Analyse_raman.pkl', 'rb') as file: 
        data_raman = pickle.load(file) 
    with open(f'{raw_data_path}/Analyse_uv.pkl', 'rb') as file: 
        data_uv = pickle.load(file) 

    idx_train = df_train['Batch_OGD_name']
    idx_val = df_val['Batch_OGD_name']
    out_train, out_val, reduce_r, reduce_uv = preprocess_spectral(idx_train, idx_val, 
                                              data_raman, data_uv,
                                              mode=mode)



    # Fit the kmeans and preprocess data
    sc = StandardScaler()
    ohe = OneHotEncoder(sparse_output=False,handle_unknown='ignore')
    X_train, sc, ohe = preprocess(df_train, sc, ohe, fit_dv=True)
    X_val, _, _ = preprocess(df_val, sc, ohe, fit_dv=False)

    X_train.index = idx_train
    X_val.index = idx_val

    # combine metadata and spectral data
    data_train = pd.merge(X_train, out_train, left_index=True, right_index=True)
    data_val = pd.merge(X_val, out_val, left_index=True, right_index=True)


    if save:
    # Create dest_path folder unless it already exists
        if not dest_path:
            dest_path = f'data/{raw_data_path.split("/")[1]}/ML_ready'
        os.makedirs(dest_path, exist_ok=True)

        # Save Scaler,Encoder and datasets
        dump_pickle(sc, os.path.join(dest_path, "sc.pkl"))
        dump_pickle(ohe, os.path.join(dest_path, "ohe.pkl"))
        dump_pickle(reduce_r, os.path.join(dest_path, "reduce_r.pkl"))
        dump_pickle(reduce_uv, os.path.join(dest_path, "reduce_uv.pkl"))
        
        dump_pickle((data_train), os.path.join(dest_path, "train.pkl"))
        dump_pickle((data_val), os.path.join(dest_path, "val.pkl"))

        print(f"artifacts saved at {dest_path}")
#### POSSIBLE MAKE A val HERE
# def val_one_sampel


if __name__ == '__main__':
    run_data_prep()
