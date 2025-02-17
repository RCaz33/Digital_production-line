
# Import general
import os
import io
import base64
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import plotly
import plotly.express as px
import config



# import for bdd - mysql
import mysql.connector as bdd_connect

# import pour flask
from flask import Flask, jsonify, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required

# import pour le back
from utils import make_chart_for_dash_produits,update_stocks_K_C, populate_form, get_last_10_batch, get_form_data, get_form_data_KC8, get_matieres_premieres
from forms import *
# Instanciate app
app = Flask(__name__)
app.config['SECRET_KEY'] = "somesecretkey" # secret key stored in app == env variable to hide



# enable CSRF protection globally for a Flask app
from flask_wtf.csrf import CSRFProtect, generate_csrf
csrf = CSRFProtect(app)



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


# configure default batch
global default_batch
response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/')

K_name,C_name,THF_name = get_matieres_premieres(response)
default_batch = dict({'K':K_name,'C':C_name,'THF':THF_name})

response = requests.get(f'http://127.0.0.1:8000/KC8/')
KC8_all = pd.DataFrame(response.json())
KC8_batch = KC8_all.loc[KC8_all.Batch_KC8_id==np.max(KC8_all.Batch_KC8_id),'Batch_KC8_name'].values[0]
default_batch['KC8'] = KC8_batch



@app.route("/")
@app.route("/Materiaux", methods=["GET","POST"])
# @login_required
def acceuil_materiaux():

    global default_batch

    # batch without ending time
    response = requests.get(f'http://127.0.0.1:8000/OGD/')
    OGD_all = pd.DataFrame(response.json())
    OGD_en_cours = OGD_all.loc[OGD_all.Batch_OGD_heure_fin.isnull(),['Batch_OGD_name','Batch_OGD_heure_debut']].values

    response = requests.get(f'http://127.0.0.1:8000/KC8/')
    KC8_all = pd.DataFrame(response.json())
    KC8_en_cours = KC8_all.loc[KC8_all.Batch_KC8_heure_fin.isnull(),['Batch_KC8_name','Batch_KC8_heure_debut']].values


    # get stock matieres premieres
    stock_MP = requests.get(f'http://127.0.0.1:8000/matieres_premieres/')
    stock_MP = pd.DataFrame(stock_MP.json())[['MP_ref_fournisseur','MP_quantite']]
    stock_MP.index = stock_MP['MP_ref_fournisseur']
    stock_MP.drop(columns='MP_ref_fournisseur',inplace=True)
    stock_MP = stock_MP.T.to_dict()
    Stock_KC8 = requests.get(f'http://127.0.0.1:8000/KC8/name/{default_batch["KC8"]}')

    print(Stock_KC8)
    return render_template("acceuil_materiaux.html",
                        n_batch_K = default_batch['K'],
                        stock_K = stock_MP[default_batch['K']]['MP_quantite'],
                        n_batch_C = default_batch['C'],
                        stock_C = stock_MP[default_batch['C']]['MP_quantite'],
                        n_batch_THF = default_batch['THF'],
                        stock_THF = stock_MP[default_batch['THF']]['MP_quantite'],
                        n_batch_KC8 = default_batch['KC8'],
                        stock_KC8 = Stock_KC8.json()['Batch_KC8_masse'],
                        OGD_en_cours = OGD_en_cours,
                        KC8_en_cours = KC8_en_cours)



@app.route("/Nouvelle_matiere_premiere", methods=['GET','POST'])
def Add_MP():

    form_MP = Form_Matieres_premieres()

    if form_MP.validate_on_submit():
        url = 'http://127.0.0.1:8000/matieres_premieres/'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        MP_date_reception_str = request.form['MP_date_reception']
        MP_date_reception = datetime.datetime.strptime(MP_date_reception_str, '%d/%m/%y')
        data = {
            "MP_nom": request.form['MP_nom'],
            "MP_codeCW": config.codes_MP_CW[request.form['MP_nom']],
            "MP_ref_fournisseur": request.form['MP_ref_fournisseur'],
            "MP_quantite": request.form['MP_quantite'],
            "MP_date_reception": MP_date_reception.isoformat(),
            "MP_unite": request.form['MP_unite'],
            "MP_Analyses": "None"}

        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            flash("Nouvelle matière première ajoutée avec succès")
        else:
            flash(json.dumps(response.json()))
        return redirect(url_for('Add_MP'))
    else:
        for field,errors in form_MP.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_MP, field).label.text}' : {error}")
    
    form_MP.MP_date_reception.data = datetime.datetime.now()

    MP = pd.DataFrame(requests.get(f'http://127.0.0.1:8000/matieres_premieres/').json())
    batch_C = MP.loc[MP.MP_nom=='Carbone',['MP_ref_fournisseur','MP_quantite','MP_unite']].values
    batch_K = MP.loc[MP.MP_nom=='Potassium',['MP_ref_fournisseur','MP_quantite','MP_unite']].values
    batch_THF = MP.loc[MP.MP_nom=='THF',['MP_ref_fournisseur','MP_quantite','MP_unite']].values
    return render_template("Add_matiere_premiere.html",
                           Form_Matieres_premieres=form_MP,
                           batch_C=batch_C[::-1],
                           batch_K=batch_K[::-1],
                           batch_THF=batch_THF[::-1],
                           Inspect=False)



@app.route("/Inspecter_matiere_premiere/<MP_ref_fournisseur>", methods=['GET', 'POST'])
def Inspect_MP(MP_ref_fournisseur):
    print(MP_ref_fournisseur)
    headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'}
    
    response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{MP_ref_fournisseur}', headers=headers)
    form_MP = Form_Matieres_premieres()

    data = response.json()
    for field in form_MP:
        if field.name in ['csrf_token','submit']:
            continue
        elif 'date' in field.name:
            form_MP[field.name].data = datetime.datetime.strptime(data[field.name], '%Y-%m-%dT%H:%M:%S')
        else:
            form_MP[field.name].data = data[field.name]
        
    # récupère toute les analyses associées à un batch
    # response = requests.get(f'http://
    return render_template("Add_matiere_premiere.html",
                           Inspect = True,
                           Form_Matieres_premieres=form_MP)



#################################################################
####################### Nouveau Batch ###########################
#################################################################




@app.route("/Nouveau_batch_KC8", methods=['GET','POST'])
def Add_KC8():
    form_KC8 = Form_Batch_KC8()
    url = 'http://127.0.0.1:8000/KC8/'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'}
    

    if form_KC8.validate_on_submit():

        # Format datetime
        KC8_date_debut = request.form['Batch_KC8_date']
        KC8_date_debut = datetime.datetime.strptime(KC8_date_debut, '%d/%m/%y')
        KC8_heure_debut = request.form['Batch_KC8_heure_debut']
        KC8_heure_debut = datetime.datetime.strptime(KC8_heure_debut, '%H:%M').time()
        KC8_heure_debut = datetime.datetime.combine(KC8_date_debut.date(),KC8_heure_debut )

        data = {
            "Batch_KC8_name": request.form['Batch_KC8_name'],
            "Batch_KC8_date": KC8_date_debut.isoformat(),
            "Batch_KC8_Technicien": request.form['Batch_KC8_Technicien'],
            "Batch_KC8_K_batch": request.form['Batch_KC8_K_batch'],
            "Batch_KC8_C_batch": request.form['Batch_KC8_C_batch'],
            "Batch_KC8_masse": request.form['Batch_KC8_masse'],
            "Batch_KC8_Temperature": request.form['Batch_KC8_Temperature'],
            "Batch_KC8_Agitation": request.form['Batch_KC8_Agitation'],
            "Batch_KC8_heure_debut": KC8_heure_debut.isoformat(),
            "Batch_KC8_heure_fin": None,
            "Batch_KC8_room_HR": request.form['Batch_KC8_room_HR'],
            "Batch_KC8_room_T": request.form['Batch_KC8_room_T'],
            "Batch_KC8_Stock" : request.form['Batch_KC8_masse'],
            "Batch_KC8_Analyses": "None"}

        print(data)
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print('sucessssss')
            flash(json.dumps({'Problem connecting to the database': response.json()}))
        else:
            flash(json.dumps({'status': 'OK'}))

        # Update Matieres premieres
        print(update_stocks_K_C(data)) ### REMAKE CALCULATION WITH FABIEN !!!
        # data = request.get_json()
        # result_K = data.get('result_K')
        # result_C = data.get('result_C')
        # print(result_K,result_C)


        return redirect(url_for('acceuil_materiaux'))
    else:
        for field,errors in form_KC8.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_KC8, field).label.text}' : {error}")


    # pre-filling with today and last saved batches
    response = requests.get(url+'last', headers=headers)
    # make batch KC8 ONE more than the last one --> TO DO : here is the last KC8 batch appears
    # make guard that the new batch of KC8 should not be a batch that already exiosts
    form_KC8.Batch_KC8_name.data = response.json()['Batch_KC8_name']
    form_KC8.Batch_KC8_date.data = datetime.datetime.now()
    form_KC8.Batch_KC8_heure_debut.data = datetime.datetime.now()
    form_KC8.Batch_KC8_K_batch.data = default_batch['K']
    form_KC8.Batch_KC8_C_batch.data = default_batch['C']
    
     # Get the data
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    # Batch OGD existants
    response = requests.get(url='http://127.0.0.1:8000/KC8/',headers=headers)
    form_KC8.Batch_KC8_name.validators[0].values = [a['Batch_KC8_name'] for a in response.json()]
    
    # calculate K et C
    # form_calculate_K_C = Form_calculate_K_C()

    return render_template("Add_batch_KC8.html",
                           Form_KC8=form_KC8)

@app.route("/Nouveau_batch_OGD", methods=['GET','POST'])
def Add_OGD():
    global default_batch
    form_OGD = Form_Batch_OGD()
    if form_OGD.validate_on_submit():

        print(10*"\n ENTER VALIDATE ON SUBMIT")
        url = 'http://127.0.0.1:8000/OGD/'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'}
        

        OGD_date_debut = request.form['Batch_OGD_date']
        OGD_date_debut = datetime.datetime.strptime(OGD_date_debut, '%d/%m/%y')
        OGD_heure_debut = request.form['Batch_OGD_heure_debut']
        OGD_heure_debut = datetime.datetime.strptime(OGD_heure_debut, '%H:%M').time()
        OGD_heure_debut = datetime.datetime.combine(OGD_date_debut.date(),OGD_heure_debut )

        data = {
            "Batch_OGD_name": request.form['Batch_OGD_name'],
            "Batch_OGD_date": OGD_date_debut.isoformat(),
            "Batch_OGD_Technicien": request.form['Batch_OGD_Technicien'],
            "Batch_OGD_KC8_batch": request.form['Batch_OGD_KC8_batch'],
            "Batch_OGD_KC8_masse": request.form['Batch_OGD_KC8_masse'],
            "Batch_OGD_THF_batch": request.form['Batch_OGD_THF_batch'],
            "Batch_OGD_THF_Volume": request.form['Batch_OGD_THF_Volume'],
            "Batch_OGD_Temperature": request.form['Batch_OGD_Temperature'],
            "Batch_OGD_Agitation": request.form['Batch_OGD_Agitation'],
            "Batch_OGD_heure_debut": OGD_heure_debut.isoformat(),
            "Batch_OGD_heure_fin": None,
            "Batch_OGD_room_HR": request.form['Batch_OGD_room_HR'],
            "Batch_OGD_room_T": request.form['Batch_OGD_room_T'],
            "Batch_OGD_Analyses": "None"}
        print(data)
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            flash(json.dumps('Probleme de connection à la base de donnée'))
        else:
            flash(json.dumps({'status': 'OK'}))

        try:
            # update stock of KC8 
            response = requests.get(f'http://127.0.0.1:8000/KC8/name/{data["Batch_OGD_KC8_batch"]}')
            updated_batch = response.json()
            updated_batch['Batch_KC8_masse'] = int(updated_batch['Batch_KC8_masse'] - int(data['Batch_OGD_KC8_masse']))
            response2 = requests.post(f'http://127.0.0.1:8000/KC8/update/{updated_batch["Batch_KC8_id"]}', headers=headers, data=json.dumps(updated_batch))

            # update stock of THF
            response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_OGD_THF_batch"]}')
            updated_batch = response.json()
            updated_batch['MP_quantite'] = updated_batch['MP_quantite'] - int(data['Batch_OGD_THF_Volume'])
            response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch["MP_id"]}', headers=headers, data=json.dumps(updated_batch))
        except:
            flash("Problème lors de la mise à jour des stocks de la base de données",response.status_code)

        return redirect(url_for('index'))
    else:
        print(10*"\n ELSE NOT VALIDATE ON SUBMIT")
        for field,errors in form_OGD.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_OGD, field).label.text}' : {error}")
            return render_template("Add_batch_OGD.html",
                           Form_OGD=form_OGD)
        
    # formate le nom de batch OGD avec la semaine (today.isocalendar()[1]:02)
    today = datetime.datetime.now()
    form_OGD.Batch_OGD_name.data = f"OGD{str(today.year)[-2:]}{today.isocalendar()[1]:02}"
    form_OGD.Batch_OGD_date.data = today

    form_OGD.Batch_OGD_heure_debut.data = today
    form_OGD.Batch_OGD_KC8_batch.data = default_batch['KC8']
    form_OGD.Batch_OGD_THF_batch.data = default_batch['THF']

    # Get the data
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    # Batch OGD existants
    response = requests.get(url='http://127.0.0.1:8000/OGD/',headers=headers)
    form_OGD.Batch_OGD_name.validators[0].values = [a['Batch_OGD_name'] for a in response.json()]
    # Batch KC8 existants
    response = requests.get(url='http://127.0.0.1:8000/KC8/',headers=headers)
    form_OGD.Batch_OGD_KC8_batch.choices = [a['Batch_KC8_name'] for a in response.json() if a['Batch_KC8_masse'] > 0][:-10:-1]
    return render_template("Add_batch_OGD.html",
                           Form_OGD=form_OGD)



@app.route("/Nouveau_batch_produit/<produit>", methods=['GET','POST'])
def Add_Produit(produit):
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    form_produit = Form_Produit()
    
    if form_produit.validate_on_submit():
        url = 'http://127.0.0.1:8000/Produit/'
        Produit_date = request.form['Batch_Produit_date']
        Produit_date = datetime.datetime.strptime(Produit_date, '%d/%m/%y')
        data = {
            "Batch_Produit_ref_CW": request.form['Batch_Produit_ref_CW'],
            "Batch_Produit_date": Produit_date.isoformat(),
            "Batch_Produit_Technicien": request.form['Batch_Produit_Technicien'],
            "Batch_Produit_OGD_batch": request.form['Batch_Produit_OGD_batch'],
            "Batch_Produit_OGD_Qte": request.form['Batch_Produit_OGD_Qte'],
            "Batch_Produit_additif_bacth": request.form['Batch_Produit_additif_bacth'],
            "Batch_Produit_additif_Qte": request.form['Batch_Produit_additif_Qte'],
            "Batch_Produit_Analyses": "None",}

        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            flash(json.dumps({'Problem connecting to the database': response.json()}))
        else:
            flash(json.dumps({'status': 'OK'}))

        # update stock of OGD 
        response = requests.get(f'http://127.0.0.1:8000/OGD/name/{data["Batch_Produit_OGD_batch"]}')
        updated_batch = response.json()
        updated_batch['Batch_Produit_OGD_Qte'] = int(updated_batch['Batch_Produit_OGD_Qte'] - int(data['Batch_Produit_OGD_Qte']))
        response2 = requests.post(f'http://127.0.0.1:8000/Produit/update/{updated_batch["Batch_Produit_id"]}', headers=headers, data=json.dumps(updated_batch))

        # update stock of stabilisant
        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/name/{data["Batch_Produit_stabilisant_bacth"]}')
        updated_batch = response.json()
        updated_batch['MP_quantite'] = updated_batch['MP_quantite'] - int(data['Batch_Produit_stabilisant_Qte'])
        response = requests.post(f'http://127.0.0.1:8000/matieres_premieres/update/{updated_batch["MP_id"]}', headers=headers, data=json.dumps(updated_batch))

        # UPDATE ENVOI IF produit_desc with ref from produit
        if Envoi_id:
            requests.get()

        return redirect(url_for('index'))
    else:
        for field,errors in form_produit.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_produit, field).label.text}' : {error}")

    # populate form
    today = datetime.datetime.now()
    form_produit.Batch_Produit_date.data = today

    # try:     # test if the making the batch is coming from a request for a client
    #     Envoi_id = request.args.get('envoie')
    #     print(50*"\n")
    #     print("envoi",Envoi_id)
    #     response = requests.get(url=f'http://127.0.0.1:8000/Envoi/id/{Envoi_id}',headers=headers)
    #     envoi_ref = pd.DataFrame(response.json())
    #     print(envoi_ref)
    #     # ecrit le nom de batch
    #     form_produit.Batch_OGD_name.data = f"OGD{str(today.year)[-2:]}{today.isocalendar()[1]:02}"
    #     # calulate mass of OGD for given amount of product
    #     form_produit.Batch_Produit_OGD_Qte.data = 2
    #     # calulate mass of additif for given amount of product
    #     form_produit.Batch_Produit_additif_Qte.data = 3
    #     # print(produit_desc.replace("'", '"'))
    #     # flash(f'Produit pour {client.split("'")[3]}')
    # except:
    #     flash('Produit pour étagère')
 
    # formate le nom de batch produit avec la semaine (today.isocalendar()[1]:02)
    # form_produit.Batch_Produit_date.data = today
    # response = requests.get(url='OGD')
    # Batch_Produit_OGD_batch
    # form_produit.Batch_Produit_OGD_batch.data = 
    # form_produit.Batch_OGD_THF_batch.data = default_batch['THF']

    # CALCULATE FOR A GIVEN PRODUCT THE QUANTITIES OF ADDITIVE BASE ON OGD
    type_product=None
    if type_product == 'W':
        form_produit.Batch_Produit_stabilisant_bacth.data = 'W'
        form_produit.Batch_Produit_stabilisant_Qte.data = 1
    elif type_product == '...':
        form_produit.Batch_Produit_stabilisant_bacth.data = '...'
        form_produit.Batch_Produit_stabilisant_Qte.data = 1

    form_produit.Batch_Produit_OGD_batch.choices = 'request on OGD'


    Envoi_id = request.args.get('envoie')
    print(5*"\n")
    print("envoi",Envoi_id)


    return render_template("Add_batch_produit.html",
                           Form_Produit=form_produit,
                           produit=produit)


@app.route("/Update_default_batch", methods=['GET','POST'])
def Update_default_batch():
    global default_batch

    last_10_K, last_10_C, last_10_THF, last_10_KC8 = get_last_10_batch()

    if request.method == 'POST':

        print(10*"vv\n")
        print(request.form.get('n_batch_K'))

        default_batch['K']= request.form.get('n_batch_K')
        print(default_batch['K'])
        default_batch['C']= request.form.get('n_batch_C')
        default_batch['THF']= request.form.get('n_batch_THF')
        default_batch['KC8']= request.form.get('n_batch_KC8')
        return redirect(url_for('acceuil_materiaux')) 

    csrf_token = generate_csrf()
    return render_template("Update_default_batch.html",
                           last_10_K=last_10_K,
                           last_10_C=last_10_C,
                           last_10_THF=last_10_THF,
                           last_10_KC8=last_10_KC8,
                           csrf_token=csrf_token)



#################################################################
####################### Mise à jour Batch #######################
#################################################################

@app.route("/MaJ_batch_OGD/<batch_name>",methods=["GET","POST"])
# @login_required
def update_batch_OGD(batch_name):
    # get Batch info
    url = 'http://127.0.0.1:8000/OGD/'
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'}
    response = requests.get(url+f'name/{batch_name}',headers=headers)
    id_batch = response.json()['Batch_OGD_id']    

    # fill-in value with data from db
    form_OGD = Form_Batch_OGD()
    form_OGD = populate_form(form_OGD, response)
    
    if request.method == 'POST': 
        data = dict()
        data['Batch_OGD_id'] = id_batch
        for field in form_OGD:
            if field.name == 'csrf_token':
                continue
            elif 'date' in field.name or 'heure' in field.name:
                data[field.name] = form_OGD[field.name].data.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                data[field.name] = form_OGD[field.name].data

        response = requests.post(url+f'update/{id_batch}', headers=headers, data=json.dumps(data))
        flash(json.dumps({'status': response.status_code}), 200)
        return redirect(url_for('index')) 
    
    # reformater les datetime pour affichage correct dans le form
    form_OGD['Batch_OGD_date'].data = form_OGD['Batch_OGD_date'].data.strftime(format='%d/%m/%y')
    form_OGD['Batch_OGD_heure_debut'].data = form_OGD['Batch_OGD_heure_debut'].data.strftime(format='%H:%M')
    return render_template("MaJ_batch_OGD.html",
                           Form_OGD = form_OGD)


@app.route("/MaJ_batch_KC8/<batch_name>",methods=["GET","POST"])
# @login_required
def update_batch_KC8(batch_name):
    # get Batch info
    url = 'http://127.0.0.1:8000/KC8/'
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'}
    response = requests.get(url+f'name/{batch_name}',headers=headers)
    id_batch = response.json()['Batch_KC8_id']    

    # fill-in value with data from db
    form_KC8 = Form_Batch_KC8()
    form_KC8 = populate_form(form_KC8, response)
    
    if request.method == 'POST':
        data = dict()
        data['Batch_KC8_id'] = id_batch
        for field in form_KC8:
            if field.name == 'csrf_token':
                continue
            elif 'date' in field.name or 'heure' in field.name:
                data[field.name] = form_KC8[field.name].data.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                data[field.name] = form_KC8[field.name].data

        response = requests.post(url+f'update/{id_batch}', headers=headers, data=json.dumps(data))
        flash(json.dumps({'status': response.status_code}), 200)
        return redirect(url_for('index')) 
    
    # reformater les datetime pour afficahge correct dans le form
    form_KC8['Batch_KC8_date'].data = form_KC8['Batch_KC8_date'].data.strftime(format='%d/%m/%y')
    form_KC8['Batch_KC8_heure_debut'].data = form_KC8['Batch_KC8_heure_debut'].data.strftime(format='%H:%M')
    return render_template("MaJ_batch_KC8.html",
                           Form_KC8 = form_KC8)



#################################################################
########################## Delete Batch #########################
#################################################################

@app.route('/del_KC8/<batch_name>', methods=['GET'])
def supprimer_KC8(batch_name):
    response = requests.get(f'http://127.0.0.1:8000/KC8/name/{batch_name}')
    batch_id = response.json()['Batch_KC8_id']
    response = requests.get(f'http://127.0.0.1:8000/KC8/delete/{batch_id}')
    flash(f'{response.status_code} :Batch {batch_name} supprimé')
    return redirect(url_for('index'))

@app.route('/del_OGD/<batch_name>', methods=['GET','POST'])
def supprimer_OGD(batch_name):

    response = requests.get(f'http://127.0.0.1:8000/OGD/name/{batch_name}')
    data = response.json()
    batch_id = data['Batch_OGD_id']
    print(response.json())
    print(batch_id)
    print(type(batch_id))

    # displau confirmation message
    if request.method == 'POST':
        response = requests.get(f'http://127.0.0.1:8000/OGD/delete/{(batch_id)}')
        flash(f'{response.status_code} Batch {batch_name} supprimé')
        return redirect(url_for('index'))
    form = Confirm_delete()
    return render_template('confirm_delete.html', batch_data=data, form=form)


@app.route("/Cahier_production",methods=["GET","POST"])
def cahier_prod():
    url = 'http://127.0.0.1:8000/'
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'}

    response = requests.get(url+f'OGD',headers=headers)
    batch_OGD = pd.DataFrame(response.json()).sort_values('Batch_OGD_id', ascending=False)['Batch_OGD_name'].values


    response = requests.get(url+f'KC8',headers=headers)
    batch_KC8 = pd.DataFrame(response.json()).sort_values('Batch_KC8_id', ascending=False)['Batch_KC8_name'].values


    return render_template("Cahier_prod.html",
                           batch_OGDs=batch_OGD,
                           batch_KC8s=batch_KC8)



#################################################################
########################## Dashboards ###########################
#################################################################

@app.route("/Dashboard_production",methods=["GET","POST"])
def dash_prod():

    # request the products available
    response = requests.get('http://127.0.0.1:8000/Produit/')
    Produits_all = pd.DataFrame(response.json())
    WNC_en_cours = Produits_all.loc[Produits_all.Batch_Produit_ref_CW.apply(lambda x : ('W' in x.split('-')[0]) & ('NC' not in x.split('-')[0])),
                                    ['Batch_Produit_ref_CW','Batch_Produit_date']].values
    W_en_cours = Produits_all.loc[Produits_all.Batch_Produit_ref_CW.apply(lambda x : ('W' in x.split('-')[0]) & ('NC' in x.split('-')[0])),
                                  ['Batch_Produit_ref_CW','Batch_Produit_date']].values
    Epo_en_cours = Produits_all.loc[Produits_all.Batch_Produit_ref_CW.apply(lambda x : ('Epo' in x.split('-')[0]) ),
                                    ['Batch_Produit_ref_CW','Batch_Produit_date']].values


    # get the latest 5 OGD
    img_UV, img_RAMAN = make_chart_for_dash_produits(last_n = 5)

    return render_template("acceuil_production.html",
                           WNC_en_cours=WNC_en_cours,
                           W_en_cours=W_en_cours,
                           Epo_en_cours=Epo_en_cours,
                           img_UV=img_UV,
                           img_RAMAN=img_RAMAN)



@app.route("/Dashboard_commerce",methods=["GET","POST"])
def dash_commerce():

    # display available products


    # demande batch produit 
    response = requests.get(f'http://127.0.0.1:8000/Envoi/')
    Envois_all = pd.DataFrame(response.json())
    Envois_en_attente = Envois_all.loc[Envois_all.Envoi_produit_batch.isnull(),['Envoi_produit_name','Envoi_produit_Qte','Envoi_client_name','Envoi_id']][::-1].values

    response = requests.get(f'http://127.0.0.1:8000/Produit/')
    array = np.array([(a['Batch_Produit_ref_CW'],a['Batch_Produit_OGD_Qte']) for a in response.json()])
    df = pd.DataFrame(array, columns=['produit','Qté'])
    df['Categorie'] = df.produit.apply(lambda x :x.split("-")[0])
    df['Qté'] = df['Qté'].astype(float)
    fig = px.bar(df,x='Categorie',y='Qté',color='produit',title='Stocks des produits sur étagère')
    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)


    return render_template("acceuil_commerce.html",
                           graphJSON=graphJSON,
                           Envois_en_attente=Envois_en_attente)


#################################################################
########################## CLIENTS - COMMANDES ##################
#################################################################

@app.route("/Clients", methods=['GET','POST'])
def acceuil_clients():
    response = requests.get(f'http://127.0.0.1:8000/Client/')
    Clients_all = pd.DataFrame(response.json())
    table_client = Clients_all.to_html(classes='table table-striped table-bordered', index=False)
    form_client = Form_Client()

    if form_client.validate_on_submit():
        url = 'http://127.0.0.1:8000/Client/'
        headers = {'accept': 'application/json',
                'Content-Type': 'application/json'}
        data = {'Client_nom':request.form['Client_name'],
                'Client_adresse':request.form['Client_adresse']}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return redirect(url_for('acceuil_clients'))

    return render_template("acceuil_client.html",
                           table_client = table_client,
                           Form_Client = form_client)


@app.route("/Commande",methods=["GET","POST"])
def Add_commande():

    form_envoi = Form_Envoi()
    if request.method == 'POST':
        # data = dict()
        # for field in form_envoi:
        #     if field.name == 'csrf_token' or field.name == 'Envoi_submit':
        #         continue
        #     elif 'date' in field.name or 'heure' in field.name:
        #         data[field.name] = form_envoi[field.name].data.strftime('%Y-%m-%dT%H:%M:%S')
        #     else:
        #         data[field.name] = form_envoi[field.name].data

        Envoi_date_commande = request.form['Envoi_date_commande']
        Envoi_date_commande = datetime.datetime.strptime(Envoi_date_commande, '%d/%m/%y')

        Envoi_date_prevu = request.form['Envoi_date_prevu']
        Envoi_date_prevu = datetime.datetime.strptime(Envoi_date_prevu, '%d/%m/%y')


        data = {"Envoi_date_commande":Envoi_date_commande.isoformat(),
                "Envoi_client_name":request.form['Envoi_client_name'],
                "Envoi_produit_name":request.form['Envoi_produit_name'],
                "Envoi_produit_batch":None,
                "Envoi_produit_Qte":request.form['Envoi_produit_Qte'],
                "Envoi_produit_emballage":"",
                "Envoi_date_prevu":Envoi_date_prevu.isoformat(),
                "Envoi_date_effective":None,
                "Envoi_code_coli":None,
                "Envoi_retour_client":None,
                }
        print(data)
        response = requests.post(f'http://127.0.0.1:8000/Envoi/',data=json.dumps(data))
        flash(f'{response.status_code} Demande production {data['Envoi_client_name']} ({data['Envoi_produit_Qte']} kg) effectué')
        return redirect(url_for('dash_commerce'))

    today = datetime.datetime.now()
    form_envoi.Envoi_date_commande.data = today
    response = requests.get(f'http://127.0.0.1:8000/Client/')
    form_envoi.Envoi_client_name.choices = np.unique(np.array([a['Client_nom'] for a in response.json()])).tolist()
    return render_template("Commande.html",
                           Form_Envoi = form_envoi)



@app.route("/Envois",methods=["GET","POST"])
def Add_envoi():

    form_envoi = Form_Envoi()
    if request.method == 'POST':
        data = dict()
        for field in form_envoi:
            if field.name == 'csrf_token' or field.name == 'Envoi_submit':
                continue
            elif 'date' in field.name or 'heure' in field.name:
                data[field.name] = form_envoi[field.name].data.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                data[field.name] = form_envoi[field.name].data

        data['Envoi_produit_name']=data['Envoi_produit_batch'].split('-')[0]
        data["Envoi_retour_client"]=None
                
        response = requests.post(f'http://127.0.0.1:8000/Envoi/',data=json.dumps(data))
        flash(f'{response.status_code} Demande production {data['Envoi_client_name']} ({data['Envoi_produit_Qte']} kg) effectué')
        return redirect(url_for('dash_commerce'))

    today = datetime.datetime.now()
    form_envoi.Envoi_date_commande.data = today
    response = requests.get(f'http://127.0.0.1:8000/Client/')
    form_envoi.Envoi_client_name.choices = np.unique(np.array([a['Client_nom'] for a in response.json()])).tolist()

    response = requests.get(f'http://127.0.0.1:8000/Produit/')
    list_produits = np.array([a['Batch_Produit_ref_CW'] for a in response.json() if float(a['Batch_Produit_OGD_Qte']) > 0]).tolist()
    form_envoi.Envoi_produit_batch.choices = list_produits


    today = datetime.datetime.now()
    form_envoi.Envoi_date_prevu.data = today
    form_envoi.Envoi_date_effective.data = today


    return render_template("Envois.html",
                           Form_Envoi = form_envoi)


@app.route("/Suivi_envois",methods=["GET","POST"])
def Suivi_envoi():

    form_envoi = Form_Envoi()
    if form_envoi.validate_on_submit():
        #change attribute retour client in form and submit to update to database

        response = requests.post(f'http://127.0.0.1:8000/Envois/update/{id}',data=json.dumps(data))
        flash(f'{response.status_code} Mise a jour envoi de {data['Envoi_produit_name']} à {data['Envoi_client_name']} effectué')
        return redirect(url_for('dash_commerce'))

    response = requests.get(f'http://127.0.0.1:8000/Envoi/')
    Envois_all = pd.DataFrame(response.json())
    Envois_all = Envois_all.loc[Envois_all.Envoi_retour_client.isnull()]

    return render_template("Suivi_envois.html",
                           Envois_all = [b for b in Envois_all.values])



























# Etabli un sevreur de developpement  /!\  ==> ue production serveur like WGSI Gunicorn for Production !!!!
# from gunicorn import run

if __name__ == "__main__":

    ### Doctest for app.py
    import doctest
    doctest.testmod()
    ### -----------------


    app.run(debug=True, host='0.0.0.0', port=4000) 
    # run("app:app", host="0.0.0.0", port=5000, workers=1)


# afficher figure et tableaux
    #     url = 'http://127.0.0.1:8000/'
    # headers = {
    # 'accept': 'application/json',
    # 'Content-Type': 'application/json'}
    # response = requests.get(url+f'analyses_UV',headers=headers)
    # UV_OGD = pd.DataFrame(response.json())[['Analyse_UV_name','Analyse_UV_subname','Analyse_UV_details','Analyses_UV_data']]
    # UV_OGD = UV_OGD.loc[UV_OGD.Analyse_UV_subname == 'UV']
    # print(UV_OGD)
    # UV_OGD['conc'] = UV_OGD.apply(lambda x: x[3]['200'] / float(x[2]['dillution'].split(':')[1]), axis=1)
    #     # info batch date
    # response = requests.get(url+f'OGD',headers=headers)
    # batch_OGD = pd.DataFrame(response.json())

    # # create new df
    # df=pd.merge(batch_OGD[['Batch_OGD_name','Batch_OGD_date','Batch_OGD_KC8_masse']],
    #         UV_OGD[['Analyse_UV_name','conc']],
    #         left_on='Batch_OGD_name',
    #         right_on='Analyse_UV_name',
    #         how='inner')
    #     # format date
    # df['Batch_OGD_date'] = pd.to_datetime(df['Batch_OGD_date'])
    # df['week'] = df.Batch_OGD_date.apply(lambda x : x.week) #df.Batch_name.apply(lambda x : pd.to_datetime(int(x[2:4]),unit='W').week)  # df['date'].dt.week # 
    # df['month'] = df.Batch_OGD_date.apply(lambda x : x.month) #Batch_name.apply(lambda x : pd.to_datetime(int(x[2:4]),unit='W').month) # df['date'].dt.month # 
    # df['year'] = df.Batch_OGD_date.apply(lambda x : x.year)
    # df.Batch_OGD_KC8_masse = df.Batch_OGD_KC8_masse.apply(lambda x : int(round(x)))
    #     # Pivot Table
    # table = pd.pivot_table(df, 
    #                 index=[ 'month', 'week'], 
    #                 values=['Batch_OGD_name', 'conc'], 
    #                 aggfunc={'Batch_OGD_name': 'count', 'conc': ['sum', 'mean']})
    # html_table = table.to_html(index=True)
    #     # create graph
    # fig = px.box(df, x='Batch_OGD_date', y="conc", points="all")
    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)