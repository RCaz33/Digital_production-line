from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, StringField, SubmitField, DateTimeField, FloatField, IntegerField, TimeField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, NoneOf, AnyOf, ValidationError, Email

import datetime
import re
from app import config
########################################
#####  Create forms to login users #####
########################################

allowed_emails = config.allowed_emails
allowed_email_pattern = config.allowed_email_pattern
def email_pattern_allowed(form, field):
    if field.data not in allowed_emails:
        raise ValidationError('Email is not in the allowed list of emails.')
    if not re.search(allowed_email_pattern, field.data):
        raise ValidationError('Email must end with @carbon-waters.com.')
    
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(),email_pattern_allowed])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DeleteAccount(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
########################################
#####  Create forms to gather data #####
########################################
class Form_Matieres_premieres(FlaskForm):
    MP_nom = SelectField('Type', choices=config.matieres_premieres)
    MP_ref_fournisseur = StringField('ref fournisseur', [Length(max=50),DataRequired()]) 
    MP_date_reception = DateTimeField('Date reception', format='%d/%m/%y')
    MP_quantite = FloatField('Quantité', default=20)
    MP_unite = SelectField('unite', choices=config.unitees)
 # name of batch + date of analysis + type of analysis + details analysis
                      # "nom_250129_Raman / nom_250202_DLS / .."
    MP_stock = FloatField('Stock', default=20)
    # submit = SubmitField('Submit New matiere premiere')


class Form_analyses(FlaskForm):
    Analyse_path_to_raw = StringField('local_path', [Length(max=10)])
    Analyse_code = StringField('code_analyse', [Length(max=10)]) 
    submit = SubmitField('Submit New Analyse')


class Form_Batch_XX(FlaskForm):
    Batch_XX_name = StringField('Nom Batch', validators=[NoneOf([],message='Ce batch existe déjà'),Length(max=10)])
    Batch_XX_date = DateTimeField('Date début production', format='%d/%m/%y')
    Batch_XX_Technicien = SelectField('Technicien', choices=config.Techniciens_CW)
    Batch_XX_K_batch =  SelectField('Batch_K_name',choices=[])
    Batch_XX_C_batch =  SelectField('Batch_C_name',choices=[])
    Batch_XX_masse = FloatField('Masse totale (Kg)', default=0.6)
    Batch_XX_Temperature = FloatField('Température agitation', default=50)
    Batch_XX_Agitation = IntegerField('Vitesse agitation',default=250)
    Batch_XX_heure_debut = TimeField('Heure de début', format='%H:%M')
    Batch_XX_heure_fin = TimeField('Heure de fin', format='%H:%M')
    Batch_XX_room_HR = FloatField('Humidité (ppm)', default=0.09)
    Batch_XX_room_T = FloatField('Temperature (°C)', default=25)
    Batch_XX_Stock = FloatField('Stock de XX', default=0)
    Batch_XX_Analyses = StringField('reference_analyses', [Length(max=60)])
    # def validate_unique_batch(self, field):


class Form_Batch_XY(FlaskForm):
    Batch_XY_name = StringField('Nom Batch', validators=[NoneOf([],message='Ce batch existe déjà'),Length(max=10)])
    Batch_XY_date = DateTimeField('Date début production', format='%d/%m/%y')
    Batch_XY_Technicien = SelectField('Technicien', choices=config.Techniciens_CW)
    Batch_XY_XX_batch =  SelectField('Batch_XX_name',choices=[])
    Batch_XY_XX_masse = FloatField('Masse XX utlilisé', default=0.6)
    Batch_XY_YY_batch = SelectField('Batch_YY_name',choices=[])
    Batch_XY_YY_Volume = IntegerField('Volume (L)',default=30)
    Batch_XY_Temperature = FloatField('Température agitation', default=50)
    Batch_XY_Agitation = IntegerField('Vitesse agitation',default=250)
    Batch_XY_heure_debut = TimeField('Heure de début', format='%H:%M')
    Batch_XY_heure_fin = TimeField('Heure de fin', format='%H:%M')
    Batch_XY_room_HR = FloatField('Humidité (ppm)', default=0.09)
    Batch_XY_room_T = FloatField('Temperature (°C)', default=25)
    Batch_XY_Stock = FloatField('Stock de XY', default=0)
    Batch_XY_Analyses = StringField('reference_analyses', [Length(max=60)])

class Form_Produit(FlaskForm):
    Batch_Produit_ref_CW = StringField('Nom Batch', [Length(max=10)])#, validators=[NoneOf([],message='Ce batch existe déjà'),Length(max=10)])
    Batch_Produit_date = DateTimeField('Date début production', format='%d/%m/%y')
    Batch_Produit_Technicien = SelectField('Technicien', choices=config.Techniciens_CW)
    Batch_Produit_XY_batch =  SelectField('Batch_XY_name', choices=[])
    Batch_Produit_XY_Qte = FloatField('Qte XY utitisé', default=50)
    Batch_Produit_additif_batch = SelectField('Batch_additif_name',choices=['Viscosant','Epikote1001','Epikote827'])
    Batch_Produit_additif_Qte = FloatField('Additif Qte',default=250)
    Batch_produit_stock = FloatField('Stock de produit (L)',default=0)
    Batch_Produit_Analyses = StringField('reference_analyses', [Length(max=60)])

class Form_Envoi(FlaskForm):
    Envoi_date_commande = DateTimeField('Date commande', format='%d/%m/%y')
    Envoi_client_name = SelectField('Nom Client', choices=[])
    Envoi_produit_name = SelectField('Type', choices=config.Produits_CW)
    Envoi_produit_batch = SelectField('Reference Batch', choices=[]) 
    Envoi_produit_Qte = FloatField('Qte produit', default=50)
    Envoi_produit_emballage =  StringField('Conditionnement', [Length(max=10)])
    Envoi_date_prevu = DateTimeField('Date envoi prevu', format='%d/%m/%y')
    Envoi_date_effective = DateTimeField('Date envoi effective', format='%d/%m/%y')
    Envoi_code_coli = StringField('Reference coli', [Length(max=50)])
    Envoi_delivered = DateTimeField('Date reception', format='%d/%m/%y')
    Envoi_retour_client = TextAreaField('Metadata')
    Envoi_submit = SubmitField('Valider')

class Confirm_delete(FlaskForm):
    submit = SubmitField('Confirm Delete')


class Form_calculate_K_C(FlaskForm):
    submit = SubmitField('Calculate')
    
class Form_Client(FlaskForm):
    Client_name = StringField('Nom client')
    Client_adresse = StringField('Adresse client')


class Form_submit_training_regr(FlaskForm):
    submit = SubmitField('Actualiser algorithme')
