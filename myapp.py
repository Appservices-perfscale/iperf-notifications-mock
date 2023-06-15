#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import random
import time
import datetime
import click
# import time

from flask import Flask, current_app, g, request, jsonify, abort

import psycopg2.pool



app = Flask(__name__)

app.config['DB_POOL_COUNT_MIN'] = os.environ.get('DB_POOL_COUNT_MIN', 2)
app.config['DB_POOL_COUNT_MAX'] = os.environ.get('DB_POOL_COUNT_MAX', 10)
app.config['DB_POOL_GETCONN_ATTEMPTS'] = os.environ.get('DB_POOL_GETCONN_ATTEMPTS', 10)
app.config['DATABASE'] = f"postgresql://{ os.environ['POSTGRESQL_USER'] }:{ os.environ['POSTGRESQL_PASSWORD'] }@{ os.environ['POSTGRESQL_HOST'] }:{ os.environ['POSTGRESQL_PORT'] }/{ os.environ['POSTGRESQL_DATABASE'] }"


##########
# DB setup
##########

def get_db():
    if 'db' not in g:
        for attempt in range(current_app.config["DB_POOL_GETCONN_ATTEMPTS"]):
            try:
                g.db = current_app.config["db_pool"].getconn()
            except:
                time.sleep(.1)
            else:
                break
        else:
            raise Exception("Failed to get DB connection")

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        current_app.config["db_pool"].putconn(db)


app.teardown_appcontext(close_db)
app.config["db_pool"] = psycopg2.pool.ThreadedConnectionPool(
    app.config['DB_POOL_COUNT_MIN'],
    app.config['DB_POOL_COUNT_MAX'],
    app.config['DATABASE'],
)
app.logger.info(f"Initialized DB pool (min {app.config['DB_POOL_COUNT_MIN']}, max {app.config['DB_POOL_COUNT_MIN']})")


##########
# Routes
##########

@app.route('/code/200', methods=['GET'])
def get_request():
    message_id = request.get_json()["events"][0]["metadata"]["message_id"]
    
    try:
        db = get_db()
        cur = db.cursor()
        sql = """
            INSERT INTO items_notifications(message_id, dispatched_at, dispatched_count) VALUES (%s, NOW(), 1)
                ON CONFLICT (message_id) DO UPDATE
                SET dispatched_at = EXCLUDED.dispatched_at, dispatched_count = items_notifications.dispatched_count + 1
        """
        print(sql)
        cur.execute(sql, (message_id,))
        
    except Exception as e:
        print(f"There is an exception {e}")
        
    finally:
        db.commit() 
        cur.close()
       
    print

    return f"Updated data for Request with message id {message_id}"

@app.route('/code/500', methods=['GET'])
def get_request_500():
#     We are testing my updating invalid column. Should return 500 error
    message_id = request.get_json()["events"][0]["metadata"]["message_id"]
    
    try:
        db = get_db()
        cur = db.cursor()
        sql = """
            INSERT INTO items_notifications(message_id, dispatched_at, dispatched_cou) VALUES (%s, NOW(), 1)
                ON CONFLICT (message_id) DO UPDATE
                SET dispatched_at = EXCLUDED.dispatched_at, dispatched_count = items_notifications.dispatched_count + 1
        """
        print(sql)
        cur.execute(sql, (message_id,))
        
    except Exception as e:
        abort(500)
        
    finally:
        db.commit() 
        cur.close()
       
    print

    return f"Updated data for Request with message id {message_id}"


##########
# CLI
##########

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    db = get_db()
    cur = db.cursor()

    cur.execute(
        """
        DROP TABLE IF EXISTS requests;
        CREATE TABLE requests (
                request_id VARCHAR PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE NULL,
                dispatched_at TIMESTAMP WITH TIME ZONE NULL,
                dispatched_count INTEGER DEFAULT 0);
        CREATE INDEX request_id_idx
                ON requests (request_id);
        """
    )

    db.commit()
    cur.close()

    click.echo('Initialized the database.')


@click.command('test-data')
def test_data_command():
    """Add some data to play with"""
    db = get_db()
    cur = db.cursor()

#     cur.execute("INSERT INTO requests (request_id, created_at) 
#                 ('abc', NOW())")

#     db.commit()
#     cur.close()

#     click.echo('Added a record to the database.')


app.cli.add_command(init_db_command)
app.cli.add_command(test_data_command)
