import datetime
from flask import flash
import requests
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import joblib
import io
import base64

def fetch_MP():
    try:
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/')
        K_name,C_name,THF_name = get_matieres_premieres(response)
        default_batch = dict({'K':K_name,'C':C_name,'THF':THF_name})

        response = requests.get(f'http://127.0.0.1:8000/KC8/')
        KC8_all = pd.DataFrame(response.json())
        KC8_batch = KC8_all.loc[KC8_all.Batch_KC8_id==np.max(KC8_all.Batch_KC8_id),'Batch_KC8_name'].values[0]
        default_batch['KC8'] = KC8_batch
        print(5*"\n{*} SUCESS")
        print('--> fetch_MP OK')
    except:
        print(5*"\n{*} ERROR")
        print('==> Traceback : problem with utils.update_MP')

    return default_batch


def update_stock_product(data):
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
        headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'}
        status=dict()
        # update stock of K 
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_KC8_K_batch"]}')
        status['get_K'] = response.status_code
        updated_batch = response.json()
        new_value = int(updated_batch['MP_stock'] - (39/(39+(8*12))*float(data['Batch_KC8_masse'])))
        if new_value >= 0:
            updated_batch['MP_stock'] = new_value
            response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch["MP_id"]}', headers=headers, data=json.dumps(updated_batch))
            status['post_K'] = response.status_code
        else :
            status['post_K'] = None
        # update stock of C
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_KC8_C_batch"]}')
        updated_batch = response.json()
        status['get_C'] = response.status_code
        new_value = updated_batch['MP_stock'] - ((8*12)/(39+(8*12))*float(data['Batch_KC8_masse']))
        if new_value >= 0:
            updated_batch['MP_stock'] = new_value
            response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch["MP_id"]}', headers=headers, data=json.dumps(updated_batch))
            status['post_C'] = response.status_code
        else :
            status['post_C'] = None
        return status

def update_stocks_KC8_THF(data):
        headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'}
        status=dict()

        # update stock of KC8 
        response = requests.get(f'http://127.0.0.1:8000/KC8/name/{data["Batch_OGD_KC8_batch"]}')
        status['get_KC8'] = response.status_code
        updated_batch = response.json()
        new_value = float(updated_batch['Batch_KC8_masse'] - float(data['Batch_OGD_KC8_masse']))
        
        if new_value >= 0:
            updated_batch['Batch_KC8_masse'] = new_value
            response2 = requests.post(f'http://127.0.0.1:8000/KC8/update/{updated_batch["Batch_KC8_id"]}', headers=headers, data=json.dumps(updated_batch))
            status['post_KC8'] = response2.status_code
        else :
            status['post_KC8'] = None        
        
        # update stock of THF
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_OGD_THF_batch"]}')
        status['get_THF'] = response.status_code
        updated_batch = response.json()
        new_value = updated_batch['MP_stock'] - int(data['Batch_OGD_THF_Volume'])

        if new_value >= 0:
            updated_batch['MP_stock'] = new_value
            response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch["MP_id"]}', headers=headers, data=json.dumps(updated_batch))
            status['post_THF'] = response.status_code
        else :
            status['post_THF'] = None  

        return status


def populate_form(form,response):
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
    data = pd.DataFrame(response.json())
    K_name=data.loc[data.MP_nom == 'Potassium'].sort_values('MP_id')['MP_ref_fournisseur'].values[-1]
    C_name=data.loc[data.MP_nom == 'Carbone'].sort_values('MP_id')['MP_ref_fournisseur'].values[-1]
    THF_name=data.loc[data.MP_nom == 'THF'].sort_values('MP_id')['MP_ref_fournisseur'].values[-1]
    return K_name,C_name,THF_name



def post_data_step1_fastapi(step, batch_id,form_Sn):
    form_Sn_data = list() 
    try:         
        for field in form_Sn:
            if  field.name != 'submit' and field.name != 'csrf_token':

                # transform l'heure en format datetime pour insertion dans BDD
                if 'Heure' in field.name:
                    date = [a.data.date() for a in form_Sn if 'Date' in a.name][0]
                    correct_datetime = datetime.datetime.combine(date,field.data)
                    form_Sn_data.append(correct_datetime.strftime('%Y-%m-%d %H:%M:%S'))

                # API call pour anonymiser le technicien en changeant intilatiales par id
                elif 'Initiales' in field.name:
                    ## condition qui gere si la page contien un id de technicien à la place des initiales (mise à jour)
                    if field.data.isnumeric():
                        form_Sn_data.append(field.data)
                    else:
                        response = requests.get(f'http://127.0.0.1:5001/techniciens/initials/?initiales={field.data.upper()}')
                        tech_id = response.json()['Technicien_id']
                        form_Sn_data.append(tech_id)

                # transforme bool en little integral
                elif 'Centrifugation' in field.name:
                    form_Sn_data.append(1 if field.data == True else 0)

                # mise à jour 24/06/28 ==> chgmt protocole, tous les ajout le même jour = plus besoin de cette info
                elif 'Ajout_jourJ' in field.name:
                    form_Sn_data.append(0)

                # si les données n'ont pas besion d'etre réagencé on les ajoute au formulaire
                else:
                    form_Sn_data.append(field.data)
    except Exception as e:
        print(10*"EXECPT in parsing fields \n",e)    


    # format a list with all data to insert
    to_insert = list()
    to_insert.append(batch_id)
    for data in form_Sn_data:
        to_insert.append(str(data)) # make each item a string to include in a sql query
        
        
    if step==1:
        response = requests.get('http://127.0.0.1:5001/step1/name?initiales={field.data.upper()}')

        
        curseur.execute(f"SELECT Batch_id FROM Etape1_lancement WHERE Batch_id = {to_insert[0]};")
        _data = curseur.fetchall()
        if not _data:
            flash("Mise à jour Etape1")
            to_execute =  f"INSERT INTO Etape1_lancement VALUES ({','.join(['%s' for _ in to_insert])})"
        else:
            curseur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'Etape1_lancement';")
            form_Sn_fields = [col[0] for col in curseur.fetchall()] 
            flash("/!\\ Les valeurs de Etape1 ont étée actualisées /!\\")
            to_execute =  f"UPDATE Etape1_lancement SET {','.join([f+'='+'%s' for f in form_Sn_fields])} WHERE Batch_id ={to_insert[0]};"
                

###### Automatise la recuperation des données 
def get_form_data(step, form_S0, form_Sn, curseur):
        form_Sn_data = list()
        ## On recupère toutes les informations du formulaire form_Sn
        try:
            
            for field in form_Sn:
                if  field.name != 'submit' and field.name != 'csrf_token':

                    # transform l'heure en format datetime pour insertion dans BDD
                    if 'Heure' in field.name:
                        date = [a.data.date() for a in form_Sn if 'Date' in a.name][0]
                        correct_datetime = datetime.datetime.combine(date,field.data)
                        form_Sn_data.append(correct_datetime.strftime('%Y-%m-%d %H:%M:%S'))

                    # anonymise technicien en changeant intilatiales par id
                    elif 'Initiales' in field.name:
                        ## condition qui gere si la page contien un id de technicien à la place des initiales (mise à jour)
                        if field.data.isnumeric():
                            form_Sn_data.append(field.data)
                        else:
                            to_execute = "SELECT Technicien_id FROM Techniciens WHERE Initiales_tech=%s"
                            curseur.execute(to_execute,(field.data.upper(),))
                            form_Sn_data.append(curseur.fetchone()[0])

                    # transforme bool en little integral
                    elif 'Centrifugation' in field.name:
                        form_Sn_data.append(1 if field.data == True else 0)

                    # mise à jour 24/06/28 ==> chgmt protocole, tous les ajout le même jour = plus besoin de cette info
                    elif 'Ajout_jourJ' in field.name:
                        form_Sn_data.append(0)

                    # si les données n'ont pas besion d'etre réagencé on les ajoute au formulaire
                    else:
                        form_Sn_data.append(field.data)
        except Exception as e:
            print(10*"EXECPT in parsing fields \n",e)


        try:
            ## On identifie le ID du Batch
            to_execute = "SELECT Batch_id FROM Batch_OGD WHERE Batch_name=%s"
            curseur.execute(to_execute,(form_S0.Step0_BatchName.data,)) 

            # on initialise la liste à inserer dans les tables de la BDD en commencant par l'ID de Batch
            to_insert = list()
            to_insert.append(str(curseur.fetchone()[0]))

            # on itere chaque donnée du form pour l'ajouter à la liste à inserer
            for data in form_Sn_data:
                to_insert.append(str(data))


        except Exception as e:
            print(10*"EXECPT in loading curseur data \n",e)


        try:
            ## Pour chaque etape : on recupere l'ID 
            ## si il n'existe pas on INSERT INTO
            ## si il existe on recupere le nom des colonnes de la BDD puis UPDATE .. SET .. WHERE Batch_id = ID 
            curseur.fetchall()
            if step==1:
                curseur.execute(f"SELECT Batch_id FROM Etape1_lancement WHERE Batch_id = {to_insert[0]};")
                _data = curseur.fetchall()
                if not _data:
                    flash("Mise à jour Etape1")
                    to_execute =  f"INSERT INTO Etape1_lancement VALUES ({','.join(['%s' for _ in to_insert])})"
                else:
                    curseur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'Etape1_lancement';")
                    form_Sn_fields = [col[0] for col in curseur.fetchall()] 
                    flash("/!\\ Les valeurs de Etape1 ont étée actualisées /!\\")
                    to_execute =  f"UPDATE Etape1_lancement SET {','.join([f+'='+'%s' for f in form_Sn_fields])} WHERE Batch_id ={to_insert[0]};"
                    

            elif step==2:
                curseur.execute(f"SELECT Batch_id FROM Etape2_THF_Sedim_Centri WHERE Batch_id = {to_insert[0]};")
                _data = curseur.fetchall()
                if not _data:
                    flash("ise à jour Etape2")
                    to_execute =  f"INSERT INTO Etape2_THF_Sedim_Centri VALUES ({','.join(['%s' for _ in to_insert])})"
                else:
                    curseur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'Etape2_THF_Sedim_Centri';")
                    form_Sn_fields = [col[0] for col in curseur.fetchall()] 
                    flash("/!\\ Les valeurs de Etape2 ont étée actualisées /!\\")
                    to_execute =  f"UPDATE Etape2_THF_Sedim_Centri SET {','.join([f+'='+'%s' for f in form_Sn_fields])} WHERE Batch_id ={to_insert[0]};"
                                    

            elif step==3:
                curseur.execute(f"SELECT Batch_id FROM Etape3_Oxydation WHERE Batch_id = {to_insert[0]};")
                _data = curseur.fetchall()
                if not _data:
                    flash("Mise à jour Etape3")
                    to_execute =  f"INSERT INTO Etape3_Oxydation VALUES ({','.join(['%s' for _ in to_insert])})"
                else:
                    curseur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'Etape3_Oxydation';")
                    form_Sn_fields = [col[0] for col in curseur.fetchall()]                  
                    flash("/!\\ Les valeurs de Etape3 ont étée actualisées /!\\")
                    to_execute =  f"UPDATE Etape3_Oxydation SET {','.join([f+'='+'%s' for f in form_Sn_fields])} WHERE Batch_id ={to_insert[0]};"


            elif step==4:
                curseur.execute(f"SELECT Batch_id FROM Etape4_CtrlQualite WHERE Batch_id = {to_insert[0]};")
                _data = curseur.fetchall()
                if not _data:
                    flash("Mise à jour Etape4")
                    to_execute =  f"INSERT INTO Etape4_CtrlQualite VALUES ({','.join(['%s' for _ in to_insert])})"
                else:
                    curseur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'Etape4_CtrlQualite';")
                    form_Sn_fields = [col[0] for col in curseur.fetchall()]                  
                    flash("/!\\ Les valeurs de Etape4 ont étée actualisées /!\\")
                    to_execute =  f"UPDATE Etape4_CtrlQualite SET {','.join([f+'='+'%s' for f in form_Sn_fields])} WHERE Batch_id ={to_insert[0]};"

            else:
                pass

        except Exception as e:
            print(10*"EXECPT in SQL insertino \n",e)


        
        try:
            if not _data:
                curseur.execute(to_execute, tuple(to_insert))
                print(to_execute)
                print(to_insert)
            else:
                curseur.execute(to_execute,tuple(to_insert))

        except Exception as e :
            print("the except is", e)

print("utils.py file loaded")


###### Automatise la recuperation des données 
def get_form_data_KC8(form_KC8, curseur):
        form_Sn_data = list()
        ## On recupère toutes les informations du formulaire form_Sn
        try:
            for field in form_KC8:            
                
                if  field.name != 'submit' and field.name != 'csrf_token':
                    
                    
                    # transform l'heure en format datetime pour insertion dans BDD
                    if 'Heure' in field.name:
                        date = [a.data.date() for a in form_KC8 if 'Date' in a.name][0]
                        correct_datetime = datetime.datetime.combine(date,field.data)
                        form_Sn_data.append(correct_datetime.strftime('%Y-%m-%d %H:%M:%S'))
                        
                    # anonymise technicien en changeant intilatiales par id
                    elif 'Initiales' in field.name:
                        
                        ## condition qui gere si la page contien un id de technicien à la place des initiales (mise à jour)
                        if field.data.isnumeric():
                            form_Sn_data.append(field.data)
                        else:
                            to_execute = "SELECT Technicien_id FROM Techniciens WHERE Initiales_tech=%s"
                            curseur.execute(to_execute,(field.data.upper(),))
                            form_Sn_data.append(curseur.fetchone()[0])

                    elif 'KC8_Visual_verification'in field.name or 'KC8_Analysis_validation' in field.name:
                        print(field.name)
                        form_Sn_data.append(1 if field.data == True else 0)
                        
                    # elif 'KC8_Analysis_validation' in field.name:
                    #     print(field.name)
                    #     form_Sn_data.append(1 if field.data == True else 0)

                    # si les données n'ont pas besion d'etre réagencé on les ajoute au formulaire
                    else:
                        form_Sn_data.append(field.data)
        except Exception as e:
            print(10*"EXECPT in parsing fields \n",e)

        to_insert = [str(data) for data in form_Sn_data]
 
 
        try:
            curseur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'Batch_KC8' ORDER BY ordinal_position;;")
            form_Sn_fields = [col[0] for col in curseur.fetchall()][1:]        
            to_execute =  f"INSERT INTO Batch_KC8 ({','.join([_ for _ in form_Sn_fields])}) VALUES ({','.join(['%s' for _ in to_insert])});"
        except Exception as e:
            print(10*"EXECPT in SQL insertion \n",e)

        try:
            curseur.execute(to_execute,tuple(to_insert))
        except Exception as e :
            print("EXCEPTION Upon executing SQL statement : \n==>", e)


def make_chart_for_dash_produits(last_n = 5):

    # because mac OS, need to set backend to agg
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # get values to be updated
    sc_UV = joblib.load("Data/sc_UV.joblib")
    indicator_UV=joblib.load("Data/indicator_UV.joblib")
    pca_UV=joblib.load("Data/pca_UV.joblib")
    weights_UV=joblib.load("Data/weights_UV.joblib")
    kmeans_UV=joblib.load("Data/kmeans_UV.joblib")

    sc_RAMAN=joblib.load("Data/sc_RAMAN.joblib")
    indicator_RAMAN=joblib.load("Data/indicator_RAMAN.joblib")
    pca_RAMAN=joblib.load("Data/pca_RAMAN.joblib")
    weights_RAMAN=joblib.load("Data/weights_RAMAN.joblib")
    kmeans_RAMAN=joblib.load("Data/kmeans_RAMAN.joblib")

    # make the API CALL
    response = requests.get('http://127.0.0.1:8000/OGD/')
    OGD_all = pd.DataFrame(response.json())
    last_5 = OGD_all['Batch_OGD_name'][-last_n:].values

    # fetch analysis
    UV_data=pd.DataFrame()
    RAMAN_data=pd.DataFrame()
    for OGD_n in last_5:
        try:
            response = requests.get(f'http://127.0.0.1:8000/analyses/name/{OGD_n}')
            analyses = pd.DataFrame(response.json())
            analyse_UV = analyses.loc[analyses.Analyse_subname == 'UV']
            analyse_RAMAN = analyses.loc[analyses.Analyse_subname == 'RAMAN']   
            UV_data = pd.concat([UV_data,analyse_UV])
            RAMAN_data = pd.concat([RAMAN_data,analyse_RAMAN])
        except:
            last_5 = last_5[~np.isin(last_5,[OGD_n])]
            last_n -= 1

    # prepare UV with dillution
    UV_spectra = pd.DataFrame(UV_data['Analyses_data'].tolist()).astype(float)
    dillution_factor = pd.Series(UV_data['Analyse_details'].apply(lambda x : int(x['dilution'].split(":")[1])),name='dillution_factor')
    UV_spectra_dill = UV_spectra.mul(dillution_factor.reset_index(drop=True),axis=0)

    # generate indicators
    indic_UV = (UV_spectra_dill['200'] / UV_spectra_dill['490'])[-last_n:]
    indic_UV.index=last_5
    indic_RAMAN = RAMAN_data['Analyse_details'].apply(lambda x : x['group1_indic1-ex D/G'])[-last_n:]
    indic_RAMAN.index=last_5

    # prepare sample with scaling and PCA transform
    sample_UV = pca_UV.transform(sc_UV.transform(UV_spectra_dill))
    sample_RAMAN = pca_RAMAN.transform(sc_RAMAN.transform(pd.DataFrame(RAMAN_data['Analyses_data'].tolist()).astype(float)))


# make figure
    f_UV, ax = plt.subplots(1,2,figsize=(6,3))
    ax[0].scatter(weights_UV[:,0],weights_UV[:,1], c=kmeans_UV.labels_)
    ax[0].scatter(sample_UV[:,0],sample_UV[:,1],c='red')
    ax[1].boxplot(x=indicator_UV,showfliers=False)
    ax[1].scatter([1 for i in range(last_n)],indic_UV,c='red')
    for label in indic_UV.index:
        ax[1].text(1.1,indic_UV[label],s=label)
    plt.suptitle('Analyse UV')
    img = io.BytesIO()
    plt.savefig(img,format='png')
    img.seek(0)
    img_UV = base64.b64encode(img.getvalue()).decode('utf-8')

    f_RAMAN, ax = plt.subplots(1,2,figsize=(6,3))
    ax[0].scatter(weights_RAMAN[:,0],weights_RAMAN[:,1], c=kmeans_RAMAN.labels_)
    ax[0].scatter(sample_RAMAN[:,0],sample_RAMAN[:,1], c='red')
    ax[1].boxplot(x=indicator_RAMAN)
    ax[1].scatter([1 for i in range(last_n)],indic_RAMAN,c='red')
    for label in indic_RAMAN.index:
        ax[1].text(1.01,indic_RAMAN[label],s=label)
    plt.suptitle('Analyse RAMAN')

    img = io.BytesIO()
    plt.savefig(img,format='png')
    img.seek(0)
    img_RAMAN = base64.b64encode(img.getvalue()).decode('utf-8')

    return img_UV, img_RAMAN


    
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
        