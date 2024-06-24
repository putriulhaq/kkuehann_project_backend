from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, Blueprint
import psycopg2 
from flask_restx import Namespace, Resource, reqparse
import argparse
from .db import pool
from psycopg2.extras import DictCursor
from datetime import datetime


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
        cur = conn.cursor(cursor_factory=DictCursor)
        try:
            cur.execute(
                '''
                    select
                        distinct on
                        (order_detail_id)
                        od.*,
                        c.*,
                        code_value(od.order_status, 'eng') as order_status_name
                    from
                        "order" o
                    join "order_detail" od on
                        o.order_detail_id = od.order_detail_id
                    join transaction t on
                        t.order_detail_id = od.order_detail_id
                        join customer c on c.customer_id = od.customer_id
                ''') 
            rows = cur.fetchall()
            res = [dict(row) for row in rows]
            return jsonify(res)
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)

    # orderArgs.add_argument('rate', type=int, help='Rate cannot be converted')
    orderArgs.add_argument('cust_name', type=str)
    orderArgs.add_argument('address', type=str)
    orderArgs.add_argument('no_tlp', type=str)
    orderArgs.add_argument('order_to', type=str)
    orderArgs.add_argument('description', type=str) 
    orderArgs.add_argument('orderItems', type=list) 
    orderArgs.add_argument('req_date_order', type=str, location='json') 
    
    @order.expect(orderArgs)
    def post(self):
        conn = pool.get_connection()
        cur = conn.cursor()
        data = request.json
        args = orderArgs.parse_args()
        order_items = data.get('orderItems', [])
        order_data = {
            'cust_name': args['cust_name'],
            'address': args['address'],
            'address_order': args['address'],  # Set address_order sama dengan address
            'no_tlp': args['no_tlp'],
            'order_to': args['order_to'],
            'description': args['description'],
            'req_date_order': args['req_date_order'],
            'orderItems': order_items
        }
        print(order_data)
        
        try:
            # Insert customer and return customer_id
            cur.execute(
                """
                INSERT INTO public."customer" (cust_name, address, no_tlp)
                VALUES (%s, %s, %s)
                RETURNING customer_id
                """,
                (
                    order_data['cust_name'],
                    order_data['address'],
                    order_data['no_tlp']
                )
            )
            customer_id = cur.fetchone()[0]
            
            # Insert order detail and return order_detail_id
            cur.execute(
                """
                INSERT INTO public.order_detail (customer_id, upd_date_order, req_date_order, address_order, created_at)
                VALUES (%s, NOW(), %s, %s, NOW())
                RETURNING order_detail_id
                """,
                (
                    customer_id,
                    order_data['req_date_order'],
                    order_data['address_order']
                )
            )
            order_detail_id = cur.fetchone()[0]
            
            # Loop through orderItems and insert each one into the order table
            for item in order_items:
                cur.execute(
                    """
                    INSERT INTO public."order" (order_detail_id, menu_id, quantity, order_status)
                    VALUES (%s, %s, %s, '002001')
                    """,
                    (
                        order_detail_id,
                        item['menu_id'],
                        item['quantity']
                    )
                )
            
            # Insert into the transaction table
            cur.execute(
                """
                INSERT INTO public."transaction" (
                    transaction_id, transaction_type, transaction_status, transaction_to, order_detail_id
                )
                VALUES (
                    NEXTVAL('transaction_id_seq'), '002001', '003001', '004001', %s
                )
                """,
                (order_detail_id,)
            )
            
            conn.commit()
            return jsonify({"status": "success"})
        
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
        
        finally:
            pool.return_connection(conn)


@order.route('/latest-order')
class LatestOrder(Resource):
    def get(self):
        if pool:
            print('succes')
            print('yaa')
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
                select distinct on (od.order_detail_id)
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




    