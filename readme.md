# 🏭 Suivi de Production Digital

Ce projet est une plateforme **full stack** orchestrée avec `Docker Compose`, dédiée au **suivi de production industriel**. Elle intègre des services **API**, des modèles **machine learning**, une **base de données relationnelle**, une **interface utilisateur**, ainsi qu’un système de **monitoring** via Prometheus et Grafana.

---

## 📦 Architecture générale

Le projet est découpé en plusieurs services indépendants :

```
├── flask-app/           → Interface utilisateur (Flask)
├── fastapi-db/          → API FastAPI pour gestion BDD
├── fastapi-ml/          → API FastAPI pour modèles ML
├── mysql/               → Base de données MySQL
├── prometheus/          → Collecte des métriques
├── grafana/             → Visualisation et alertes
├── docker-compose.yml   → Orchestration multi-container
```

---

## ⚙️ Fonctionnalités principales

### 🧠 FastAPI - Service Machine Learning
Application dédiée à l'entraînement et au déploiement de modèles ML, avec suivi via MLFlow.

#### Dossiers & Fichiers :

- `/app`
  - `main.py` : définition des routes FastAPI
  - `utils_regr.py` : entraînement modèle de régression supervisé
  - `utils_class.py` : entraînement modèle de classification supervisé
  - `utils_pipe.py` : classification non supervisée
  - `/data` : modèles sauvegardés localement
- `/ML-models` : pipeline d’agrégation, nettoyage et entraînement
  - `/ML_supervised/` : scripts et analyses
  - `/ML_unsupervized/` : tests et analyses

#### Routes exposées :
```python
GET     /info                             # Vérifie santé de l'app
POST    /predict/{model_type}            # Prédiction en régression
GET     /variable_importance             # Analyse des variables du modèle
GET     /restart_training_regression     # Relance entraînement régression
GET     /get_fig_uv                      # Résultat classification UV
GET     /get_fig_raman                   # Résultat classification Raman
```

---

### 🗃️ FastAPI - Service Gestion de Base de Données
API sécurisée pour interagir avec la base MySQL via SQLAlchemy.

#### Dossiers & Fichiers :
- `/database/`
  - `db_xxx.py` : logique SQL
  - `models.py` : définition des tables
- `/router/` : endpoints organisés par entité
- `main.py` : point d’entrée
- `schemas.py` : validation des données (Pydantic)

#### Tables principales :
- `DB_Prediction`, `DB_Analyses`, `DB_Matieres_premieres`, `DB_Batch_XX`, `DB_Batch_XY`, etc.

#### Routes CRUD typiques :
```python
POST    /                               # Create
GET     /                               # Read all
GET     /last                           # Read last
GET     /id/{id}                        # Read one by ID
GET     /name/{name}                    # Read one by name
POST    /update/{id}                    # Update
GET     /delete/{id}                    # Delete
```

---

### 🖥️ Flask - Interface Utilisateur
Application web Flask pour le suivi de production, avec authentification et intégration API.

#### Structure :
- `/static/` : Bootstrap CSS
- `/templates/` : HTML
- `app.py` : routes principales
- `config.py` : configuration globale
- `forms.py` : formulaires FlaskForm
- `models.py` : gestion utilisateurs
- `utils.py` : fonctions utilitaires

#### Authentification :
```python
/register
/login
/delete_account
/logout
```

#### Routes principales (exemples) :
```python
/Materiaux
/Nouvelle_matiere_premiere
/Nouveau_batch_XX
/Ajouter_analyses/<batch_name>
/Dashboard_production
/Clients
/Commande
/Envois
/MaJ_retour_Client/<ref_envoi>
```

---

## 📈 Monitoring avec Prometheus & Grafana

### Lancer l’application :
```bash
docker-compose up --build
```

### Vérifier Prometheus :
- Accès navigateur : `http://localhost:9090/targets`
- Vérifiez que `State` = `UP`

> ⚙️ En cas de souci, ajustez les cibles dans `prometheus.yml` :
```yml
- job_name: 'flask'
  static_configs:
    - targets: ['host.docker.internal:5000']
- job_name: 'fastapi_ml'
  static_configs:
    - targets: ['host.docker.internal:8001']
```

### Configurer Grafana :
- Accès : `http://localhost:3000`
- Datasource : Prometheus → `http://host.docker.internal:9090`
- Créez dashboards pour suivre la santé de vos services et alertes

---

## 📂 Tests

- Tous les endpoints API sont testés dans le dossier `/tests`

---

## ☁️ Stockage modèles

- Suivi ML avec **MLFlow**
- Modèles stockés **localement** ou sur **Azure Blob Storage**

---

## 📜 License

Ce projet est open-source sous licence MIT.

 host.docker.internal:5000
