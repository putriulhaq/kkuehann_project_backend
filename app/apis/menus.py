from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, Blueprint
import psycopg2 
from flask_restx import Namespace, Resource, reqparse
from .db import pool

# Inisialisasi pool koneksi
# pool = ConnectionPool()

# Mendapatkan koneksi dari pool
# conn = pool.get_connection()
# pool = current_app.config.pool

menus = Namespace("menus", description= "Menus's APIS Namespace")

# menusArgs = reqparse.ArgumentParser()
# # menusArgs.add_argument('rate', type=int, help='Rate cannot be converted')
# menusArgs.add_argument('manu_name', type=str,)
# menusArgs.add_argument('description', type=str,)
# menusArgs.add_argument('pricelist', type=str,)

@menus.route("")
class Menus(Resource):
    # @menus.expect(menusArgs)
    def get(self):
        conn = pool.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''
                    SELECT * FROM menu
                ''') 
            res = cur.fetchall()
            cur.close()
            # # conn.close()
            # pool.return_connection(conn)
            # pool.close_all_connections()
            return jsonify(res)
        except Exception as e:
                return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)
    
    def post(self):
        conn = pool.get_connection()
        cur = conn.cursor()
        # args = menusArgs.parser_args()
        try:
            cur.execute(
                '''
                    INSERT into menus
                    (
                        menu_name, 
                        description, 
                        is_deleted, 
                        created_at, 
                        pricelist
                    )
                    values 
                    (
                        %s, 
                        %s,
                        '001002', 
                        'now()', 
                        %s,
                    )
                '''
                ) 
            # res = cur.fetchall()
            # cur.close()
            conn.commit()
            # conn.close()
            pool.return_connection(conn)
            pool.close_all_connections()
            return jsonify("success")
        except Exception as e:
                return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)
    