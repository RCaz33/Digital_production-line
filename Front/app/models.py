from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# une classe utilisateur qui interagit directement avec la base de données via mysql.connector
import mysql.connector as bdd_connect

import os
from dotenv import load_dotenv
load_dotenv()

def get_db_connection():
    BDD_CW = bdd_connect.connect(host=os.getenv('LOCAL_DB_HOST'),
                                user=os.getenv('LOCAL_DB_USER'),
                                password=os.getenv('LOCAL_DB_PASS'),
                                database=os.getenv('LOCAL_DB_BDD'),
                                port=3306
                                )
    curseur = BDD_CW.cursor(dictionary=True)
    return BDD_CW, curseur

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, name):
        self.id = id
        self.email = email
        self.password = password
        self.name = name

    @staticmethod
    def get(user_id):
        BDD_CW, cursor = get_db_connection()
        # cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Utilisateurs WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        BDD_CW.close()
        if user:
            return User(user['id'], user['email'], user['password'], user['name'])
        return None



    @staticmethod
    def find_by_email(email):
        BDD_CW, cursor = get_db_connection()
        # cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Utilisateurs WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        BDD_CW.close()
        if user:
            return User(user['id'], user['email'], user['password'], user['name'])
        return None

    @staticmethod
    def create(email, password, name):
        hashed_password = generate_password_hash(password)
        print(10*"*\n",len(hashed_password),"\n",10*"*\n")
        BDD_CW, cursor = get_db_connection()
        # cursor = conn.cursor()
        cursor.execute("INSERT INTO Utilisateurs (email, password, name) VALUES (%s, %s, %s)", (email, hashed_password, name))
        BDD_CW.commit()
        cursor.close()
        BDD_CW.close()

    def check_password(self, password):
        return check_password_hash(self.password, password)


    # RGPD
    @staticmethod
    def delete(email):
        BDD_CW, conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE * FROM Utilisateurs WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return f"Entry for {email} deleted (details:{user})"
