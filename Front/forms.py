from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, DateTimeField, FloatField, IntegerField, TimeField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, AnyOf, ValidationError, Email
import datetime
import re


########################################
#####  Create forms to login users #####
########################################

allowed_email_pattern = r'@carbon-waters.com'  # Example pattern: email must end with @example.com
allowed_emails=['a@carbon-waters.com','b@carbon-waters.com','c@carbon-waters.com']
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
    MP_nom = SelectField('Type', choices=[
        ('C', 'Carbone'),
        ('K', 'Potassium'),
        ('THF', 'Solvant THF')
    ])
    MP_codeCW = SelectField('Code CW', choices=[f'CW_00{i}' for i in range(1,10)])
    MP_ref_fournisseur = StringField('ref fournisseur', [Length(max=50)]) 
    MP_quantite = FloatField('Quantité', default=20)
    MP_unite = SelectField('unite', choices=[
        ('L', 'Litres'),
        ('Kg', 'Kilogrammes'),
        ('g', 'grammes')
    ])
 # name of batch + date of analysis + type of analysis + details analysis
                      # "nom_250129_Raman / nom_250202_DLS / .."
    submit = SubmitField('Submit New matiere premiere')

class Form_analyses(FlaskForm):
    Analyse_path_to_raw = StringField('local_path', [Length(max=10)])
    Analyse_code = StringField('code_analyse', [Length(max=10)]) 
    submit = SubmitField('Submit New Analyse')


class Form_Batch_KC8(FlaskForm):
    __tablename__ = 'Batch_KC8'
    Batch_KC8_name = StringField('Nom Batch', [Length(max=10)])
    Batch_KC8_date = DateTimeField('Date début production', format='%d%m%y')
    Batch_KC8_Technicien = StringField('Technicien', [Length(max=10)])
    Batch_KC8_K_batch =  StringField('Batch_K_name')
    Batch_KC8_C_batch =  StringField('Batch_C_name')
    Batch_KC8_masse = IntegerField('Masse totale',[NumberRange(min=0, max=1000)], default=20)
    Batch_KC8_Temperature = FloatField('Température agitation', default=50)
    Batch_KC8_Agitation = IntegerField('Vitesse agitation',default=250)
    Batch_KC8_heure_debut = TimeField('Heure de début', format='%H:%M')
    Batch_KC8_heure_fin = TimeField('Heure de début', format='%H:%M')
    Batch_KC8_room_HR = FloatField('Humidité (ppm)', default=0.09)
    Batch_KC8_room_T = FloatField('Temperature (°C)', default=25)
    Batch_KC8_Analyses = StringField('reference_analyses', [Length(max=60)])

class Form_Batch_OGD(FlaskForm):
    Batch_OGD_name = StringField('Nom Batch', [Length(max=10)])
    Batch_OGD_date = DateTimeField('Date début production', format='%d%m%y')
    Batch_OGD_Technicien = StringField('Technicien', [Length(max=10)])
    Batch_OGD_KC8_batch =  StringField('Batch_KC8_name')
    Batch_OGD_KC8_masse = FloatField('Masse KC8 utliisé', default=50)
    Batch_OGD_THF_batch = StringField('Batch_THF_name')
    Batch_OGD_THF_Volume = IntegerField('Volume (mL)',default=250)
    Batch_OGD_Temperature = FloatField('Température agitation', default=50)
    Batch_OGD_Agitation = IntegerField('Vitesse agitation',default=250)
    Batch_OGD_heure_debut = TimeField('Heure de début', format='%H:%M')
    Batch_OGD_heure_fin = TimeField('Heure de début', format='%H:%M')
    Batch_OGD_room_HR = FloatField('Humidité (ppm)', default=0.09)
    Batch_OGD_room_T = FloatField('Temperature (°C)', default=25)
    Batch_OGD_Analyses = StringField('reference_analyses', [Length(max=60)])



class Form_2023_S0(FlaskForm):
    Step0_Batchid = IntegerField('Batch_id')
    Step0_BatchName = StringField('#Batch OGD', [Length(max=10)])
    Step0_BatchTHF = StringField('#Batch THF', [Length(max=10)])
    submit = SubmitField('Submit New Batch')


class Form_2023_S1(FlaskForm):
    Step1_Date = DateTimeField('Date début production', format='%d%m%y')
    Step1_Initiales = StringField('Initiales', [Length(max=5), 
                                                AnyOf(['FB','IT','CD','JP','NM','MM','RS','WL'], 
                                                      message="Initiales non reconnues : Contacter service IT pour ajout BDD")])

    Step1_KC8_Batch = StringField('nom du batch de KC8', [Length(max=20)])
    Step1_KC8_Masse = FloatField('Masse KC8 (g)', default=20)
    Step1_KC8_VTHF = IntegerField('Volume THF (mL)',[NumberRange(min=0, max=1000)], default=500)

    Step1_Exfoliation_RefPlaque = IntegerField('Ref plaque agit')
    Step1_Exfoliation_Vitesse = IntegerField('Vitesse plaques (rpm)', default=230)
    Step1_Exfoliation_Heure = TimeField('Heure de début', format='%H:%M')

    Step1_env_Lab_H2O = FloatField('Labo humidité (%)', [NumberRange(min=0, max=100)], default=0)
    Step1_env_Lab_T = FloatField('Labo température (°C)', [NumberRange(min=-10, max=40)], default=0)
    Step1_env_GloveBox_T = FloatField('BaG température (°C)', [NumberRange(min=-10, max=40)], default=0)
    Step1_env_GloveBox_H2O = FloatField('BaG H2O (ppm)', [NumberRange(min=0, max=50)], default=0)
    Step1_env_GloveBox_O2 = FloatField('BaG O2 (ppm)', [NumberRange(min=0, max=50)], default=0)

    Step1_Observation = StringField('Observation Etape graphenure')

    submit = SubmitField('Submit Infos Step 1')


class Form_2023_S2(FlaskForm):
    Step2_Date = DateTimeField('Date', format='%d%m%y')
    Step2_Initiales = StringField('Initiales', [Length(max=5), 
                                                AnyOf(['FB','IT','CD','JP','NM','MM','RS','WL'], 
                                                      message="Initiales non reconnues : Contacter service IT pour ajout BDD")])

    Step2_Ajout_jourJ = BooleanField('Ajout J-1', default=False)
    Step2_AjoutTHF_Heure = TimeField("Heure deuxieme d'ajout", format='%H:%M')
    Step2_AjoutTHF_VTHF = IntegerField('Volume THF (mL)',[NumberRange(min=0, max=1000)], default=500)

    Step2_Sedimentation_StartHeure = TimeField('Heure début sédimentation', format='%H:%M')
    Step2_Sedimentation_EndHeure = TimeField('Heure fin sédimentation', format='%H:%M')
    Step2_Sedimentation_Sediments = StringField('Observations')

    Step2_CtrlVisuel = StringField('Controle visuel apres centrifugation')

    Step2_env_Lab_H2O = FloatField('Labo humidité (%)', [NumberRange(min=0, max=100)], default=0)
    Step2_env_Lab_T = FloatField('Labo température (°C)', [NumberRange(min=-10, max=40)], default=0)
    Step2_env_GloveBox_T = FloatField('BaG température (°C)', [NumberRange(min=-10, max=40)], default=0)
    Step2_env_GloveBox_H2O = FloatField('BaG H2O (ppm)', [NumberRange(min=0, max=50)], default=0)
    Step2_env_GloveBox_O2 = FloatField('BaG O2 (ppm)', [NumberRange(min=0, max=50)], default=0)
    Step2_Observation = StringField('Observation Etape THF')

    Step2_Centrifugation = BooleanField('Batch centrifugé ?')
    submit = SubmitField('Submit Info Step 2')


class Form_2023_S3(FlaskForm):
    Step3_Date = DateTimeField('Date', format='%d%m%y')
    Step3_Initiales = StringField('Initiales', [Length(max=5), 
                                                AnyOf(['FB','IT','CD','JP','NM','MM','RS','WL'], 
                                                      message="Initiales non reconnues : Contacter service IT pour ajout BDD")])
    

    Step3_Ox_Debit = FloatField('Debit air synthétique (nL/min)', [NumberRange(min=0, max=50)], default=0)
    Step3_Ox_Temps = FloatField('Durée (s)', default=30)

    Step3_env_Lab_H2O = FloatField('Labo humidité (%)', [NumberRange(min=0, max=100)])
    Step3_env_Lab_T = FloatField('Labo température (°C)', [NumberRange(min=-10, max=40)])

    Step3_Observations =  StringField('Observation Etape oxidation')

    submit = SubmitField('Submit Info Step 3')


class Form_2023_S4(FlaskForm):

    Step4_Date = DateTimeField('Date', format='%d%m%y')
    Step4_Initiales = StringField('Initiales', [Length(max=5), 
                                                AnyOf(['FB','IT','CD','JP','NM','MM','RS','WL'], 
                                                      message="Initiales non reconnues : Contacter service IT pour ajout BDD")])

    Step4_Analyse_mOGD = FloatField('mOGD (g)', [NumberRange(min=0, max=10)],default=0)
    Step4_Analyse_mTHF = FloatField('mTHF (g)', [NumberRange(min=0, max=10)],default=0)
    Step4_Analyse_UV_800nm = FloatField('Valeur absorbance à 800 nm',default=0)

    Step4_Resultat_MesureUV = FloatField('Concentration OGD', [NumberRange(min=0, max=10)])
    Step4_Resultat_Categorie = IntegerField('Catégorie', [NumberRange(min=-1, max=3)])

    Step4_Stockage_type = StringField('Bouteille ? / Volume ?',default='na')
    Step4_Stockage_Emplacement = StringField('Paillasse ? / BaG ?',default='na')
    Step4_Stockage_Utilisation = StringField('Utilisation ? / Livraison ?',default='na')

    Step4_Observations =  StringField('Observation Etape oxidation')

    submit = SubmitField("Submit Info Step 4")



class Form_KC8(FlaskForm):
    # Batch_KC8_id = IntegerField('Batch_id')
    KC8_Date = DateTimeField('Date', format='%d%m%y')
    KC8_Initiales = StringField('Initiales', [Length(max=5), 
                                                AnyOf(['FB','IT','CD','JP','NM','MM','RS','WL'], 
                                                      message="Initiales non reconnues : Contacter service IT pour ajout BDD")])
    Batch_KC8_name = StringField('#Batch KC8', [Length(max=10)])
    KC8_Lab_HR = FloatField('Labo humidité (%)', [NumberRange(min=0, max=100)])
    KC8_Lab_T= FloatField('Labo température (°C)', [NumberRange(min=-10, max=40)])
    KC8_BaG_T = FloatField('BaG température (°C)', [NumberRange(min=-10, max=40)])
    KC8_BaG_O2_ppm = FloatField('BaG O2 (ppm)', [NumberRange(min=0, max=50)], default=0)
    KC8_Bag_H20_ppm = FloatField('BaG H2O (ppm)', [NumberRange(min=0, max=100)])
    KC8_Batch_Graphite = StringField('Batch Graphite',default='A1.')
    KC8_Batch_K = StringField('Batch Potassium',default='10224825')
    KC8_masse_K = FloatField('Masse Potassium',default='4.')
    KC8_masse_C = FloatField('Masse Carbone',default='10.')
    KC8_Heating_thermostat_ref = StringField('Reference thermostat',default='3')
    KC8_Heating_Start_Heure = TimeField("Heure debut chauffage", format='%H:%M')
    KC8_Heating_End_Heure = TimeField("Heure fin chauffage", format='%H:%M')
    KC8_Visual_verification  = BooleanField('Batch OK ?')
    KC8_Observation = StringField('Observations',default='na')
    KC8_Analsysis_date = DateTimeField('Date analyse', format='%d%m%y')
    KC8_Analysis_Initiales = StringField('Initiales', [Length(max=5), 
                                                AnyOf(['FB','IT','CD','JP','NM','MM','RS','WL'], 
                                                      message="Initiales non reconnues : Contacter service IT pour ajout BDD")])
    KC8_Analysis_validation = BooleanField('Batch validé ?')
    KC8_Analysis_Observation = StringField('Observations analyse',default='na')
    submit = SubmitField("Submit Info Batch KC8")

    