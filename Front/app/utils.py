import datetime
from flask import flash
import requests
import pandas as pd
import numpy as np
import json
import joblib
import io
import base64
import os
from dotenv import load_dotenv
load_dotenv()


def update_preds_from_UV(batch_name,conc):
    """ met à jour les prédictions de concentration réelle dans la BDD """

    response = requests.get("http://127.0.0.1:8000/Predictions")
    code_get = response.status_code

    # update the prediction for a given batch name
    a = pd.DataFrame(response.json())
    mask = [batch_name in a.Prediction_data[i]['sample'] for i in range(a.shape[0])]
    new_pred=dict()
    for col in a[mask]:
        new_pred[col] = a[mask][col].values[0]
    id = new_pred['Prediction_id']
    new_pred['Prediction_id'] = str(new_pred['Prediction_id'])

    # mise a jour concentration reelle
    new_pred_data = new_pred['Prediction_data']
    new_pred_data['reel'] = float(conc[0])
    new_pred['Prediction_data'] = new_pred_data

    response = requests.post(f"http://127.0.0.1:8000/Predictions/update/{id}",data=json.dumps(new_pred))
    code_post = response.status_code
    return code_get, code_post




def update_MPs():
    """ met à jour les stocks disponibles des matières premières """
    response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/')
    MP = pd.DataFrame(response.json())
    batch_C = MP.loc[MP.MP_nom=='Carbone',['MP_ref_fournisseur','MP_stock','MP_unite']].values
    batch_K = MP.loc[MP.MP_nom=='Potassium',['MP_ref_fournisseur','MP_stock','MP_unite']].values
    batch_THF = MP.loc[MP.MP_nom=='THF',['MP_ref_fournisseur','MP_stock','MP_unite']].values
    return batch_C,batch_K,batch_THF


def predict_OGD_concentration(data,heure_debut):
    """ route protégée 
    utilise API_ML pour prédire la concentration de graphene dans l'OGD"""
    data_bis = data.copy()
    data_bis["Batch_OGD_heure_fin"] = (heure_debut + pd.DateOffset(days=6)).isoformat()
    data_bis["Batch_OGD_Analyses"] = "1"
    data_bis["Batch_OGD_Stock"] = 0

    response = requests.post(url = "http://127.0.0.1:8001/predict/elasticnet",
                                headers = {'Supervized-API-Key': os.getenv('API_SUPERVIZED_SECRET_KEY'),
                                           'Content-Type': 'application/json'},
                                data = json.dumps(data_bis))
    return response.json()['pred']


def format_datetime(date,heure):
    """ transforme les dates et heures en format datetime """

    date = datetime.datetime.strptime(date, '%d/%m/%y')
    heure =  datetime.datetime.strptime(heure, '%H:%M').time()
    heure = datetime.datetime.combine(date.date(),heure)
    return date, heure



def fetch_MP():
    """ fetch les derniers batch de matieres premieres et de KC8 """    

    try:
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/')
        K_name,C_name,THF_name = get_matieres_premieres(response)
        default_batch = dict({'K':K_name,'C':C_name,'THF':THF_name})

        try:
            response = requests.get(f'http://127.0.0.1:8000/KC8/')
            KC8_all = pd.DataFrame(response.json())
            # on filtre pour n'avoir que les batch qui sont termines
            KC8_all = KC8_all.loc[~KC8_all.Batch_KC8_heure_fin.isnull()]
            # on recupere le dernier batch ajoute
            KC8_batch = KC8_all.loc[KC8_all.Batch_KC8_id==np.max(KC8_all.Batch_KC8_id),'Batch_KC8_name'].values[0]
            default_batch['KC8'] = KC8_batch
        except:
            default_batch['KC8'] = 'na'
        print(5*"\n{*} SUCESS")
        print('--> fetch_MP OK')


        return default_batch
    except:
        return('==> Traceback : problem with utils.update_MP')

    


def update_stock_product(data):
        """ met à jour le stock des produits après envoie de batch """

        headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'}
        status=dict()
        response = requests.get(f'http://127.0.0.1:8000/Produit/name/{data["Envoi_produit_batch"]}')
        status['get_product'] = response.status_code
        updated_batch = response.json()
        new_value = int(updated_batch['Batch_produit_stock'] - float(data['Envoi_produit_Qte']))
        if new_value >= 0:
            updated_batch['Batch_produit_stock'] = new_value
            response = requests.post(f'http://127.0.0.1:8000/Produit/update/{updated_batch["Batch_Produit_id"]}', headers=headers, data=json.dumps(updated_batch))
            status['post_product'] = response.status_code
        else :
            status['post_product'] = None
        return status


def update_stock_OGD_additif(data):
        """ met à jour le stock des OGD et des additifs après fabrication produit """

        headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'}
        status=dict()

        response = requests.get(f'http://127.0.0.1:8000/OGD/name/{data["Batch_Produit_OGD_batch"]}')
        status['get_OGD'] = response.status_code
        updated_batch = response.json()
        new_value = int(updated_batch['Batch_OGD_Stock'] - float(data['Batch_Produit_OGD_Qte']))
        if new_value >= 0:
            updated_batch['Batch_OGD_Stock'] = new_value
            response = requests.post(f'http://127.0.0.1:8000/OGD/update/{updated_batch["Batch_OGD_id"]}', headers=headers, data=json.dumps(updated_batch))
            status['post_OGD'] = response.status_code
        else :
            status['post_OGD'] = None
        
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_Produit_additif_batch"]}')
        status['get_additif'] = response.status_code
        updated_batch = response.json()
        new_value = int(updated_batch['Batch_Produit_additif_Qte'] - float(data['Batch_Produit_additif_Qte']))
        if new_value >= 0:
            updated_batch['Batch_Produit_additif_Qte'] = new_value
            response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch["MP_id"]}', headers=headers, data=json.dumps(updated_batch))
            status['post_additif'] = response.status_code
        else :
            status['post_additif'] = None

        return status





def update_stocks_K_C(data):
        """ met à jour le stock de K et C après fabrication de KC8 """

        headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'}
        status=dict()
        # update stock of K 
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_KC8_K_batch"]}')
        status['get_K'] = response.status_code
        updated_batch_K = response.json()
        new_value_K = int(updated_batch_K['MP_stock'] - (39/(39+(8*12))*float(data['Batch_KC8_masse'])))
        print(updated_batch_K)
        # update stock of C
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_KC8_C_batch"]}')
        updated_batch_C = response.json()
        status['get_C'] = response.status_code
        new_value_C = updated_batch_C['MP_stock'] - ((8*12)/(39+(8*12))*float(data['Batch_KC8_masse']))
        print(updated_batch_C)
        # mise a jour bdd
        if (new_value_K >= 0) and (new_value_C >= 0):
            updated_batch_K['MP_stock'] = new_value_K
            response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch_K["MP_id"]}', headers=headers, data=json.dumps(updated_batch_K))
            status['post_K'] = response.status_code
        
            updated_batch_C['MP_stock'] = new_value_C
            response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch_C["MP_id"]}', headers=headers, data=json.dumps(updated_batch_C))
            status['post_C'] = response.status_code
        
        else :
            status['post_K'],status['post_C'] = None, None

        return status



def update_stocks_KC8_THF(data):
        """ met à jour le stock de KC8 et THF après fabrication de OGD """

        headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'}
        status=dict()

        # update stock of KC8 
        response = requests.get(f'http://127.0.0.1:8000/KC8/name/{data["Batch_OGD_KC8_batch"]}')
        status['get_KC8'] = response.status_code
        updated_batch_KC8 = response.json()
        new_value_KC8 = float(updated_batch_KC8['Batch_KC8_masse'] - float(data['Batch_OGD_KC8_masse']))
        
        # update stock of THF
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_OGD_THF_batch"]}')
        status['get_THF'] = response.status_code
        updated_batch_THF = response.json()
        new_value_THF = updated_batch_THF['MP_stock'] - int(data['Batch_OGD_THF_Volume'])

        if (new_value_KC8 >= 0) and (new_value_THF >= 0):
            updated_batch_KC8['Batch_KC8_masse'] = new_value_KC8
            response2 = requests.post(f'http://127.0.0.1:8000/KC8/update/{updated_batch_KC8["Batch_KC8_id"]}', headers=headers, data=json.dumps(updated_batch_KC8))
            status['post_KC8'] = response2.status_code

            updated_batch_THF['MP_stock'] = new_value_THF
            response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch_THF["MP_id"]}', headers=headers, data=json.dumps(updated_batch_THF))
            status['post_THF'] = response.status_code

        else :
            status['post_KC8'] = None        

        return status


def populate_form(form,response):
    """ renseigne les champ du form avec la data de l'API """

    data = response.json()
    for field in form:
        for k,v in data.items():
            if field.name == k:
                if field.name == 'Envoi_date_effective':
                    try:
                        form[field.name].data = datetime.datetime.strptime(data[k], '%Y-%m-%dT%H:%M:%S')#.strftime(format='%d/%m/%y')
                    except:
                        continue
                elif  '_date' in field.name :
                    form[field.name].data = datetime.datetime.strptime(data[k], '%Y-%m-%dT%H:%M:%S')#.strftime(format='%d/%m/%y')
                elif '_heure_debut' in field.name:
                    form[field.name].data = datetime.datetime.strptime(data[k], '%Y-%m-%dT%H:%M:%S')#.strftime(format='%H:%M')
                elif '_heure_fin' in field.name:
                    form[field.name].data = datetime.datetime.now()
                else:
                    form[field.name].data = data[k]
    return form



def get_last_10_batch():
    """ recupere les 10 derniers batch de matieres premieres et de KC8 """

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'}
    
    # get last matieres premieres
    url = 'http://127.0.0.1:8000/matieres_premieres/'
    data = pd.DataFrame(requests.get(url).json())
    last_10_K=data.loc[data.MP_nom == 'Potassium'].sort_values('MP_id')['MP_ref_fournisseur'].values[-10:][::-1]
    last_10_C=data.loc[data.MP_nom == 'Carbone'].sort_values('MP_id')['MP_ref_fournisseur'].values[-10:][::-1]
    last_10_THF=data.loc[data.MP_nom == 'THF'].sort_values('MP_id')['MP_ref_fournisseur'].values[-10:][::-1]
    # get last KC8
    url = 'http://127.0.0.1:8000/KC8/'
    data = pd.DataFrame(requests.get(url).json()) 
    data = data.loc[~data.Batch_KC8_heure_fin.isnull()]
    last_10_KC8=data.sort_values('Batch_KC8_id')['Batch_KC8_name'].values[-10:][::-1]
    
    return last_10_K, last_10_C, last_10_THF, last_10_KC8

def get_matieres_premieres(response):
    """ recupere les dernieres matieres premieres """

    data = pd.DataFrame(response.json())
    try:
        K_name=data.loc[data.MP_nom == 'Potassium'].sort_values('MP_id')['MP_ref_fournisseur'].values[-1]
        C_name=data.loc[data.MP_nom == 'Carbone'].sort_values('MP_id')['MP_ref_fournisseur'].values[-1]
        THF_name=data.loc[data.MP_nom == 'THF'].sort_values('MP_id')['MP_ref_fournisseur'].values[-1]
    except:
        K_name=C_name=THF_name='na'
    return K_name,C_name,THF_name

    
class get_material_composition_for_product:
    """ compute the qty of material needed as a function of product
    ratio are base on 1L OGD at 2 g/L ==> 2 grams of OGD
    On multiplie le facteur par la quantité de produit fini voulue pour avoir la masse de produit utilise (cf mail Victor 18/02/25)
    # UPDATE WITH CALCULATION DEPENDING ON QTY
    """
    def __init__(self, product: str, product_qty: float = 1):
        self.product = product
        self.product_qty = product_qty 


    def OGD(self):
        if self.product == 'W1':
            return {'OGD':0.17*self.product_qty}
        elif self.product == 'W2':
            return {'OGD':0.5*self.product_qty}
        elif self.product == 'W3':
            return {'OGD':2.4*self.product_qty}
        elif self.product == 'W10':
            return {'OGD':4.9*self.product_qty}
        elif self.product == 'W3NC':
            return {'OGD':2.4*self.product_qty}
        elif self.product == 'W10NC':
            return {'OGD':4.9*self.product_qty}
        elif self.product == 'W20NC':
            return {'OGD':9.8*self.product_qty}
        elif self.product == 'EpoC':
            return {'OGD':3.6*self.product_qty}
        elif self.product == 'EpoF':
            return {'OGD':13.2*self.product_qty}
        elif self.product == 'EpoR':
            return {'OGD':3.6*self.product_qty}
        



    def water(self):
        if self.product in ['W1','W2','W3','W10','W3NC','W10NC']:
            return {'water':1*self.product_qty}
        elif self.product == 'W20NC':
            return {'water':2*self.product_qty}
        elif self.product in ['EpoC','EpoF','EpoR']:
            return {'water':0.08*self.product_qty}
        else:
            return {'water':0}
        
    def viscosant(self):

        ##### IF Y_UPDATE HERE? UPDATE ALSO SCRIPT IN ADD_BATCH_PRODUIT
        if self.product in ['W2','W3']:
            return {'viscosant':0.005*self.product_qty}
        elif self.product in ['W3NC','W10NC']:
            return {'viscosant':0.006*self.product_qty}
        elif self.product == 'W10':
            return {'viscosant':0.008*self.product_qty}
        elif self.product == 'W20NC':
            return {'viscosant':0.001*self.product_qty}
        else:
            return {'viscosant':0}
        
    def KOH(self):
        if self.product in ['W2','W3','W10']:
            return {'KOH':0.015*self.product_qty}
        elif self.product in ['W3NC','W10NC']:
            return {'KOH':0.018*self.product_qty}
        elif self.product == 'W20NC':
            return {'KOH':0.036*self.product_qty}
        else:
            return {'KOH':0}
        
    def hexane(self):
        if self.product in ['W2','W3','W10','W3NC','W10NC']:
            return {'hexane':1*self.product_qty}
        elif self.product == 'W20NC':
            return {'hexane':2*self.product_qty}
        else:
            return {'hexane':0}
        
    def Epikote1001(self):
        if self.product == 'EpoC':
            return {'Epikote1001':1.2*self.product_qty}
        else:
            return {'Epikote1001':0}
        
    def Epikote827(self):
        if self.product in ['EpoF','EpoR']:
            return {'Epikote827':1.2*self.product_qty}
        else:
            return {'Epikote827':0}
        
    def acetone(self):
        if self.product in ['EpoC','EpoF']:
            return {'acetone':0.5*self.product_qty}
        else:
            return {'acetone':0}
        
    def xylene(self):
        if self.product == 'EpoC':
            return {'xylene':0.4*self.product_qty}
        else:
            return {'xylene':0}
        
    def NaTPB(self):
        if self.product in ['EpoC','EpoF','EpoR']:
            return {'NaTPB':0.01*self.product_qty}
        else:
            return {'NaTPB':0}
        

