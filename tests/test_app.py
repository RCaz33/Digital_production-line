import doctest
import mysql.connector 


# Add the parent directory to sys.path
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Front import app


def test_connect_to_db():
    """
    Establishes a connection to the MySQL database.
    """
    conn, cursor = connect_to_db()
    assert isinstance(conn, mysql.connector.connection.MySQLConnection)
