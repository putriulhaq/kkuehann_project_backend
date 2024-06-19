from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, Blueprint
import psycopg2 
from flask_restx import Namespace, Resource, reqparse
from .db import pool
from psycopg2.extras import DictCursor


menus = Namespace("menus", description= "Menus's APIS Namespace")

menusArgs = reqparse.RequestParser()
# menusArgs.add_argument('rate', type=int, help='Rate cannot be converted')
menusArgs.add_argument('menu_name', type=str,)
menusArgs.add_argument('description', type=str,)
menusArgs.add_argument('priceist', type=str,)

@menus.route("")
class Menus(Resource):
    # @menus.expect(menusArgs)
    def get(self):
        conn = pool.get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        try:
            cur.execute(
                '''
                    SELECT * FROM menu
                ''') 
            res = cur.fetchall()
            cur.close()
            result = []
            for row in res:
                transformed_row = {"menu_id": row["menu_id"], "menu_name": row["menu_name"], "pricelist": row["priceist"], "description": row["description"]}
                result.append(transformed_row)

            return jsonify(result) 
            # return jsonify()
        except Exception as e:
                return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)
    
    @menus.expect(menusArgs)
    def post(self):
        conn = pool.get_connection()
        cur = conn.cursor()
        args = menusArgs.parse_args()
        try:
            cur.execute(
                """
                    INSERT into menu
                    (
                        menu_name,
                        description, 
                        is_deleted, 
                        created_at, 
                        priceist
                    )
                    VALUES 
                    (
                        %(menu_name)s, 
                        %(description)s,
                        '001002', 
                        'now()', 
                        %(priceist)s
                    )
                    """, 
                args
                ) 
            conn.commit()
            return jsonify({"status": "success"})
        except Exception as e:
                return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)
    