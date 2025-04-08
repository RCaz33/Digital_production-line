

# Monitorer l'application 
* récupérer métriques avec prometheus 
* visualiser et alerter avec graphana


```
docker-compose up --build   # ligne de commande
localhost:9090/targets      # navigateur
    --> vérifier "State" est "UP"
    --> si non, re-configurer targets dans prometheus.yml --host
            flask http://host.docker.internal:5000 
            fastapi_ml http://host.docker.internal:8001 
    
http://localhost:3000/connections/datasources/new # navigateur
    --> sélectionner Pometheus
    --> iniquer meme URL que prometheus.yml http://host.docker.internal:9090

http://localhost:3000/dashboard/new # navigateur
    --> configurer metriques```

