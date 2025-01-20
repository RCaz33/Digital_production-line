from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


db_user = 'root' #os.environ['DB_USER']
db_pass = 'pass' #os.environ['DB_PASS']
db_name = 'CW_BDD' #os.environ['DB_NAME']

MYSQL_DATABASE_URL = f"mysql+mysqlconnector://{db_user}:{db_pass}@localhost:3306/{db_name}"

engine = create_engine(
    MYSQL_DATABASE_URL, #connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():  #get_session
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()