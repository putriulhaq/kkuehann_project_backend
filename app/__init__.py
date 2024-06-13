# app.py
import sys
import os

# Tambahkan direktori 'apis' ke dalam sys.path
current_dir = os.path.dirname(os.path.realpath(__file__))
apis_dir = os.path.join(current_dir, 'apis')
sys.path.append(apis_dir)

from flask import Flask
from flask_restx import Api, Resource

# Inisialisasi pool koneksi
from apis.db import ConnectionPool, initializeConnectionPool, pool, psycopg2, atexit
initializeConnectionPool()

from apis.users import users
from apis.dash import dash
from apis.menus import menus
from apis.transaction import transaction
from apis.order import order
# from apis.dashboard import dashboard
import pkgutil

app = Flask(__name__) 
api = Api(app)


# Mendaftarkan namespace users
api.add_namespace(users, path='/users')
api.add_namespace(menus, path='/menus')
api.add_namespace(transaction, path='/transaction')
api.add_namespace(dash, path='/dash')
api.add_namespace(order, path='/order')

if __name__ == "__main__":
    app.run(debug=True)
    # list_modules('apis.db')