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
from app import config

# import for bdd - mysql
import requests
import mysql.connector as bdd_connect

# import pour flask
from flask import Flask, jsonify, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required

# import pour le backend
from app.utils import update_preds_from_UV, update_MPs, predict_OGD_concentration,format_datetime, update_stock_product, update_stock_OGD_additif, get_material_composition_for_product, update_stocks_KC8_THF, fetch_MP, make_chart_for_dash_produits,update_stocks_K_C, populate_form, get_last_10_batch, get_form_data, get_form_data_KC8, get_matieres_premieres
from app.forms import *




# Instanciate app
app = Flask(__name__)
app.config['SECRET_KEY'] = "somesecretkey" # secret key stored in app == env variable to hide

# enable CSRF protection globally for a Flask app
from flask_wtf.csrf import CSRFProtect, generate_csrf
csrf = CSRFProtect(app)

# enable monitoring
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)



from flask import Flask, render_template, redirect, url_for
from prometheus_flask_exporter import PrometheusMetrics
import requests
import pandas as pd
import time


# Define custom metrics
stock_gauge = metrics.gauge('stock_matieres_premieres', 'Stock levels of materials', labels={'material': 'material_name'})
batches_in_progress = metrics.gauge('batches_in_progress', 'Number of batches in progress', labels={'batch_type': 'batch_name'})
external_requests_total = metrics.counter('external_requests_total', 'Total external requests made', labels={'endpoint': 'endpoint_name'})
errors_total = metrics.counter('acceuil_materiaux_errors_total', 'Total errors in acceuil_materiaux', labels={'error_type': 'error_name'})





# Database connexion for developpment
from app.models import get_db_connection

    ## Test de la connection à la bdd
try:
    BDD_CW, curseur = get_db_connection()
    print('connection à la BDD OK')
    curseur.close()
    BDD_CW.close()
except:
    print("Can't connect to BDD")



########################################################################################
############################### LOGIN #######################################
########################################################################################

# import for managing users
from app.models import User
from flask import request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

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
            return redirect(url_for('acceuil_materiaux'))  # Redirect to a success page
    
        else:
            if not user:
                flash("Email not found, you must register first")
            elif not user.check_password(password):
                flash('Incorrect password')
            
    return render_template('login.html', form=form)

@app.route('/delete_account', methods=['POST'])
def delete_account():
    form = DeleteAccount()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.find_by_email(email)
        if user and user.check_password(password):
            User.delete(email)
    return render_template("delete_account.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


########################################################################################
############################## Page d'acceuil / Dashboard ##############################
########################################################################################





@app.route("/Materiaux", methods=["GET","POST"])
@metrics.counter('acceuil_materiaux_requests_total', 'Total requests to acceuil_materiaux')
@metrics.histogram('acceuil_materiaux_request_duration_seconds', 'Duration of requests to acceuil_materiaux', labels={'status': 'status'})
# @login_required
def acceuil_materiaux():

    # configure default batch
    global default_batch
    default_batch = fetch_MP()

    if type(default_batch) != dict:
        return redirect(url_for('Add_MP'))
     
    try:
        # batch without ending time
        response = requests.get(f'http://127.0.0.1:8000/OGD/')
        OGD_all = pd.DataFrame(response.json())
        OGD_en_cours = OGD_all.loc[OGD_all.Batch_OGD_heure_fin.isnull(),['Batch_OGD_name','Batch_OGD_heure_debut','Batch_OGD_Stock']].values
        response = requests.get(f'http://127.0.0.1:8000/KC8/')
        KC8_all = pd.DataFrame(response.json())
        KC8_en_cours = KC8_all.loc[KC8_all.Batch_KC8_heure_fin.isnull(),['Batch_KC8_name','Batch_KC8_heure_debut']].values
    except:
        OGD_en_cours=KC8_en_cours=list()

    # get stock matieres premieres
    stock_MP = requests.get(f'http://127.0.0.1:8000/matieres_premieres/')

    if stock_MP.json():
        stock_MP = pd.DataFrame(stock_MP.json())[['MP_ref_fournisseur','MP_stock']]
        stock_MP.index = stock_MP['MP_ref_fournisseur']
        stock_MP.drop(columns='MP_ref_fournisseur',inplace=True)
        stock_MP = stock_MP.T.to_dict()
        stock_K = stock_MP[default_batch['K']]['MP_stock']
        stock_C = stock_MP[default_batch['C']]['MP_stock']
        stock_THF = stock_MP[default_batch['THF']]['MP_stock']
    else:
        stock_K = stock_C = stock_THF = 'na'




    Stock_KC8 = requests.get(f'http://127.0.0.1:8000/KC8/name/{default_batch["KC8"]}')
    try:
        Stock_KC8 = Stock_KC8.json()['Batch_KC8_masse']
    except:
        Stock_KC8 = 0
    
    return render_template("acceuil_materiaux.html",
                        n_batch_K = default_batch['K'],
                        stock_K = stock_K,
                        n_batch_C = default_batch['C'],
                        stock_C = stock_C,
                        n_batch_THF = default_batch['THF'],
                        stock_THF = stock_THF,
                        n_batch_KC8 = default_batch['KC8'],
                        stock_KC8 = Stock_KC8,
                        OGD_en_cours = OGD_en_cours,
                        KC8_en_cours = KC8_en_cours)


@app.route("/")
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
            "MP_codeCW": config.ref_CW_matiere_premiere[request.form['MP_nom']],
            "MP_ref_fournisseur": request.form['MP_ref_fournisseur'],
            "MP_quantite" : request.form["MP_stock"],
            "MP_stock": request.form['MP_stock'],
            "MP_date_reception": MP_date_reception.isoformat(),
            "MP_unite": request.form['MP_unite'],
            "MP_Analyses": "None"}

        response = requests.get(f'http://127.0.0.1:8000/matieres_premieres/')
        batch_exist = [a['MP_ref_fournisseur'] for a in response.json()]
        df = pd.DataFrame(response.json())
        

        if 'MaJ' in request.form.keys():
                MP_to_update = df.loc[(df.MP_ref_fournisseur == request.form['MP_ref_fournisseur'])]
                id_MP = MP_to_update.index[0]
                data = MP_to_update.to_dict()
                data['MP_stock'] = request.form['MP_stock']

                print(10*"\n","CECI EST UNE MISE A JOUR")
                data['MP_id'] = str(id_MP)
                response = requests.post(url+f"update/{id_MP}", headers=headers, data=json.dumps(data))
        elif 'submit_new' in request.form.keys() : # check if batch name exists and returns error if so
            print(10*"\n","CECI EST UN NVX BATCH")
            # verifie que la référence unique reste unique
            print(data)
            if data['MP_ref_fournisseur'] in batch_exist:
                flash("reference existante")
                return redirect(url_for('Add_MP'))
            # ajout nvlle matiere premiere
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                flash("Nouvelle matière première ajoutée avec succès")
            else:
                flash(json.dumps(response.json()))

        batch_C,batch_K,batch_THF = update_MPs()
        return render_template("Add_matiere_premiere.html",
                           Form_Matieres_premieres=form_MP,
                           batch_C=batch_C[::-1],
                           batch_K=batch_K[::-1],
                           batch_THF=batch_THF[::-1],
                           Inspect=False)
    
    else:
        for field,errors in form_MP.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_MP, field).label.text}' : {error}")
    
    form_MP.MP_date_reception.data = datetime.datetime.now()
  
    try:
        batch_C,batch_K,batch_THF = update_MPs()
    except Exception as e:
        print(e)
        batch_C=batch_K=batch_THF=[]

    # visualistion baisse des stocks:




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

    # MaJ batch K disponibles
    response = requests.get(url='http://127.0.0.1:8000/matieres_premieres/',headers=headers)
    form_KC8.Batch_KC8_K_batch.choices = [a['MP_ref_fournisseur'] for a in response.json() if (a['MP_stock'] >= 0) and (a['MP_nom'] == 'Potassium')][:-10:-1]
    # MaJ batch C disponibles
    response = requests.get(url='http://127.0.0.1:8000/matieres_premieres/',headers=headers)
    form_KC8.Batch_KC8_C_batch.choices = [a['MP_ref_fournisseur'] for a in response.json() if (a['MP_stock'] >= 0) and (a['MP_nom'] == 'Carbone')][:-10:-1]    


    if form_KC8.validate_on_submit():

        # Format datetime
        KC8_date_debut, KC8_heure_debut = format_datetime(request.form['Batch_KC8_date'],
                                                          request.form['Batch_KC8_heure_debut'])

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

        # Update matiere premiere and check if new mass >= 0
        a = update_stocks_K_C(data) 
        if not a['post_K'] or not a['post_C']:
            flash("Impossible d'utiliser ce batch pour cette quantité de KC8")
            return redirect(url_for('Add_KC8'))

        # Post new batch for KC8
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            flash(json.dumps({'Problem connecting to the database': response.json()}))
        else:
            flash(json.dumps({'status': 'OK'}))

        return redirect(url_for('acceuil_materiaux'))
    

    else:
        for field,errors in form_KC8.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_KC8, field).label.text}' : {error}")


    # pre-filling with today and last saved batches
    response = requests.get(url+'last', headers=headers)
    # make batch KC8 ONE more than the last one --> TO DO : here is the last KC8 batch appears
    # make guard that the new batch of KC8 should not be a batch that already exiosts
    if response.status_code == 200:
        form_KC8.Batch_KC8_name.data = response.json()['Batch_KC8_name']
        form_KC8.Batch_KC8_K_batch.data = default_batch['K']
        form_KC8.Batch_KC8_C_batch.data = default_batch['C']
    form_KC8.Batch_KC8_date.data = datetime.datetime.now()
    form_KC8.Batch_KC8_heure_debut.data = datetime.datetime.now()
     # Get the data
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    # Batch OGD existants
    response = requests.get(url='http://127.0.0.1:8000/KC8/',headers=headers)
    form_KC8.Batch_KC8_name.validators[0].values = [a['Batch_KC8_name'] for a in response.json()]
    
    
    return render_template("Add_batch_KC8.html",
                           Form_KC8=form_KC8)

@app.route("/Nouveau_batch_OGD", methods=['GET','POST'])
def Add_OGD():
    global default_batch
    form_OGD = Form_Batch_OGD()

    # Setting up headers
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    # MaJ batch KC8 disponibles
    response = requests.get(url='http://127.0.0.1:8000/KC8/',headers=headers)
    form_OGD.Batch_OGD_KC8_batch.choices = [a['Batch_KC8_name'] for a in response.json() if a['Batch_KC8_masse'] > 0][:-10:-1]
    # MaJ batch THF disponibles
    response = requests.get(url='http://127.0.0.1:8000/matieres_premieres/',headers=headers)
    form_OGD.Batch_OGD_THF_batch.choices = [a['MP_ref_fournisseur'] for a in response.json() if (a['MP_stock'] >= 0) and (a['MP_nom'] == 'THF')][:-10:-1]    

    if form_OGD.validate_on_submit():

        url = 'http://127.0.0.1:8000/OGD/'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'}
        
        OGD_date_debut, OGD_heure_debut = format_datetime(request.form['Batch_OGD_date'],
                                                          request.form['Batch_OGD_heure_debut'])

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
            "Batch_OGD_Stock" : None,
            "Batch_OGD_Analyses": "None"}


        # Update matiere premiere and check if new mass >= 0
        status = update_stocks_KC8_THF(data) 
        if not status['post_KC8'] or not status['post_THF']:
            flash("Impossible d'utiliser ce(s) batch(s) pour cette quantité de OGD")
            return redirect(url_for('Add_OGD'))
        

        # make prediction on OGD concentration
        pred = predict_OGD_concentration(data,OGD_heure_debut)
        # on calcule la qté de produit et le met dans stocks
        data['Batch_OGD_Stock'] = float(pred) * float(data['Batch_OGD_THF_Volume']) * 1 ## g/L x L ==> grammes PRECISER LE RATIO DE VOLUME RECUPERE
        response = requests.post(url, headers=headers, data=json.dumps(data))


        if response.status_code != 200:
            flash(json.dumps('Probleme de connection à la base de donnée'))
        else:
            flash(json.dumps({'status': 'OK'}))

        return redirect(url_for('acceuil_materiaux'))
    

    else:
        for field,errors in form_OGD.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_OGD, field).label.text}' : {error}")

       
    # formate le nom de batch OGD avec la semaine (today.isocalendar()[1]:02)
    today = datetime.datetime.now()
    form_OGD.Batch_OGD_name.data = f"P{str(today.year)[-2:]}{today.isocalendar()[1]:02}"
    form_OGD.Batch_OGD_date.data = today
    form_OGD.Batch_OGD_heure_debut.data = today
    form_OGD.Batch_OGD_KC8_batch.data = default_batch['KC8']
    form_OGD.Batch_OGD_THF_batch.data = default_batch['THF']

    # Display batch OGD existants
    response = requests.get(url='http://127.0.0.1:8000/OGD/',headers=headers)
    form_OGD.Batch_OGD_name.validators[0].values = [a['Batch_OGD_name'] for a in response.json()]


    # print("form before rendering html")
    # print("\n".join([f'{(a.name,a.data)}' for a in form_OGD]))
    return render_template("Add_batch_OGD.html",
                           Form_OGD=form_OGD)



@app.route("/Nouveau_batch_produit/<produit>", methods=['GET','POST'])
def Add_Produit(produit):

    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    form_produit = Form_Produit()
    # MaJ choix batch OGD : ONLY batch terminated and with stock > 0
    response = requests.get(url='http://127.0.0.1:8000/OGD/',headers=headers)
    batchs_OGD = pd.DataFrame(response.json())
    batchs_OGD_ready = batchs_OGD.loc[(~batchs_OGD.Batch_OGD_heure_fin.isnull()) & (batchs_OGD.Batch_OGD_Stock > 0), 'Batch_OGD_name']
    form_produit.Batch_Produit_OGD_batch.choices = batchs_OGD_ready.tolist()

    # FillIn fom from  #### UPDATE BY SHOWINF ONLY BACTH WHERE THERE IS STILL STOCK
    response = requests.get(url='http://127.0.0.1:8000/matieres_premieres/',headers=headers)
    MP_with_stock = [a for a in response.json() if a['MP_stock'] >0]
    if ('W' in produit) and not (produit =='W1'):
        # form_produit.Batch_Produit_additif_batch.choices = [a['MP_codeCW'] for a in response.json() if a['MP_nom'] == 'Viscosant'][:-10:-1]
        form_produit.Batch_Produit_additif_batch.choices = [a['MP_nom'] for a in MP_with_stock if a['MP_nom'] == 'Viscosant'][:-5:-1]
    elif ('Epo' in produit) and not (produit == 'EpoC'):
        # form_produit.Batch_Produit_additif_batch.choices = [a['MP_codeCW'] for a in response.json() if a['MP_nom'] == 'ResineEpikote827'][:-10:-1]
        form_produit.Batch_Produit_additif_batch.choices = [a['MP_nom'] for a in MP_with_stock if a['MP_nom'] == 'ResineEpikote827'][:-5:-1]
    elif produit in ['EpoF, EpoR']:
        # form_produit.Batch_Produit_additif_batch.choices = [a['MP_codeCW'] for a in response.json() if a['MP_nom'] == 'ResineEpikote1001'][:-10:-1]
        form_produit.Batch_Produit_additif_batch.choices = [a['MP_nom'] for a in MP_with_stock if a['MP_nom'] == 'ResineEpikote1001'][:-5:-1]
    else:
        flash("produit n'a pas d'additifs")

    if form_produit.validate_on_submit():
        
        Produit_date = request.form['Batch_Produit_date']
        Produit_date = datetime.datetime.strptime(Produit_date, '%d/%m/%y')
        print("FORM",5*"\n")
        print(request.form)
        data = {
            "Batch_Produit_ref_CW": request.form['Batch_Produit_ref_CW'],
            "Batch_Produit_date": Produit_date.isoformat(),
            "Batch_Produit_Technicien": request.form['Batch_Produit_Technicien'],
            "Batch_Produit_OGD_batch": request.form['Batch_Produit_OGD_batch'],
            "Batch_Produit_OGD_Qte": request.form['Batch_Produit_OGD_Qte'],
            "Batch_Produit_additif_batch": request.form['Batch_Produit_additif_batch'],
            "Batch_Produit_additif_Qte": request.form['Batch_Produit_additif_Qte'],
            "Batch_Produit_stock": request.form['Batch_produit_stock'],
            "Batch_Produit_Analyses": "None",}
        

    ################################################################################################
    ################################################################################################
    ######### UPDATE CODE : FUNCTION MUST UPDATE --ALL-- THE MP USED FOR THE BATCH  ################    ########################
    ################################################################################################
    ################################################################################################
    ################################################################################################
        
        # Update OGD and viscosant and check if new mass >= 0
        a = update_stock_OGD_additif(data) 
        if not a['post_OGD'] or not a['post_additif']:
            flash("Impossible d'utiliser ce(s) batch(s) pour cette quantité de OGD")
            return redirect(url_for('Add_OGD'))
        elif not a['get_OGD'] or not a['get_additif']:
            flash('Probleme acces à database (table OGD)')
            return redirect(url_for('Add_OGD'))

        # update product table
        response = requests.post(url = 'http://127.0.0.1:8000/Produit/', headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            flash(json.dumps({'Problem connecting to the database': response.json()}))
        else:
            flash(json.dumps({'Ajout nouveaux batch produit': 'OK'}))

        # UPDATE ENVOI IF produit_desc with ref from produit
        if Envoi_id:
            requests.get()

        return redirect(url_for('acceuil_materiaux'))
    else:
        for field,errors in form_produit.errors.items():
            for error in errors:
                flash(f"Erreur pour le champ '{getattr(form_produit, field).label.text}' : {error}")

    # populate form
    today = datetime.datetime.now()
    form_produit.Batch_Produit_date.data = today


    # check if production comes from client demand -> fill in form with mass
    Envoi_id = request.args.get('envoie')
    if Envoi_id:
        response = requests.get(url=f'http://127.0.0.1:8000/Envoi/id/{Envoi_id}',headers=headers)
        produit_qte = response.json()['Envoi_produit_Qte']
        form_produit.Batch_produit_stock.data = produit_qte
        print(produit_qte)

        # iterate over all methods to get all quantities
        list_of_material = get_material_composition_for_product(produit,float(produit_qte))
        Qte_materiaux = dict()
        for method_name in dir(list_of_material):
            if not method_name.startswith("__"):  
                method = getattr(list_of_material, method_name)
                if callable(method):
                    Qte_materiaux.update(method())
                    # print(f"{method_name}: {method()}")
        print(Qte_materiaux)

        form_produit.Batch_Produit_OGD_Qte.data = Qte_materiaux['OGD']

        if 'W' in produit:
            form_produit.Batch_Produit_additif_Qte.data = Qte_materiaux['viscosant']
        elif 'EpoC' in produit:
            form_produit.Batch_Produit_additif_Qte.data = Qte_materiaux['Epikote1001']
        else:
            form_produit.Batch_Produit_additif_Qte.data = Qte_materiaux['Epikote827']
            


    today = datetime.datetime.now()
    name = config.ref_CW_produit[produit]
    form_produit.Batch_Produit_ref_CW.data = f"{produit}-{str(today.year)[-2:]}{today.isocalendar()[1]:02}"
    form_produit.Batch_Produit_date.data = today


    return render_template("Add_batch_produit.html",
                           Form_Produit=form_produit,
                           produit=produit,
                           name=name)


@app.route("/Update_default_batch", methods=['GET','POST'])
def Update_default_batch():
    global default_batch
    # default_batch = fetch_MP()

    last_10_K, last_10_C, last_10_THF, last_10_KC8 = get_last_10_batch()

    if request.method == 'POST':
        default_batch['K']= request.form.get('n_batch_K')
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
    # MaJ batch KC8 disponibles
    response = requests.get(url='http://127.0.0.1:8000/KC8/',headers=headers)
    form_OGD.Batch_OGD_KC8_batch.choices = [a['Batch_KC8_name'] for a in response.json() if a['Batch_KC8_masse'] > 0][:-10:-1]
    # MaJ batch THF disponibles
    response = requests.get(url='http://127.0.0.1:8000/matieres_premieres/',headers=headers)
    form_OGD.Batch_OGD_THF_batch.choices = [a['MP_ref_fournisseur'] for a in response.json() if (a['MP_stock'] >= 0) and (a['MP_nom'] == 'THF')][:-10:-1]    
    
    
    if request.method == 'POST': 
        data = dict()
        data['Batch_OGD_id'] = id_batch
        for field in form_OGD:
            print(field.name,form_OGD[field.name].data)

            if field.name == 'csrf_token':
                continue
            elif 'date' in field.name or 'heure' in field.name:
                data[field.name] = form_OGD[field.name].data.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                data[field.name] = form_OGD[field.name].data
        response = requests.post(url+f'update/{id_batch}', headers=headers, data=json.dumps(data))
        flash(json.dumps({'status': response.status_code}), 200)
        return redirect(url_for('acceuil_materiaux')) 
    
    # reformater les datetime pour affichage correct dans le form
    # form_OGD['Batch_OGD_date'].data = form_OGD['Batch_OGD_date'].data.strftime(format='%d/%m/%y')
    # form_OGD['Batch_OGD_heure_debut'].data = form_OGD['Batch_OGD_heure_debut'].data.strftime(format='%H:%M')
    
    print(5*"\n")
    print("\n".join([f'{(a.name,a.data)}' for a in form_OGD]))
    
    return render_template("MaJ_batch_OGD.html",
                           Form_OGD = form_OGD)


@app.route("/MaJ_batch_KC8/<batch_name>",methods=["GET","POST"])
# @login_required
def update_batch_KC8(batch_name):
    # get Batch info
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'}
    response = requests.get(f'http://127.0.0.1:8000/KC8/name/{batch_name}',headers=headers)
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

        response = requests.post(f'http://127.0.0.1:8000/KC8/update/{id_batch}', headers=headers, data=json.dumps(data))
        flash(json.dumps({'status': response.status_code}), 200)
        return redirect(url_for('acceuil_materiaux')) 
    
    # reformater les datetime pour afficahge correct dans le form
    form_KC8['Batch_KC8_date'].data = form_KC8['Batch_KC8_date'].data.strftime(format='%d/%m/%y')
    form_KC8['Batch_KC8_heure_debut'].data = form_KC8['Batch_KC8_heure_debut'].data.strftime(format='%H:%M')
    return render_template("MaJ_batch_KC8.html",
                           Form_KC8 = form_KC8)


#################################################################
####################### Ajouter analyses ########################
#################################################################


@app.route('/Ajouter_analyses/<batch_name>', methods=['GET',"POST"])
def Add_analyse(batch_name):
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'}
    form_OGD = Form_Batch_OGD()
    form_KC8 = Form_Batch_KC8()
    if request.method == 'POST':
            
        # Check if data was added
        data_UV = request.files['file_UV']
        data_Raman = request.files['file_Raman']
        if not data_UV and not data_Raman:
            flash("Pas d'analyses ajoutées")
            return redirect(url_for('Add_analyse',batch_name=batch_name))

        if 'KC8' in batch_name:
            # RAMAN
            data_Raman = request.files['file_Raman']
            file_Raman = pd.read_csv(data_Raman,sep='\t')
            file_Raman=file_Raman.to_dict()
            analyse=dict()
            analyse['Analyse_name'] = batch_name
            analyse['Analyse_subname'] = 'RAMAN'
            analyse['Analyse_details'] = dict({'methode':request.form.get('type_raman'),
            'details':request.form.get('details_RAMAN')})
            analyse['Analyses_data'] = file_Raman
            response = requests.post('http://127.0.0.1:8000/analyses/', headers=headers, data=json.dumps(analyse))

        else:
            print("HERE WE ADD DATA")
            # UV
            file_UV = pd.read_csv(data_UV,sep='\t',index_col=0,header=None)

            abs_800 = file_UV.values[-1]
            dilution = request.form.get("dilution")
            conc = abs_800 * float(dilution)

            analyse=dict()
            analyse['Analyse_name'] = batch_name
            analyse['Analyse_subname'] = 'UV'
            analyse['Analyse_details'] = {'dilution':f'1:{ dilution }',
                                          'centrifuge':request.form.get('centrif'),
                                          'details':request.form.get('details_UV'),
                                          'conc':f'{conc}'}
            analyse['Analyses_data'] = file_UV.to_dict()[1]


            print(10*"\n")
            print(analyse)
            response = requests.post('http://127.0.0.1:8000/analyses/', headers=headers, data=json.dumps(analyse))
            
            
            ######## METTRE A JOUR LA TABLE DES PREDICTIONS AVEC LA CONCENTRATION RELLE
            code_get,code_post = update_preds_from_UV(batch_name,conc)
            print(10*"\n")
            print('MaJ PREDICTIONS',code_post,code_get)
            # response = requests.get("http://127.0.0.1:8000/Predictions")
            # a = pd.DataFrame(response.json())
            # mask = [batch_name in a.Prediction_data[i]['sample'] for i in range(a.shape[0])]

            #     data = {"Prediction_date": date,  # AJOUTER DATE AUJ
            #             "Prediction_type": "OGD_conc",
            #             "Prediction_model_version": "string",
            #             "Prediction_data": {"sample":data.Batch_OGD_name,
            #                                 "pred":float(pred[0]),
            #                                 "reel":0}}


                # headers = {'accept': 'application/json','Content-Type': 'application/json'}
                # response = requests.post(url='http://127.0.0.1:8000/Predictions/', headers=headers, data=json.dumps(data))  
                        


            # RAMAN
            data_Raman = request.files['file_Raman']
            if data_Raman:
                file_Raman = pd.read_csv(data_Raman,sep='\t')
                analyse=dict()
                analyse['Analyse_name'] = batch_name
                analyse['Analyse_subname'] = 'RAMAN'
                analyse['Analyse_details'] = dict({'methode':request.form.get('type_raman'),
                'details':request.form.get('details_RAMAN')})
                analyse['Analyses_data'] = file_Raman.to_dict()
                response = requests.post('http://127.0.0.1:8000/analyses/', headers=headers, data=json.dumps(analyse))

        flash(f"Analyse ajoutée avec succés pour {batch_name}")
        return redirect(url_for('Add_analyse',batch_name=batch_name))


    if batch_name.startswith('P') or batch_name.startswith('2'):
        print('IT IS OGD BATCH')
        # request info on batch
        response = requests.get(f'http://127.0.0.1:8000/OGD/name/{batch_name}',headers=headers)
        form_OGD = populate_form(form_OGD, response)
        return render_template("Ajout_analyse_OGD.html",
                               Form_OGD = form_OGD)

    elif 'K' in batch_name:
        # request info on batch
        response = requests.get(f'http://127.0.0.1:8000/KC8/name/{batch_name}',headers=headers)
        form_KC8 = populate_form(form_KC8, response)
        return render_template("Ajout_analyse_KC8.html",
                               Form_KC8 = form_KC8)



    return redirect(url_for('cahier_prod'))

#################################################################
########################## Delete Batch #########################
#################################################################

@app.route('/del_KC8/<batch_name>', methods=['GET'])
def supprimer_KC8(batch_name):
    response = requests.get(f'http://127.0.0.1:8000/KC8/name/{batch_name}')
    batch_id = response.json()['Batch_KC8_id']
    response = requests.get(f'http://127.0.0.1:8000/KC8/delete/{batch_id}')
    flash(f'{response.status_code} :Batch {batch_name} supprimé')
    return redirect(url_for('acceuil_materiaux'))

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
        return redirect(url_for('acceuil_materiaux'))
    form = Confirm_delete()
    return render_template('confirm_delete.html', batch_data=data, form=form)


@app.route("/Cahier_production",methods=["GET","POST"])
def cahier_prod():
    url = 'http://127.0.0.1:8000/'
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'}

    response = requests.get(url+f'OGD/',headers=headers)
    batch_OGD = pd.DataFrame(response.json()).sort_values('Batch_OGD_id', ascending=False)['Batch_OGD_name'].values


    response = requests.get(url+f'KC8/',headers=headers)

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
    try:
        response = requests.get('http://127.0.0.1:8000/Produit/')
        Produits_all = pd.DataFrame(response.json())
        WNC_en_cours = Produits_all.loc[Produits_all.Batch_Produit_ref_CW.apply(lambda x : ('W' in x.split('-')[0]) & ('NC' not in x.split('-')[0])),
                                        ['Batch_Produit_ref_CW','Batch_Produit_date']].values
        W_en_cours = Produits_all.loc[Produits_all.Batch_Produit_ref_CW.apply(lambda x : ('W' in x.split('-')[0]) & ('NC' in x.split('-')[0])),
                                    ['Batch_Produit_ref_CW','Batch_Produit_date']].values
        Epo_en_cours = Produits_all.loc[Produits_all.Batch_Produit_ref_CW.apply(lambda x : ('Epo' in x.split('-')[0]) ),
                                        ['Batch_Produit_ref_CW','Batch_Produit_date']].values
    except:
        WNC_en_cours = W_en_cours = Epo_en_cours = []

    response = requests.get('http://127.0.0.1:8001/get_fig_uv/')
    img_UV = response.content
    response = requests.get('http://127.0.0.1:8001/get_fig_raman/')
    img_RAMAN = response.content
    print(10*"\n","DASHBOARD production")
    
    print(img_RAMAN)

    return render_template("acceuil_production.html",
                           WNC_en_cours=WNC_en_cours,
                           W_en_cours=W_en_cours,
                           Epo_en_cours=Epo_en_cours,
                           img_UV=img_UV.decode(),
                           img_RAMAN=img_RAMAN.decode())

@app.route("/Dashboard_ML", methods=['GET','POST'])
def dash_ML():
    response = requests.get('http://127.0.0.1:8000/Predictions/')
    all_preds = pd.DataFrame(response.json())
    all_preds['Prediction_data']
    table_preds = pd.concat([pd.DataFrame(all_preds['Prediction_data'][i], index=[i]) for i in range(all_preds.shape[0])])
    table_preds = table_preds.to_html(classes='table table-striped table-bordered', index=False)


    print(all_preds['Prediction_data'])
    se=list()
    for pred in all_preds['Prediction_data']:
        se.append((pred['pred']-pred['reel'])**2)
    rmse = (np.sum(np.array(se))/len(se))**0.5


    headers = {
        "Supervized-API-Key": os.getenv('API_SUPERVIZED_SECRET_KEY'), 
        "Content-Type": "application/json"
    }
    response = requests.get('http://127.0.0.1:8001/variable_importance/',headers=headers)
    img= response.content


    if request.method == 'POST':
        response = requests.get('http://127.0.0.1:8001/restart_training_regression/',headers=headers)

        print(10*"\n","RESTART TRAINING")
        print(response.content)
        
    form_regr = Form_submit_training_regr()

    return render_template("acceuil_ML.html",
                           table_preds=table_preds,
                           all_preds=all_preds.iloc[:,:-1],
                           rmse=rmse,
                           img=img.decode(),
                           form_regr=form_regr)



@app.route("/Dashboard_commerce",methods=["GET","POST"])
def dash_commerce():

    # display available products


    # demande batch produit 
    try :
        response = requests.get(f'http://127.0.0.1:8000/Envoi/')
        Envois_all = pd.DataFrame(response.json())
        Envois_en_attente = Envois_all.loc[Envois_all.Envoi_produit_batch.isnull(),['Envoi_produit_name','Envoi_produit_Qte','Envoi_client_name','Envoi_id']][::-1].values
    except:
        Envois_en_attente = list()


    response = requests.get(f'http://127.0.0.1:8000/Produit/')
    print(response.status_code)
    if response.status_code == 200 and response.json() != []:
        array = np.array([(a['Batch_Produit_ref_CW'],a['Batch_produit_stock']) for a in response.json() if a['Batch_produit_stock']>0])
        df = pd.DataFrame(array, columns=['produit','Qté'])
        df['Categorie'] = df.produit.apply(lambda x :x.split("-")[0])
        df['Qté'] = df['Qté'].astype(float)
        fig = px.bar(df,x='Categorie',y='Qté',color='produit',title='Stocks des produits sur étagère')
        graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    else :
        graphJSON=json.dumps({})



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
        flash(f"{response.status_code} Demande production {data['Envoi_client_name']} ({data['Envoi_produit_Qte']} kg) effectué")
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
    response = requests.get(f'http://127.0.0.1:8000/Client/')
    form_envoi.Envoi_client_name.choices = [a['Client_nom'] for a in response.json()]
    
    if request.method == 'POST':
        data = dict()
        for field in form_envoi:
            if field.name == 'csrf_token' or field.name == 'Envoi_submit':
                continue
            elif 'date' in field.name or 'heure' in field.name:
                data[field.name] = form_envoi[field.name].data.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                data[field.name] = form_envoi[field.name].data

        #### UPDATE HERE TO PUT ISO CODE??
        data['Envoi_produit_name']=data['Envoi_produit_batch'].split('-')[0]
        data["Envoi_retour_client"]=None


        # Update products and check if new mass >= 0
        a = update_stock_product(data) #### ATTENTION HERE POSSIBLE TO CONTROL COLIS NUMBER THAT MUST BE UNIQUE --> SEND 409
        if not a['post_product'] :
            flash("Impossible d'utiliser ce batch, quantité de stock insufisante")
            return redirect(url_for('Add_envoi'))


        print('DATA',data)

        # update envoie        
        response = requests.post(f'http://127.0.0.1:8000/Envoi/',data=json.dumps(data))
        flash(f"{response.status_code} : Envoi confirmé ({data['Envoi_client_name']} - {data['Envoi_produit_Qte']} kg)  stock de produit mis a jour")
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
        flash(f"{response.status_code} Mise a jour envoi de {data['Envoi_produit_name']} à {data['Envoi_client_name']} effectué")
        return redirect(url_for('dash_commerce'))

    response = requests.get(f'http://127.0.0.1:8000/Envoi/')
    Envois_all = pd.DataFrame(response.json())
    Envois_all = Envois_all.sort_values('Envoi_date_commande')
    Envois_all_ = Envois_all.loc[Envois_all.Envoi_retour_client.isnull()][:-5:-1]

    Envois_all = Envois_all.loc[:,['Envoi_produit_batch','Envoi_produit_Qte','Envoi_client_name','Envoi_date_commande','Envoi_date_effective','Envoi_retour_client']]
    Envois_all.Envoi_produit_Qte = Envois_all.Envoi_produit_Qte.apply(lambda x : round(x))
    Envois_all['Envoi_date_commande'] = pd.to_datetime(Envois_all['Envoi_date_commande'])
    Envois_all['Envoi_date_effective'] = pd.to_datetime(Envois_all['Envoi_date_effective'])
    Envois_all['Update'] = Envois_all['Envoi_retour_client'].apply(lambda x : '<a href='+'"{{'+ f"url_for('Envoi_retour_client', ref_envoie={x})" +'}}"'+f">{'MaJ' if x == None else 'Ajouter'}</a>")

    Envois_all = Envois_all.style.set_table_styles([
        {'selector': 'table', 'props': [('class', 'table table-striped table-bordered')]},
        {'selector': 'th', 'props': [('class', 'thead-dark')]},
        {'selector': 'td', 'props': [('class', 'align-middle')]}
    ]).format({
    'Envoi_date_commande': lambda t: t.strftime('%Y-%m-%d') if not pd.isna(t) else 'NaT',
    'Envoi_date_effective': lambda t: t.strftime('%Y-%m-%d') if not pd.isna(t) else 'NaT',})




    return render_template("Suivi_envois.html",
                           Envois_all = [b for b in Envois_all_.values],
                           table=Envois_all.to_html(index=False,escape=False))

@app.route("/MaJ_retour_Client/<ref_envoi>",methods=["GET","POST"])
def Envoi_retour_client(ref_envoi):


    form_envoi = Form_Envoi()
    response = requests.get(f'http://127.0.0.1:8000/Envoi/id/{ref_envoi}')
    form_envoi = populate_form(form_envoi, response)


    if form_envoi.validate_on_submit():
        #change attribute retour client in form and submit to update to database

        response = requests.post(f'http://127.0.0.1:8000/Envois/update/{ref_envoi}',data=json.dumps(data))
        flash(f"{response.status_code} Mise a jour envoi de {data['Envoi_produit_name']} à {data['Envoi_client_name']} effectué")
        return redirect(url_for('dash_commerce'))

    response = requests.get(f'http://127.0.0.1:8000/Envoi/')
    Envois_all = pd.DataFrame(response.json())
    Envois_all = Envois_all.loc[Envois_all.Envoi_retour_client.isnull()]

    return render_template("MaJ_envoi.html",
                            Form_envoi = form_envoi)



























# Etabli un sevreur de developpement  /!\  ==> ue production serveur like WGSI Gunicorn for Production !!!!
# from gunicorn import run

if __name__ == "__main__":

    ### Doctest for app.py
    import doctest
    doctest.testmod()
    ### -----------------


    app.run(debug=True, host='0.0.0.0', port=5000) 
    # run("app:app", host="0.0.0.0", port=5000, workers=1)

