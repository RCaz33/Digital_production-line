import pandas as pd
import joblib
import numpy as np

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
    return sum(row["Batch_OGD_heure_debut"] <= check_time <= row["Batch_OGD_heure_fin"] for check_time in check_times)


def clean_data(data):

    # Handeling duplicates
    duplicates = data.duplicated(subset=['Batch_OGD_name','Batch_OGD_date'])
    data = data.loc[~duplicates]

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
    data['conc_KC8'] = data['Batch_OGD_KC8_masse'] / data['Batch_OGD_THF_Volume']
    data.drop(columns=['Batch_OGD_KC8_masse','Batch_OGD_THF_Volume'],inplace=True)


    # Handeling time data (transform to datetime format)
    datetime_to_remove = list()
    for col in data.columns:
        if 'heure' in col or 'date' in col:
            data[col] = pd.to_datetime(data[col])
            datetime_to_remove.append(col)

    data['month_production'] = data['Batch_OGD_date'].dt.month
    data['day_production_start'] = data['Batch_OGD_date'].dt.day
    data['days_exfo'] = (data['Batch_OGD_heure_fin'] - data['Batch_OGD_heure_debut']).dt.days

    # ajouter année au batch KC8 
    data.loc[:,'Batch_OGD_KC8_batch'] = data.Batch_OGD_date.dt.year.astype(str) + "-" + data.Batch_OGD_KC8_batch

    # Ajoute data autre source
    gde_marees = get_maree_data(years = [2022,2023,2024,2025])
    data["exfo_gde_maree"] =  data.apply(lambda row: check_if_within_range(row, gde_marees['date']), axis=1)
    data.drop(columns=datetime_to_remove, inplace=True)

    # impute valeur absurdes
    for var in ['Batch_OGD_Temperature','Batch_OGD_room_HR','Batch_OGD_room_T','conc_KC8','days_exfo','exfo_gde_maree']:
        _ = data.loc[data[var] != 0, ["month_production",var]]
        _dict = _.groupby(['month_production'])[var].mean().to_dict()

        if not var in ['days_exfo','exfo_gde_maree']:
            data.loc[data[var] == 0, var] = data.loc[data[var] == 0, 'month_production'].map(_dict)
        else:
            Q1 = np.percentile(data[var], 25)
            Q3 = np.percentile(data[var], 75)
            IQR = Q3 - Q1
            # Définir les seuils pour les outliers
            low_fly = Q1 - 1.5 * IQR
            up_fly = Q3 + 1.5 * IQR
            data.loc[(data[var] < low_fly) | (data[var]> up_fly),var] = data.loc[(data[var] < low_fly) | (data[var]> up_fly), 'month_production'].map(_dict)

    return data

# prepare data for ML
def set_preprocessor(X):
    """this function instanciate and test a sklearn preprocessor"""
    categorical_columns = ['Batch_OGD_Technicien','Batch_OGD_KC8_batch', 'Batch_OGD_Analyses',
                        'month_production','day_production_start','exfo_gde_maree']


    numerical_columns = ['Batch_OGD_Temperature','Batch_OGD_Agitation','Batch_OGD_room_HR',
                    'conc_KC8','Batch_OGD_room_T','days_exfo']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('numerical', StandardScaler(),numerical_columns),
            ('categorical',OneHotEncoder(sparse_output=False,handle_unknown='ignore'),categorical_columns)])
    try:
        # preprocessor.fit(X)
        return preprocessor
    except:
        return ("set_preprocessor is not working, check columns names")
