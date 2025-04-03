from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
load_dotenv()


db_user = os.getenv('LOCAL_DB_USER') #os.environ['DB_USER']
db_pass = os.getenv('LOCAL_DB_PASS') #os.environ['DB_PASS']
db_name = os.getenv('LOCAL_DB_BDD') #os.environ['DB_NAME']
db_host=os.getenv('LOCAL_DB_HOST')

MYSQL_DATABASE_URL = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:3306/{db_name}"

engine = create_engine(
    MYSQL_DATABASE_URL, #connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

### create all the tables
from app.database.models import *
Base.metadata.create_all(engine)




def get_db():  #get_session
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()