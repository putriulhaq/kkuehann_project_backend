from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, Blueprint
import psycopg2 
from flask_restx import Namespace, Resource, reqparse
import argparse
from .db import pool
from psycopg2.extras import DictCursor


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
        cur = conn.cursor(cursor_factory=DictCursor)
        try:
            cur.execute(
                '''
                    SELECT 
                        t.transaction_id,
                        code_value(t.transaction_type, 'eng') as transaction_type,
                        code_value(t.transaction_status, 'eng') as transaction_status,
                        code_value(t.transaction_to, 'eng') as transaction_to,
                        t.decscription as description,
                        od.*,
                        c.*
                    FROM transaction t
                    LEFT JOIN order_detail od on od.transaction_id = t.transaction_id
                    LEFT JOIN customer c on c.customer_id = od.customer_id
                ''') 
            res = cur.fetchall()

            result = []
            for row in res:
                transformed_row = {"transaction_id": row["transaction_id"], "transaction_status": row["transaction_status"], "transaction_type": row["transaction_type"], "transaction_to": row["transaction_to"], "description": row["description"]}
                result.append(transformed_row)
                
            return jsonify(result)
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

        
    