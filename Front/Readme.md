# Application Flask pour suivi de production

Interface utilisateur pour la gestion de production.
Utilise API Database pour intéragir avec la base de données.
Utilise API ML pour utiliser les modèles IA.


/static : configuration boostrap css
/templates : html
app.py : routes
config.py : références produits, codes entreprise, codes ISO, techniciens, email autorisés
forms.py : formulaires FlaskForm avec validateur de champs
models.py : gestion de utilisateurs avec sécurité authentification werkzeug.security
utils.py : fonction utilitaires pour l'application



Les routes:
@app.route('/register', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
@app.route('/delete_account', methods=['POST'])
@app.route('/logout')

@login_required pou toutes les routes suivantes
@app.route("/Materiaux", methods=["GET","POST"])
@app.route("/Nouvelle_matiere_premiere", methods=['GET','POST'])
@app.route("/Inspecter_matiere_premiere/<MP_ref_fournisseur>", methods=['GET', 'POST'])
@app.route("/Nouveau_batch_KC8", methods=['GET','POST'])
@app.route("/Nouveau_batch_OGD", methods=['GET','POST'])
@app.route("/Nouveau_batch_produit/<produit>", methods=['GET','POST'])
@app.route("/Update_default_batch", methods=['GET','POST'])
@app.route("/MaJ_batch_OGD/<batch_name>",methods=["GET","POST"])
@app.route("/MaJ_batch_KC8/<batch_name>",methods=["GET","POST"])
@app.route('/Ajouter_analyses/<batch_name>', methods=['GET',"POST"])
@app.route('/del_KC8/<batch_name>', methods=['GET'])
@app.route('/del_OGD/<batch_name>', methods=['GET','POST'])
@app.route("/Cahier_production",methods=["GET","POST"])
@app.route("/Dashboard_production",methods=["GET","POST"])
@app.route("/Dashboard_ML", methods=['GET','POST'])
@app.route("/Dashboard_commerce",methods=["GET","POST"])
@app.route("/Clients", methods=['GET','POST'])
@app.route("/Commande",methods=["GET","POST"])
@app.route("/Envois",methods=["GET","POST"])
@app.route("/Suivi_envois",methods=["GET","POST"])
@app.route("/MaJ_retour_Client/<ref_envoi>",methods=["GET","POST"])


Les utilitaires
def update_preds_from_UV(batch_name,conc):
    """ met à jour les prédictions de concentration réelle dans la BDD """
def update_MPs():
    """ met à jour les stocks disponibles des matières premières """
def predict_OGD_concentration(data,heure_debut):
    """ route protégée 
    utilise API_ML pour prédire la concentration de graphene dans l'OGD"""
def format_datetime(date,heure):
    """ transforme les dates et heures en format datetime """
def fetch_MP():
    """ fetch les derniers batch de matieres premieres et de KC8 """    
def update_stock_product(data):
        """ met à jour le stock des produits après envoie de batch """
def update_stock_OGD_additif(data):
        """ met à jour le stock des OGD et des additifs après fabrication produit """
def update_stocks_K_C(data):
        """ met à jour le stock de K et C après fabrication de KC8 """
def update_stocks_KC8_THF(data):
        """ met à jour le stock de KC8 et THF après fabrication de OGD """
def populate_form(form,response):
    """ renseigne les champ du form avec la data de l'API """
def get_last_10_batch():
    """ recupere les 10 derniers batch de matieres premieres et de KC8 """
def get_matieres_premieres(response):
    """ recupere les dernieres matieres premieres """
class get_material_composition_for_product:
    """ compute the qty of material needed as a function of product
    ratio are base on 1L OGD at 2 g/L ==> 2 grams of OGD
    On multiplie le facteur par la quantité de produit fini voulue pour avoir la masse de produit utilise (cf mail Victor 18/02/25)
    # UPDATE WITH CALCULATION DEPENDING ON QTY
    """