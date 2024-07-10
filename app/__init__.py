# app.py
import sys
import os
from flask_cors import CORS
from flask import Flask, send_from_directory
from flask_restx import Api, Resource


# Tambahkan direktori 'apis' ke dalam sys.path
# current_dir = os.path.dirname(os.path.realpath(__file__))
# apis_dir = os.path.join(current_dir, 'apis')
# sys.path.append(apis_dir)

def create_app():
    
    app = Flask(__name__) 
    api = Api(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

# Inisialisasi pool koneksi
    from .apis.db import ConnectionPool, initializeConnectionPool, pool, psycopg2, atexit
    initializeConnectionPool()

    from .apis.users import users
    from .apis.dash import dash
    from .apis.menus import menus
    from .apis.transaction import transaction
    from .apis.order import order
    from .apis.delivery import delivery
    # from apis.dashboard import dashboard
    import pkgutil


    # Mendaftarkan namespace users
    api.add_namespace(users, path='/users')
    api.add_namespace(menus, path='/menus')
    api.add_namespace(transaction, path='/transaction')
    api.add_namespace(dash, path='/dash')
    api.add_namespace(order, path='/order') 
    api.add_namespace(delivery, path='/delivery') 

     # Route untuk favicon.ico
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    handler = app
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
    # list_modules('apis.db')