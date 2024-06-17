from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, Blueprint
import psycopg2 
from flask_restx import Namespace, Resource, reqparse
import argparse
from .db import pool


transaction = Namespace("transaction", description= "Menus's APIS Namespace")

transactionArgs = reqparse.RequestParser()
# transactionArgs.add_argument('rate', type=int, help='Rate cannot be converted')
transactionArgs.add_argument('transaction_type', type=str,)
transactionArgs.add_argument('transaction_status', type=str,)
transactionArgs.add_argument('transaction_to', type=str,)
transactionArgs.add_argument('description', type=str,)

@transaction.route("")
class Transaction(Resource):
    def get(self):
        if pool:
            print('succes')
        else:
            print('nope')
        conn = pool.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''
                    SELECT 
                        code_value(t.transaction_type, 'eng') as type,
                        code_value(t.transaction_status, 'eng') as status,
                        code_value(t.transaction_to, 'eng') as to
                    FROM transaction t
                ''') 
            res = cur.fetchall()
            return jsonify(res)
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)
    
    @transaction.expect(transactionArgs)
    def post(self):
        conn = pool.get_connection()
        cur = conn.cursor()
        args = transactionArgs.parse_args()
        try:
            cur.execute(
                    """
                    INSERT INTO public."transaction"
                    (
                        transaction_type, 
                        transaction_status, 
                        transaction_to, 
                        decscription
                    )
                    VALUES
                    (
                        %(transaction_type)s, 
                        %(transaction_status)s, 
                        %(transaction_to)s, 
                        %(description)s
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

        
    