import datetime
from flask import flash
import requests




def get_matieres_premieres(response):

    print(response)
    K_name='potasiim#b9286'
    
    C_name='carbon#30789'

    THF_name='THF#986'

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
