from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, Blueprint
import psycopg2 
from flask_restx import Namespace, Resource, reqparse
import argparse
from .db import pool


order = Namespace("order", description= "Menus's APIS Namespace")

orderArgs = reqparse.RequestParser()
# orderArgs.add_argument('rate', type=int, help='Rate cannot be converted')
# orderArgs.add_argument('order_type', type=str,)
# orderArgs.add_argument('order_status', type=str,)
# orderArgs.add_argument('order_to', type=str,)
# orderArgs.add_argument('description', type=str,)

@order.route("")
class Order(Resource):
    def get(self):
        if pool:
            print('succes')
        else:
            print('nope')
        conn = pool.get_connection()
        cur = conn.cursor()
        cur.execute(
            '''
                select
                    od.*
                from
                    "order" o
                join "order_detail" od on
                    o.order_id = od.order_id
                join transaction t on t.transaction_id = od. transaction_id
                join customer c on c.customer_id = od.customer_id
            ''') 
        res = cur.fetchall()
        cur.close()

        pool.return_connection(conn)
        pool.close_all_connections()
        return jsonify(res)
    
    # @transaction.expect(transactionArgs)
    # def post(self):
    #     conn = pool.get_connection()
    #     cur = conn.cursor()
    #     args = transactionArgs.parse_args()
    #     print(args)
    #     cur.execute(
    #             """
    #             INSERT INTO public."transaction"
    #             (
    #                 transaction_type, 
    #                 transaction_status, 
    #                 transaction_to, 
    #                 description
    #             )
    #             VALUES
    #             (
    #                 %(transaction_type)s, 
    #                 %(transaction_status)s, 
    #                 %(transaction_to)s, 
    #                 %(description)s
    #             )
    #             """,
    #             args
    #         )
    #     conn.commit()
    #     pool.return_connection(conn)
    #     # pool.close_all_connections()
    #     return jsonify({"status": "success"})

        
    