from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, StringField, SubmitField, DateTimeField, FloatField, IntegerField, TimeField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, AnyOf, ValidationError, Email

import datetime
import re
import config
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
    submit = SubmitField('Submit New matiere premiere')


class Form_analyses(FlaskForm):
    Analyse_path_to_raw = StringField('local_path', [Length(max=10)])
    Analyse_code = StringField('code_analyse', [Length(max=10)]) 
    submit = SubmitField('Submit New Analyse')


class Form_Batch_KC8(FlaskForm):
    Batch_KC8_name = StringField('Nom Batch', [Length(max=10)])
    Batch_KC8_date = DateTimeField('Date début production', format='%d/%m/%y')
    Batch_KC8_Technicien = SelectField('Technicien', choices=config.Techniciens_CW)
    Batch_KC8_K_batch =  StringField('Batch_K_name')
    Batch_KC8_C_batch =  StringField('Batch_C_name')
    Batch_KC8_masse = FloatField('Masse totale (Kg)', default=0.6)
    Batch_KC8_Temperature = FloatField('Température agitation', default=50)
    Batch_KC8_Agitation = IntegerField('Vitesse agitation',default=250)
    Batch_KC8_heure_debut = TimeField('Heure de début', format='%H:%M')
    Batch_KC8_heure_fin = TimeField('Heure de fin', format='%H:%M')
    Batch_KC8_room_HR = FloatField('Humidité (ppm)', default=0.09)
    Batch_KC8_room_T = FloatField('Temperature (°C)', default=25)
    Batch_KC8_Analyses = StringField('reference_analyses', [Length(max=60)])

class Form_Batch_OGD(FlaskForm):
    Batch_OGD_name = StringField('Nom Batch', [Length(max=10)])
    Batch_OGD_date = DateTimeField('Date début production', format='%d/%m/%y')
    Batch_OGD_Technicien = SelectField('Technicien', choices=config.Techniciens_CW)
    Batch_OGD_KC8_batch =  StringField('Batch_KC8_name')
    Batch_OGD_KC8_masse = FloatField('Masse KC8 utliisé', default=50)
    Batch_OGD_THF_batch = StringField('Batch_THF_name')
    Batch_OGD_THF_Volume = IntegerField('Volume (mL)',default=250)
    Batch_OGD_Temperature = FloatField('Température agitation', default=50)
    Batch_OGD_Agitation = IntegerField('Vitesse agitation',default=250)
    Batch_OGD_heure_debut = TimeField('Heure de début', format='%H:%M')
    Batch_OGD_heure_fin = TimeField('Heure de fin', format='%H:%M')
    Batch_OGD_room_HR = FloatField('Humidité (ppm)', default=0.09)
    Batch_OGD_room_T = FloatField('Temperature (°C)', default=25)
    Batch_OGD_Analyses = StringField('reference_analyses', [Length(max=60)])

class Form_Produit(FlaskForm):
    Batch_Produit_ref_CW = StringField('Nom Batch', [Length(max=10)])
    Batch_Produit_date = DateTimeField('Date début production', format='%d/%m/%y')
    Batch_Produit_Technicien = SelectField('Technicien', choices=config.Techniciens_CW)
    Batch_Produit_OGD_batch =  StringField('Batch_OGD_name')
    Batch_Produit_OGD_Qte = FloatField('Qte OGD utliisé', default=50)
    Batch_Produit_additif_bacth = StringField('Batch_additif_name')
    Batch_Produit_additif_Qte = IntegerField('Additif Qte',default=250)
    Batch_Produit_Analyses = StringField('reference_analyses', [Length(max=60)])

class Form_Envoi(FlaskForm):
    Envoi_date_commande = DateTimeField('Date commande', format='%d/%m/%y')
    Envoi_client_name = StringField('Nom Client', [Length(max=10)])
    Envoi_produit_name = SelectField('Type', choices=config.Produits_CW)
    Envoi_produit_batch = StringField('Reference Batch', [Length(max=10)])
    Envoi_produit_Qte = FloatField('Qte produit', default=50)
    Envoi_produit_emballage =  StringField('Conditionnement', [Length(max=10)])
    Envoi_date_prevu = DateTimeField('Date envoi prevu', format='%d/%m/%y')
    Envoi_date_effective = DateTimeField('Date envoi effective', format='%d/%m/%y')
    Envoi_code_coli = StringField('Reference coli', [Length(max=50)])
    Envoi_retour_client = TextAreaField('Metadata')
    Envoi_submit = SubmitField('Nouvelle demande')

class Confirm_delete(FlaskForm):
    submit = SubmitField('Confirm Delete')


class Form_calculate_K_C(FlaskForm):
    submit = SubmitField('Calculate')
    
