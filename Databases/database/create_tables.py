
#### declarative base --> create all to instanciate table in the BDD
from db_connect import engine
from models import DB_Analyses,DB_Matieres_premieres,DB_Batch_KC8,DB_Batch_OGD
from sqlalchemy.orm import declarative_base
Base = declarative_base()
Base.metadata.create_all(bind=engine)


print(engine)
#### --------------------------------------------
