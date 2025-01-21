
# Import general
import os
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import json
import plotly
import plotly.express as px

# import for bdd - mysql
import mysql.connector as bdd_connect

# import pour flask
from flask import Flask, jsonify, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required

# import pour le back
from utils import get_form_data, get_form_data_KC8, get_matieres_premieres
from forms import *

# Instanciate app
app = Flask(__name__)
app.config['SECRET_KEY'] = "somesecretkey" # secret key stored in app == env variable to hide

# Database connexion for developpment
from models import get_db_connection

    ## Test de la connection à la bdd
try:
    BDD_CW, curseur = get_db_connection()
    print('connection à la BDD OK')
    curseur.close()
    BDD_CW.close()
except:
    print("Can't connect to BDD")




# import for managing users
from models import User
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

########################################################################################
############################### LOGIN #######################################
########################################################################################
from flask import request, redirect, url_for
from flask_login import login_user, logout_user, login_required

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm() # Create the form instance
    if form.validate_on_submit(): 


        email = form.email.data
        password = form.password.data
        name = form.name.data
        
        
        if User.find_by_email(email):
            flash('Cet email est déjà utilisé, choisir un email différent')
        else:
            User.create(email, password, name)
            return redirect(url_for('login'))
        
    return render_template("register.html", form=form) 

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Login logic here 
        user = User.find_by_email(email)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))  # Redirect to a success page
    
        else:
            if not user:
                flash("Email not found, you must register first")
            elif not user.check_password(password):
                flash('Incorrect password')
            
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


########################################################################################
########################################################################################
########################################################################################


import requests
####################### Page d'acceuil / Dashboard #######################
# @app.route("/")
@app.route("/acceuil", methods=["GET","POST"])
# @login_required
def index():
    response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/')
    K_name,C_name,THF_name = get_matieres_premieres(response.json())


    response = requests.get(f'http://127.0.0.1:8000/KC8/')
    KC8_name = response.json()
    return render_template("acceuil.html",
                        n_batch_K = K_name,
                        n_batch_C = C_name,
                        n_batch_THF = THF_name,
                        n_batch_KC8 = KC8_name,
                        )


@app.route("/Nouvelle_matiere_premiere", methods=['GET','POST'])
def Add_MP():

    form_MP = Form_Matieres_premieres()
    if form_MP.validate_on_submit():
        url = 'http://127.0.0.1:8000/matieres_premieres/'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            "MP_nom": request.form['MP_nom'],
            "MP_codeCW": request.form['MP_codeCW'],
            "MP_ref_fournisseur": request.form['MP_ref_fournisseur'],
            "MP_quantite": request.form['MP_quantite'],
            "MP_unite": request.form['MP_unite'],
            "MP_Analyses": "None"}

        response = requests.post(url, headers=headers, data=json.dumps(data))
        flash(json.dumps({'status': 'OK', 'response': response.json()}), 200)
        return redirect(url_for('Add_MP'))
    else:
        for field,errors in form_MP.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_MP, field).label.text}' : {error}")

    return render_template("Add_matiere_premiere.html",
                           Form_Matieres_premieres=form_MP)



@app.route("/Nouveau_batch_KC8", methods=['GET','POST'])
def Add_KC8():

    form_KC8 = Form_Batch_KC8()
    if form_KC8.validate_on_submit():
        url = 'http://127.0.0.1:8000/KC8/'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'}
        data = {
            "Batch_KC8_name": request.form['Batch_KC8_name'],
            "Batch_KC8_date": request.form['Batch_KC8_date'],
            "Batch_KC8_Technicien": request.form['Batch_KC8_Technicien'],
            "Batch_KC8_K_batch": request.form['Batch_KC8_K_batch'],
            "Batch_KC8_C_batch": request.form['Batch_KC8_C_batch'],
            "Batch_KC8_masse": request.form['Batch_KC8_masse'],
            "Batch_KC8_Temperature": request.form['Batch_KC8_Temperature'],
            "Batch_KC8_Agitation": request.form['Batch_KC8_Agitation'],
            "Batch_KC8_heure_debut": request.form['Batch_KC8_heure_debut'],
            "Batch_KC8_heure_fin": request.form['Batch_KC8_heure_fin'],
            "Batch_KC8_room_HR": request.form['Batch_KC8_room_HR'],
            "Batch_KC8_room_T": request.form['Batch_KC8_room_T'],
            "Batch_KC8_Analyses": "None"}

        response = requests.post(url, headers=headers, data=json.dumps(data))
        flash(json.dumps({'status': 'OK', 'response': response.json()}), 200)
        return redirect(url_for('Add_MP'))
    else:
        for field,errors in form_KC8.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_KC8, field).label.text}' : {error}")

    return render_template("Add_matiere_premiere.html",
                           Form_KC8=form_KC8)

app.route("/Nouveau_batch_KC8", methods=['GET','POST'])
def Add_OGD():

    form_OGD = Form_Batch_KC8()
    if form_OGD.validate_on_submit():
        url = 'http://127.0.0.1:8000/OGD/'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'}
        data = {
            "Batch_OGD_name": request.form['Batch_OGD_name'],
            "Batch_OGD_date": request.form['Batch_OGD_date'],
            "Batch_OGD_Technicien": request.form['Batch_OGD_Technicien'],
            "Batch_OGD_KC8_batch": request.form['Batch_OGD_KC8_batch'],
            "Batch_OGD_KC8_masse": request.form['Batch_OGD_KC8_masse'],
            "Batch_OGD_THF_batch": request.form['Batch_OGD_THF_batch'],
            "Batch_OGD_THF_Volume": request.form['Batch_OGD_THF_Volume'],
            "Batch_OGD_Temperature": request.form['Batch_OGD_Temperature'],
            "Batch_OGD_Agitation": request.form['Batch_OGD_Agitation'],
            "Batch_OGD_heure_debut": request.form['Batch_OGD_heure_debut'],
            "Batch_OGD_heure_fin": request.form['Batch_OGD_heure_fin'],
            "Batch_OGD_room_HR": request.form['Batch_OGD_room_HR'],
            "Batch_OGD_room_T": request.form['Batch_OGD_room_T'],
            "Batch_OGD_Analyses": "None"}

        response = requests.post(url, headers=headers, data=json.dumps(data))
        flash(json.dumps({'status': 'OK', 'response': response.json()}), 200)
        return redirect(url_for('Add_OGD'))
    else:
        for field,errors in form_OGD.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_OGD, field).label.text}' : {error}")

    return render_template("Add_matiere_premiere.html",
                           Form_OGD=form_OGD)

####################### Mise à jour Batch #######################

@app.route("/update_batch_info/<batch_name>",methods=["GET","POST"])
@login_required
def update_batch_info(batch_name):
    # if the id exist in the table we get all the values and populate the corresponding form

    # normally this execute only after displaying the form pre filled ==> so form_S0 is prefilled
    if request.method == 'POST':
        try:
            BDD_CW, curseur = connect_to_db()

            form_S0=Form_2023_S0()
            form_S1=Form_2023_S1()
            form_S2=Form_2023_S2()
            form_S3=Form_2023_S3()
            form_S4=Form_2023_S4()

            to_execute = f"SELECT * FROM Batch_OGD WHERE Batch_name = '{batch_name}'"
            curseur.execute(to_execute)
            data_form = curseur.fetchall()

            # on initialise le form 0 (table de jointure batch name/id)
            for i, field in enumerate(form_S0):
                if field.name in {'csrf_token', 'submit'}:
                    continue
                form_S0[field.name].data = data_form[0][i]
 
            if request.form.get('submit') == 'Submit_F1':
                get_form_data(1, form_S0, form_S1, curseur)
            elif request.form.get('submit') == 'Submit_F2':
                get_form_data(2, form_S0, form_S2, curseur)
            elif request.form.get('submit') == 'Submit_F3':
                get_form_data(3, form_S0, form_S3, curseur)
            elif request.form.get('submit') == 'Submit_F4':
                get_form_data(4, form_S0, form_S4, curseur)

            BDD_CW.commit()
            curseur.close()
            BDD_CW.close()


            # flash(f"Batch {_batch_name} etape {_batch_step} mis a jour avec succes")
            return redirect(url_for('Cahier_prod'))
        
        
        except Exception as e:
            
            print(10*"excep\n","execpt in update 'POST'")
            print("there was an error when POST of forms 2 or 3 or 4:\n",e)
            flash("there was an error when POST of forms 2 or 3 or 4:\n",e)

            return redirect(url_for('Cahier_prod'))

    else:
        print(10*"update > Else\n")
        try:
            BDD_CW, curseur = connect_to_db()

            batch_id = request.args.get('batch_id')

            # we populate the form with the data of the bdd
            form_S0=Form_2023_S0()
            form_S1=Form_2023_S1()
            form_S2=Form_2023_S2()
            form_S3=Form_2023_S3()
            form_S4=Form_2023_S4()
            _forms=[form_S0,form_S1,form_S2,form_S3,form_S4]
            _DBs = ['Batch_OGD','Etape1_lancement','Etape2_THF_Sedim_Centri','Etape3_Oxydation','Etape4_CtrlQualite'] 

            for j, form in enumerate(_forms):
                
                try:
                    # pour chaque form on va voir si il y a les données dans la BDD
                    to_execute = f"SELECT * FROM {_DBs[j]} WHERE Batch_id = '{batch_id}'"
                    curseur.execute(to_execute)
                    data_form = curseur.fetchall()

                    for i, field in enumerate(form):
                        if field.name in {'csrf_token', 'submit'}:
                            continue
                        _idx = i + (0 if _DBs[j] == 'Batch_OGD' else 1) # because first DB field of all other tables is the batch id not used in the form
                        _valeur = data_form[0][_idx]
                        form[field.name].data = _valeur
                    else:
                        pass

                except:
                    continue # if there are no batch id in the table we pass

            curseur.close()
            BDD_CW.close()
            return render_template("batch_info.html",
                            form_S0=form_S0, 
                            form_S1=form_S1,
                            form_S2=form_S2,
                            form_S3=form_S3,
                            form_S4=form_S4,
                            batch_name=batch_name)
        
        except Exception as e:
            print(10*"[*] went to except\n",e)
            curseur.close()
            BDD_CW.close()

            flash("There was a problem connecting to database",e)
            return redirect(url_for('index'))

# from utils import post_data_step1_fastapi
####################### Enrgistrer un nouveau Batch #######################
@app.route("/add_new_batch", methods=['GET','POST'])
@login_required
def Fill_form_2023():

    BDD_CW, curseur = connect_to_db()


    form_S0 = Form_2023_S0()
    form_S1 = Form_2023_S1()
    

    # validate form
    if form_S0.validate_on_submit() & form_S1.validate_on_submit():
        
        # Mise à jour table Batch_OGD
        data={'Step0_BatchName':form_S0.Step0_BatchName.data,
              'Step0_BatchTHF':form_S0.Step0_BatchTHF.data}
        
        response = requests.post('http://127.0.0.1:5001/step0/',json=data)
        # if response.status_code == 200:        
        #     batch_id = response.json()['Batch_id']
            
        #     # mise à jour de la table Step1
        #     post_data_step1_fastapi(batch_id,form_S1)
             

        # Mise à jour table Batch_OGD
        to_execute = "INSERT INTO Batch_OGD (Batch_name,Batch_THF_ref)\
                        VALUES (%s,%s)"
        curseur.execute(to_execute, (form_S0.Step0_BatchName.data,form_S0.Step0_BatchTHF.data))
        BDD_CW.commit()

        # Mise à jour de la Table Etape1_lancement
        get_form_data(1, form_S0, form_S1, curseur)
        BDD_CW.commit()

        # On reinitialise le form
        for field in form_S1:
            if field.name != 'submit':
                field.data = ''
        # On ferme la connection
        curseur.close()
        BDD_CW.close()

        flash(f"Soumission du batch {form_S0.Step0_BatchName.data} avec succes")
        return redirect(url_for('Cahier_prod'))

    # handle error from filling in the form
    else:
        for field,errors in form_S1.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_S1, field).label.text}' : {error}")

    return render_template("Fill_form_2023.html",
                           form_S0=form_S0, 
                           form_S1=form_S1)


import requests
####################### Apercu de tous les Batch #######################
@app.route("/Cahier_prod", methods=['GET','POST'])
@login_required
def Cahier_prod():
    
    response = requests.get(f'http://127.0.0.1:5001/step0/')
    
    if response.status_code == 200:
        print(response.json()[0])
        data = [(a['Batch_id'],a['Batch_name']) for a in response.json()][::-1]
        return render_template("Cahier_prod.html",batch_list=data)

    elif response.status_code != 200:
        return jsonify({"error":"failed to get bdd"}), response.status_code

    elif request == 'POST':
        return redirect(url_for('update_batch_info'),batch_id=request.arg.get('batch_id'))

    else :
        return(redirect(url_for('acceuil')))


####################### Ajout informations complete de Batch #######################
@app.route("/FillIn_DB_2023", methods=['GET','POST'])
@login_required
def FillIn_DB_2023():

    BDD_CW, curseur = connect_to_db()

    form_S0 = Form_2023_S0()
    form_S1 = Form_2023_S1()
    form_S2 = Form_2023_S2()
    form_S3 = Form_2023_S3()
    form_S4 = Form_2023_S4()

    # validate form
    if form_S1.validate_on_submit() and form_S2.validate_on_submit() and form_S3.validate_on_submit() \
        and form_S4.validate_on_submit() :
        # Mise à jour table Batch_OGD
        to_execute = "INSERT INTO Batch_OGD (Batch_name,Batch_THF_ref)\
                        VALUES (%s,%s)"
        curseur.execute(to_execute, (form_S0.Step0_BatchName.data,form_S0.Step0_BatchTHF.data))
        BDD_CW.commit()

        get_form_data(1, form_S0, form_S1, curseur)
        get_form_data(2, form_S0, form_S2, curseur)
        get_form_data(3, form_S0, form_S3, curseur)
        get_form_data(4, form_S0, form_S4, curseur)

        BDD_CW.commit()
        curseur.close()
        BDD_CW.close()

        flash(f"Soumission du batch {form_S0.Step0_BatchName.data} avec succes")
        return redirect(url_for('FillIn_DB_2023'))


    # handle error from filling in the form
    else:
        for field,errors in form_S1.errors.items():
            for error in errors:
                flash(f"Erreur S1 pour le champ '{getattr(form_S1, field).label.text}' : {error}")
        for field,errors in form_S2.errors.items():
            for error in errors:
                flash(f"Erreur S2 pour le champ '{getattr(form_S2, field).label.text}' : {error}")        
        for field,errors in form_S3.errors.items():
            for error in errors:
                flash(f"Erreur S3 pour le champ '{getattr(form_S3, field).label.text}' : {error}")
        for field,errors in form_S4.errors.items():
            for error in errors:
                flash(f"Erreur S4 pour le champ '{getattr(form_S4, field).label.text}' : {error}")

    return render_template("FillIn_DB_2023.html",
                           form_S0=form_S0, 
                           form_S1=form_S1,
                           form_S2=form_S2,
                           form_S3=form_S3,
                           form_S4=form_S4)




###############################################################################
########################## MaJ add 4 batch ####################################
###############################################################################

@app.route("/add_4_batch", methods=['GET','POST'])
@login_required
def Fill_form_2023_X4():

    BDD_CW, curseur = connect_to_db()


    form_S0_1 = Form_2023_S0()
    form_S0_2 = Form_2023_S0()
    form_S0_3 = Form_2023_S0()
    form_S0_4 = Form_2023_S0()
    
    form_S1_1 = Form_2023_S1()
    form_S1_2 = Form_2023_S1()
    form_S1_3 = Form_2023_S1()
    form_S1_4 = Form_2023_S1()
    
    # validate form
    if form_S0_1.validate_on_submit() & form_S0_2.validate_on_submit() & form_S0_3.validate_on_submit() & form_S0_4.validate_on_submit()\
    & form_S1_1.validate_on_submit() & form_S1_2.validate_on_submit() & form_S1_3.validate_on_submit() & form_S1_4.validate_on_submit():

        # Mise à jour table Batch_OGD            
        to_execute = "INSERT INTO Batch_OGD (Batch_name,Batch_THF_ref)\
                        VALUES (%s,%s)"             
        for i in range(4):
            form_S0 = f"form_S0_{i+1}"
            curseur.execute(to_execute,(locals()[form_S0].Step0_BatchName.data, locals()[form_S0].Step0_BatchTHF.data))
            BDD_CW.commit()



        # Mise à jour de la Table Etape1_lancement
        for i in range(4):
            form_S0 = f"form_S0_{i+1}"
            form_S1 = f"form_S1_{i+1}"
            get_form_data(1, locals()[form_S0], locals()[form_S1], curseur)
            BDD_CW.commit()

        # On reinitialise les form
        for i in range(4):
            form_S1 = f"form_S1_{i+1}"
            for field in locals()[form_S1]:
                if field.name != 'submit':
                    field.data = ''
        # On ferme la connection
        curseur.close()
        BDD_CW.close()

        flash(f"Soumission des batch avec succes")
        return redirect(url_for('Cahier_prod'))

    # handle error from filling in the form
    else:
        for i in range(4):
            form_S1 = f"form_S1_{i+1}"
            
            for field,errors in locals()[form_S1].errors.items():
                for error in errors:
                    flash(f"Erreur pour le champ '{getattr(locals()[form_S1], field).label.text}' : {error}")

    return render_template("Fill_form_2023_X4.html",
                           form_S0_1=form_S0_1,
                           form_S0_2=form_S0_2,
                           form_S0_3=form_S0_3,
                           form_S0_4=form_S0_4, 
                           form_S1_1=form_S1_1,
                           form_S1_2=form_S1_2,
                           form_S1_3=form_S1_3,
                           form_S1_4=form_S1_4,
                           datetime=datetime,
                           str=str)





####################### Ajout informations complete de Batch #######################
@app.route("/FillIn_DB_2023_X4", methods=['GET','POST'])
@login_required
def FillIn_DB_2023_X4():

    BDD_CW, curseur = connect_to_db()

    form_S0_1, form_S0_2, form_S0_3, form_S0_4 = Form_2023_S0(), Form_2023_S0(), Form_2023_S0(), Form_2023_S0()
    form_S1_1, form_S1_2, form_S1_3, form_S1_4 = Form_2023_S1(), Form_2023_S1(), Form_2023_S1(), Form_2023_S1()
    form_S2_1, form_S2_2, form_S2_3, form_S2_4 = Form_2023_S2(), Form_2023_S2(), Form_2023_S2(), Form_2023_S2()
    form_S3_1, form_S3_2, form_S3_3, form_S3_4 = Form_2023_S3(), Form_2023_S3(), Form_2023_S3(), Form_2023_S3()
    form_S4_1, form_S4_2, form_S4_3, form_S4_4 = Form_2023_S4(), Form_2023_S4(), Form_2023_S4(), Form_2023_S4()

    # validate form
    if form_S1_1.validate_on_submit() and form_S2_1.validate_on_submit() and form_S3_1.validate_on_submit() \
        and form_S4_1.validate_on_submit() :
  
        # Mise à jour table Batch_OGD            
        to_execute = "INSERT INTO Batch_OGD (Batch_name,Batch_THF_ref)\
                        VALUES (%s,%s)"             
        for i in range(4):
            form_S0 = f"form_S0_{i+1}"
            curseur.execute(to_execute,(locals()[form_S0].Step0_BatchName.data, locals()[form_S0].Step0_BatchTHF.data))
            BDD_CW.commit()


        # Mise à jour de la Table Etape1_lancement
        for n in range(4):
            form_S0 = f"form_S0_{n+1}"
            
            for m in range(4):
                form_Sn_m = f"form_S{m+1}_{n+1}"
                
                
                get_form_data(m, locals()[form_S0], locals()[form_Sn_m], curseur)
          
        BDD_CW.commit()
        curseur.close()
        BDD_CW.close()

        flash(f"Soumission des batchs avec succes")
        return redirect(url_for('FillIn_DB_2023_X4'))


     
    # handle error from filling in the form
    else:
        for n in range(4):
            form_S0 = f"form_S0_{n+1}"
            
            for m in range(5):
                form_Sn_m = f"form_S{m}_{n+1}"
                for field,errors in locals()[form_Sn_m].errors.items():
                    for error in errors:
                        flash(f"Erreur S3 pour le champ '{getattr(locals()[form_Sn_m], field).label.text}' : {error}")


    return render_template("FillIn_DB_2023_X4.html",
                           form_S0_1=form_S0_1, form_S0_2=form_S0_2, form_S0_3=form_S0_3, form_S0_4=form_S0_4,
                           form_S1_1=form_S1_1, form_S1_2=form_S1_2, form_S1_3=form_S1_3, form_S1_4=form_S1_4,
                           form_S2_1=form_S2_1, form_S2_2=form_S2_2, form_S2_3=form_S2_3, form_S2_4=form_S2_4,
                           form_S3_1=form_S3_1, form_S3_2=form_S3_2, form_S3_3=form_S3_3, form_S3_4=form_S3_4,
                           form_S4_1=form_S4_1, form_S4_2=form_S4_2, form_S4_3=form_S4_3, form_S4_4=form_S4_4,
                           datetime=datetime, str=str)






####################### Enrgistrer un nouveau Batch #######################
@app.route("/add_batch_KC8", methods=['GET','POST'])
@login_required
def Fill_form_KC8():

    BDD_CW, curseur = connect_to_db()


    form_KC8 = Form_KC8()

    # validate form
    if form_KC8.validate_on_submit():

        # Mise à jour table Batch_KC8
        get_form_data_KC8(form_KC8, curseur) 
        BDD_CW.commit()

        # On reinitialise le form
        for field in form_KC8:
            if field.name != 'submit':
                field.data = ''
        # On ferme la connection
        curseur.close()
        BDD_CW.close()
        
        flash(f"Soumission du batch {form_KC8.Batch_KC8_name.data} avec succes")
        return redirect(url_for('Cahier_prod'))

    # handle error from filling in the form
    else:
        for field,errors in form_KC8.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_KC8, field).label.text}' : {error}")

    return render_template("Add_Batch_KC8.html",
                           form_KC8=form_KC8,
                           datetime=datetime, str=str)

















# Etabli un sevreur de developpement  /!\  ==> ue production serveur like WGSI Gunicorn for Production !!!!
# from gunicorn import run

if __name__ == "__main__":

    ### Doctest for app.py
    import doctest
    doctest.testmod()
    ### -----------------


    app.run(debug=True, host='0.0.0.0', port=4000) 
    # run("app:app", host="0.0.0.0", port=5000, workers=1)