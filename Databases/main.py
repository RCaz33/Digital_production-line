from fastapi import FastAPI, Request
from router import OGD_router, KC8_router, Matieres_premieres_router,Analyses_router, Techniciens_router

from database import models
from database.db_connect import engine
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles



app = FastAPI()



app.include_router(Analyses_router.router)
app.include_router(Matieres_premieres_router.router)
app.include_router(KC8_router.router)
app.include_router(OGD_router.router)
app.include_router(Techniciens_router.router)


# app.include_router(Step0_router.router)
# app.include_router(Step1_router.router)
# app.include_router(Step2_router.router)
# app.include_router(Step3_router.router)
# app.include_router(Step4_router.router)





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
  uvicorn.run(app,host="0.0.0.0", port=1000)