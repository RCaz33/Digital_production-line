import datetime
from flask import flash
import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
import joblib
import io
import base64


def update_stocks_K_C(data):
        headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'}
        status=dict()
        # update stock of K 
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_KC8_K_batch"]}')
        status['get_K'] = response.status_code
        updated_batch = response.json()
        updated_batch['MP_quantite'] = int(updated_batch['MP_quantite'] - (39/(39+(8*12))*float(data['Batch_KC8_masse'])))
        response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch["MP_id"]}', headers=headers, data=json.dumps(updated_batch))
        status['post_K'] = response.status_code
        
        # update stock of C
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_KC8_C_batch"]}')
        updated_batch = response.json()
        status['get_C'] = response.status_code
        updated_batch['MP_quantite'] = updated_batch['MP_quantite'] - ((8*12)/(39+(8*12))*float(data['Batch_KC8_masse']))
        response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch["MP_id"]}', headers=headers, data=json.dumps(updated_batch))
        status['post_C'] = response.status_code

        return status




def populate_form(form,response):
    data = response.json()
    for field in form:
        for k,v in data.items():
            if field.name == k:
                if  '_date' in field.name :
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
    last_5 = OGD_all['Batch_OGD_name'][-last_n:]

    # fetch analysis
    UV_data=pd.DataFrame()
    RAMAN_data=pd.DataFrame()
    for OGD_n in last_5:
        response = requests.get(f'http://127.0.0.1:8000/analyses/name/{OGD_n}')
        analyses = pd.DataFrame(response.json())
        analyse_UV = analyses.loc[analyses.Analyse_subname == 'UV']
        analyse_RAMAN = analyses.loc[analyses.Analyse_subname == 'RAMAN']   
        UV_data = pd.concat([UV_data,analyse_UV])
        RAMAN_data = pd.concat([RAMAN_data,analyse_RAMAN])

    # prepare UV with dillution
    UV_spectra = pd.DataFrame(UV_data['Analyses_data'].tolist()).astype(float)
    dillution_factor = pd.Series(UV_data['Analyse_details'].apply(lambda x : int(x['dillution'].split(":")[1])),name='dillution_factor')
    UV_spectra_dill = UV_spectra.mul(dillution_factor.reset_index(drop=True),axis=0)

    # geenrate indicators
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

