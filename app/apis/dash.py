from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, Blueprint
import psycopg2 
from flask_restx import Namespace, Resource, reqparse
from .db import pool

dash = Namespace("dashboard", description= "Dashboard's APIS Namespace")

@dash.route("/last-order")
class LastOrder(Resource):
    def get(self):
        conn = pool.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''
                select
                    c.cust_name,
                    code_value(t.transaction_type, 'eng') as transaction_type,
                    code_value(t.transaction_status, 'eng') as transaction_type,
                    od.req_date_order,
                    od.address_order,
                    array_agg(m.menu_name) as menus  
                from
                    "order" o
                join order_detail od on
                    od.order_id = o.order_id
                join customer c on c.customer_id = od.customer_id 
                join "transaction" t on od.transaction_id = t.transaction_id 
                join menu m on m.menu_id  = o.menu_id 
                group by c.cust_name, t.transaction_type, t.transaction_status, od.order_detail_id  
                order by
                    od.created_at desc
                ''') 
            res = cur.fetchall()
            cur.close()
            return jsonify(res)
        except Exception as e:
                return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)
    
@dash.route("/top-selling")
class LastOrder(Resource):
    def get(self):
        conn = pool.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''
                select
                    m.menu_name,
                    count("order".menu_id) as order_count
                from
                    "order"
                join menu m on
                    m.menu_id = "order".menu_id
                group by
                    "order".menu_id,
                    m.menu_name
                order by
                    order_count desc
                ''') 
            res = cur.fetchall()
            cur.close()
            return jsonify(res)
        except Exception as e:
                return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)
    
@dash.route("/sales-summary")
class LastOrder(Resource):
    def get(self):
        conn = pool.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''
                with menu_pricelist as (
                select
                    m.menu_id,
                    menu_name,
                    cast(m.pricelist as integer) as pricelist
                from
                    menu m
                ),
                order_summary as (
                select
                    mp.menu_name,   
                    count(o.menu_id) as order_menu,
                    mp.pricelist,
                    count(o.menu_id) * mp.pricelist as total_price,
                    AVG(count(o.menu_id) * mp.pricelist) OVER () AS average_total_price
                from
                    "order" o
                join menu_pricelist mp on
                    mp.menu_id = o.menu_id
                group by
                    mp.menu_name,
                    mp.pricelist,
                    mp.menu_id 
                )
                select
                    sum(os.total_price) as total,
                    sum(os.order_menu) as order,
                    os.average_total_price
                from
                    order_summary os
                group by
                    average_total_price
                ''') 
            res = cur.fetchall()
            cur.close()
            return jsonify(res)
        except Exception as e:
                return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)
    
@dash.route("/bar-chart")
class BarChart(Resource):
    def get(self):
        conn = pool.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''
               select
                    array_agg(count_) as count_array,
                    array_agg(menu_name) as menu_name_array
                from
                    (
                        select
                            count(quantity) as count_,
                            o.menu_id,
                            m.menu_name
                        from
                            "order" o
                        join menu m on
                            m.menu_id = o.menu_id
                        group by
                            o.menu_id,
                            m.menu_name
                    ) as sub
                ''') 
            res = cur.fetchall()
            cur.close()
            return jsonify(res)
        except Exception as e:
                return {"error": str(e)}, 500
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                pool.return_connection(conn)
    