from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, Blueprint
import psycopg2 
from flask_restx import Namespace, Resource, reqparse
import argparse
from .db import pool
from psycopg2.extras import DictCursor


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
    def post(self):
        conn = pool.get_connection()
        cur = conn.cursor()
        # args = transactionArgs.parse_args()
        # print(args)
        cur.execute(
                """
                WITH cust AS (
                        INSERT INTO public."customer" (cust_name, address, no_tlp)
                        VALUES ('Ulhaq', 'Pancoran', '081280583884')
                        RETURNING customer_id
                    ),
                    -- Insert into the order_detail table using the customer_id from the previous step and get the order_detail_id
                    detail_order AS (
                        INSERT INTO public.order_detail (customer_id, upd_date_order, req_date_order, address_order, created_at)
                        SELECT customer_id, NOW(), NOW(), 'Paris', NOW()
                        FROM cust
                        RETURNING order_detail_id
                    ),
                    -- Insert into the order table using the order_detail_id from the previous step and get the order_detail_id
                    order_insert AS (
                        INSERT INTO public."order" (order_detail_id, menu_id, quantity, order_status)
                        SELECT order_detail_id, 1, 2, '002001'
                        FROM detail_order
                        RETURNING order_detail_id
                    )
                    -- Insert into the transaction table using the order_detail_id from the previous step
                    INSERT INTO public."transaction" (
                        transaction_id,
                        transaction_type,
                        transaction_status,
                        transaction_to,
                        order_detail_id
                    )
                    SELECT 
                        NEXTVAL('transaction_id_seq'), -- Assuming you have a sequence for transaction_id
                        '002001', -- Replace with actual transaction type
                        '003001', -- Replace with actual transaction status
                        '004001', -- Replace with actual transaction to
                        order_detail_id
                    FROM order_insert;
                """,
            )
        conn.commit()
        pool.return_connection(conn)
        # pool.close_all_connections()
        return jsonify({"status": "success"})

@order.route('/latest-order')
class LatestOrder(Resource):
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
                with total_price as (
                select 
                    o.menu_id, 
                    o.quantity,
                    o.order_detail_id,
                    count(o.quantity) * cast(m.priceist as integer) as total
                from "order" o 
                left join menu m on m.menu_id = o.menu_id
                group by order_detail_id, o.menu_id, o.order_detail_id, o.quantity, m.priceist
                )
                select
                    c.cust_name,
                    od.req_date_order,
                    tp.total,
                    o.order_detail_id,
                    tp.quantity,
                    code_value(o.order_status, 'eng') as order_status
                from
                    order_detail od
                join "order" o on
                    o.order_detail_id = od.order_detail_id
                join "customer" c on
                    c.customer_id = od.customer_id
                join "transaction" t on
                    t.order_detail_id = od.order_detail_id
                join total_price tp on tp.order_detail_id = od.order_detail_id
                '''
            )
            res = cur.fetchall()

            result = []
            for row in res:
                transformed_row = {"quantity": row["quantity"], "order_detail_id": row["order_detail_id"], "cust_name": row["cust_name"], "req_date_order": row["req_date_order"], "total": row["total"], "order_status": row["order_status"]}
                result.append(transformed_row)
            return jsonify(result)
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)




    