

1. add route in main.py

2. create db_ogd_step2.py in /database
    -> requires schemas
    -> requires databse.models


3. create step2/Display in shemas.py

4. create DbForm_S2 in models.py

5. confirm same variable name as in schemas.py

6. in /router create CRUD
    -> requires step2/Base in schemas.py

7. in /database create db_ogd_step2.py

8. in /router update Step2_router.py with 
    -> CRUD function from db_ogd_step2.py to get data
    -> BaseModel from shemas.py to pass data



9. create all the tables