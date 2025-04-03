# Fast API pour le gestion de la base de données

Application pour intéragir avec la base de données de façon sécurisé.

/database : CRUDE
    |-db_xxx.py : logiques SQL avec sqlalchemy
    |-models.py : définition des tables de la BDD
/router : endpoints 
    |-xxx_router.py : .get('name/{name}') .post('update/{id}')
main.py : logique d'application / tags_metadata
schemas.py : classes pydantic pour validation du format des données / sécurité



Tables BD:
 DB_Prediction(Base):
 DB_Analyses(Base):
 DB_Matieres_premieres(Base):
 DB_Batch_XX(Base):
 DB_Batch_XY(Base):
 DbTechnicient(Base):
 DB_Batch_Produit(Base):
 DB_Envoi(Base):
 DB_Client(Base):


Routes communes:
Create 
@router.post('/', response_model=Base)
Read all 
@router.get('/', response_model=List[Base])
Read last
@router.get('/last', response_model=Base)
Read one  BY ID
@router.get('/id/{id}', response_model=Base)
Read one  BY NAME
@router.get('/name/{name}', response_model=Base)
Update 
@router.post('/update/{id}')
Delete 
@router.get('/delete/{id}')
