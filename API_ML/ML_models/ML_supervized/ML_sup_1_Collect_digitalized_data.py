# initialisation des dependences
import logging
import pandas as pd
import click
import mysql.connector as bdd_connect
import datetime

from dotenv import load_dotenv
import os
load_dotenv()



# point de lancement
@click.command()
@click.option("--host", default='localhost', help="host for the bdd")
@click.option("--user", prompt='User', help="username to connect to BDD")
@click.option("--password", prompt='Password',help="passord to connect to BDD") 
@click.option("--db", default=os.getenv('CW_DB_NAME'),help="database name")
@click.option("--port", default=3306,help="connexion port")

# fonction pour gérer les erreurs de connexions
def collect_from_bdd(host : str ,
                   user : str,
                   password : str,
                   db : str ,
                   port : int ):  
    """
    Cette fonction permet de collecter les données depuis une base de données externe
    et de les sauvegarder dans un fichier
    """
    # connexion a la base de donnée
    try : 
        BDD_CW = bdd_connect.connect(host=host,
                                    user=user,
                                    password=password,
                                    database=db,
                                    port=port)
        curseur = BDD_CW.cursor()

        # Query avec docstring pour eviter SQL insertion
        to_execute = f"SELECT *\
            FROM Batch_OGD AS BO\
            INNER JOIN Etape1_lancement AS E1 ON BO.Batch_id=E1.Batch_id\
            INNER JOIN Etape2_THF_Sedim_Centri AS E2 ON BO.Batch_id=E2.Batch_id\
            INNER JOIN Etape3_Oxydation AS E3 ON BO.Batch_id=E3.Batch_id\
            INNER JOIN Etape4_CtrlQualite AS E4 ON BO.Batch_id=E4.Batch_id\
                AND E4.QC_Conc_OGD!=0"
        curseur.execute(to_execute)

        # Fetch data 
        rows=curseur.fetchall()
        curseur.close()
        BDD_CW.close()

        # Export
        df = pd.DataFrame(rows, columns=[i[0] for i in curseur.description])
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        os.makedirs("data", exist_ok=True)
        df.to_csv(f'data/{today}_data_production.csv', index=False)

    except Exception as e:
        logging.error(f" Cannot connect to database\nRequest failed: {e}")

if __name__ == '__main__':
    collect_from_bdd()
