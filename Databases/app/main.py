from fastapi import FastAPI, Request
from app.router import Predictions_router, Clients_router, Envoi_router, Produit_router, OGD_router, KC8_router, Matieres_premieres_router,Analyses_router, Techniciens_router

from app.database import models
from app.database.db_connect import engine
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


tags_metadata = [

    {
        "name": "Techniciens_router",
        "description": "Management des **id** de techniciens. Permet d'**anonymiser** les données",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
            {
        "name": "Matieres_premieres_router",
        "description": "Permet de renseigner les matières première utilisées",
    },
        {
        "name": "KC8_router",
        "description": "Permet d'entrer les information de production de l'étape 1",
    },
]

app = FastAPI(openapi_tags=tags_metadata)


app = FastAPI()

app.include_router(Predictions_router.router)
app.include_router(Clients_router.router)
app.include_router(Analyses_router.router)
app.include_router(Matieres_premieres_router.router)
app.include_router(KC8_router.router)
app.include_router(OGD_router.router)
app.include_router(Produit_router.router)
app.include_router(Envoi_router.router)
app.include_router(Techniciens_router.router)


@app.get('/')
def index():
    return {'message': 'Hello world!'}


models.Base.metadata.create_all(engine) # create all table with CREATE IF NOT EXIST LOGIC

# origins = [
#   'http://127.0.0.1:5000'
# ]

# app.add_middleware(
#   CORSMiddleware,
#   allow_origins = origins,
#   allow_credentials = True,
#   allow_methods = ["*"],
#   allow_headers = ['*']
# )

# app.mount('/files', StaticFiles(directory="files"), name='files')



if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app,host="0.0.0.0", port=1000, reload=True)