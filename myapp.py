#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import random
import time
import datetime
import click
import logging
# import time

from flask import Flask, current_app, g, request, jsonify, abort


import psycopg2.pool



app = Flask(__name__)

app.config['DB_POOL_COUNT_MIN'] = os.environ.get('DB_POOL_COUNT_MIN', 2)
app.config['DB_POOL_COUNT_MAX'] = os.environ.get('DB_POOL_COUNT_MAX', 10)
app.config['DB_POOL_GETCONN_ATTEMPTS'] = os.environ.get('DB_POOL_GETCONN_ATTEMPTS', 10)
app.config['DATABASE'] = f"postgresql://{ os.environ['POSTGRESQL_USER'] }:{ os.environ['POSTGRESQL_PASSWORD'] }@{ os.environ['POSTGRESQL_HOST'] }:{ os.environ['POSTGRESQL_PORT'] }/{ os.environ['POSTGRESQL_DATABASE'] }"
app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler('app.log')  # Log to a file
app.logger.addHandler(handler)


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


@app.route('/code/success/<endpoint>', methods=['POST'])
def get_request(endpoint):
    """
    Testing the success endpoints
    """
    app.logger.info(f"testing get json { request.get_json() }")
    message_id = request.get_json()["events"][0]["metadata"]["message_id"]

    print(f"testing {message_id} ")

    app.logger.info(f"testing endpoint log ")
    
    try:
        db = get_db()
        cur = db.cursor()
        sql = """
            INSERT INTO items_notifications(message_id, dispatched_at, dispatched_count) VALUES (%s, NOW(), 1)
                ON CONFLICT (message_id) DO UPDATE
                SET dispatched_at = EXCLUDED.dispatched_at, dispatched_count = items_notifications.dispatched_count + 1
        """
        app.logger.info(f"the sql is {sql} ")
        cur.execute(sql, (message_id,))
        
    except Exception as e:
        return f"There is an exception on the success endpoint {endpoint}. The exception is {e}"
        
    finally:
        db.commit() 
        cur.close()

    return f"Updated data for Request with endpoint: {endpoint} for 200 endpoint"


@app.route('/code/timeout/<endpoint>', methods=['GET'])
def get_request_timeout(endpoint):
    """
    Testing delay a
    """
    
    message_id = request.get_json()["events"][0]["metadata"]["message_id"]
    
    number_sec = 30 # Seconds
    
    time.sleep(number_sec)
    print(f"testing timeout with {number_sec}") 
    
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
        print(f"There is an exception on the timeout endpoint {endpoint}. The exception is {e}")
        
    finally:
        db.commit() 
        cur.close()

    return f"Endpoint with timeout for endpoint {endpoint}, message id {message_id}"

@app.route('/code/delay/<endpoint>', methods=['GET'])
def get_request_delay(endpoint):
    """
    Testing delay a
    """
    message_id = request.get_json()["events"][0]["metadata"]["message_id"]
    
    number_sec = 5 # Seconds as requested
    
    time.sleep(number_sec)
    print(f"testing delay with {number_sec}") 
    
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
        print(f"There is an exception on the delay endpoint {endpoint}. The exception is {e}")
        
    finally:
        db.commit() 
        cur.close()

    return f"Endpoint with simulated delay for endpoint {endpoint}, message id {message_id}"

@app.route('/code/error/<endpoint>', methods=['GET'])
def get_request_error(endpoint):
    """
    Testing error by adding misspelled messageid 500 error for message_id2
    """
    message_id = request.get_json()["events"][0]["metadata"]["message_id2"]
    
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
        print(f"There is an exception on error endpoint {endpoint}. The error is...  {e}")
        
    finally:
        db.commit() 
        cur.close()

    return f"Endpoint with simulated error for endpoint {endpoint}, message id {message_id}"




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
