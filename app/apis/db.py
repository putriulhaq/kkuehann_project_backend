import psycopg2.pool
import atexit
from dotenv import load_dotenv
import os

pool = None 

print(os.getenv('DB_NAME'))

class ConnectionPool:
    def __init__(self):
        self.min_conn = 1
        self.max_conn = 5
        # self.pool = psycopg2.pool.SimpleConnectionPool(self.min_conn, self.max_conn,
        #                                                database="jexlvuum",
        #                                                user="jexlvuum",
        #                                                password="Ck7EFGjj1TJDMXuyNErlslxnj-ZeOSMT",
        #                                                host="rain.db.elephantsql.com",
        #                                                port="5432")
        self.pool = psycopg2.pool.SimpleConnectionPool(
            self.min_conn, 
            self.max_conn,
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )

    def get_connection(self):
        return self.pool.getconn()

    def return_connection(self, conn):
        self.pool.putconn(conn)

    def close_all_connections(self):
        self.pool.closeall()

def initializeConnectionPool():
    global pool
    pool = ConnectionPool()
    print(pool)


# atexit.register(lambda: pool.close_all_connections() if pool else None)

# __all__ = ['pool', 'ConnectionPool', 'initializeConnectionPool']