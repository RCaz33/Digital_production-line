# Get python
FROM python:3.12-slim

# Definir le working directory du container
WORKDIR /app_db

# copie le fichier des requirements
COPY requirements.txt /app_db/requirements.txt

# Installe les ressources necesssaires
RUN pip install --no-cache-dir -r /app_db/requirements.txt

# Copie l'ensembel des fichiers
COPY /app/ /app_db/app

# Expose le port pour acceder au container depuis l'exterieur
EXPOSE 8002

RUN ls -l /app_db/app


# Lancer l'app
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8002"]
