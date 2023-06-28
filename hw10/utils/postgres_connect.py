from configparser import ConfigParser

from psycopg2 import connect, Error
from contextlib import contextmanager


config = ConfigParser()
config.read('hw10/utils/postgres_config.ini')

user = config.get('DB', 'user')
password = config.get('DB', 'password')
host = config.get('DB', 'host')
port = config.get('DB', 'port')
db_name = config.get('DB', 'db_name')


@contextmanager
def connection():
    conn = None
    
    try:
        conn = connect(dbname=db_name, user=user, password=password, host=host, port=port)
        yield conn
        conn.commit()
    except Error as error:
        print(error)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()   