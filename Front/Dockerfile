# prendre une image de base : https://hub.docker.com/_/python
FROM python:3.10.12


# Variable env
ARG arg_pwd


# Base de donnees
ENV DB_HOST='CW_container_bdd'
ENV DB_PORT='3306'
ENV DB_USER='root'
ENV DB_PASSWORD='pass'
ENV DB='CW_BDD'



# Copier le dossier de votre projet vers un chemin dans l'image
COPY . /src

# se placer dans le bon chemin
WORKDIR /src

# éviter le timeout lors du lancement du serveur
ENV TIMEOUT=60

# mettre à jour les logiciels
RUN apt-get update

# installer les modules python
RUN pip install -r requirements.txt

# exposer le port du serveur web
EXPOSE 8080

# lancer le serveur web

# version environnement de dev
CMD ["python", "__init__.py"]

# version environnement de prod
# CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
