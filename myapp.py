#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import random
import time
import datetime
import click
import logging
# import time
import json
import re

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


@app.route('/code/success/<endpoint>', methods=['GET', 'POST'])
def get_request(endpoint):
    """
    Testing the success endpoints
    """
    app.logger.info(f"printing header of request: {request.headers} ")
    #app.logger.info(f"testing get json { request.get_json() }")
    # message_id = request.get_json()["events"][0]["metadata"]["message_id"]
    # print(f"the second {request.stream.read()}")
    message_id = request.get_json()["events"][0]["metadata"]["message_id"]
    print(f"the payload is: {request.get_json()} ")

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


@app.route('/code/timeout/<endpoint>', methods=['GET', 'POST'])
def get_request_timeout(endpoint):
    """
    Testing delay a
    """
    
    message_id = request.get_json()["events"][0]["metadata"]["message_id"]
    
    number_sec = 30 # Seconds
    
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

    time.sleep(number_sec)

    return f"Endpoint with timeout for endpoint {endpoint}, message id {message_id}"

@app.route('/code/delay/<endpoint>', methods=['GET', 'POST'])
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

@app.route('/code/error/<endpoint>', methods=['GET', 'POST'])
def get_request_error(endpoint):
    """
    Testing error by adding misspelled messageid 500 error for message_id
    """
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
        print(f"There is an exception on error endpoint {endpoint}. The error is...  {e}")
        
    finally:
        db.commit() 
        cur.close()

    return f"Endpoint with simulated error for endpoint {endpoint}, message id {message_id2}"


@app.route('/v1/sendEmails', methods=['GET', 'POST'])
def get_send_email():
    """
    Testing emails notifications submission
    """ 

    number_sec = 0.5 # Seconds
    
    email_payload = request.get_json()
    
    for value in email_payload['emails'][0].values():
        urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', value)
        for url in urls:
            if 'https://console.stage.redhat.com/insights/policies/policy/' in url:
                uuid = url.split('/')[-1]
                
    print(f"The uuid is {uuid}")
        
    time.sleep(number_sec)
    print(f"testing delay for sendemails: {number_sec}") 

    app.logger.info(f"testing sendEmails ")
    print("testing sendEmails")
    
    return f"Mocking testing sending emails"


@app.route('/v2/findUsers', methods=['GET', 'POST'])
def it_user_service():
    """
    Testing emails notifications submission
    """ 

    json_format_it_service =  [
                {
            "id": "df645b37-3e88-4fd9-a0d3-df8cc84c5216",
            "authentications": [
            {
                "principal": "tester",
                "providerName": "tester"
            },
            {
                "principal": "tester",
                "providerName": "tester"
            }
            ],
            "accountRelationships": [
            {
                "accountId": "someId",
                "startDate": "2023-01-01",
                "id":"7b92c949-5033-428c-9fe9-62f11ff0dd4f",
                "isPrimary": True,
                "permissions": [
                {
                    "permissionCode": "admin:org:all",
                    "startDate": "2023-01-01",
                    "id": "f2138fc6-f67f-4954-931e-39e5880882d2"
                }
                ],
                "emails": [
                {
                    "address": "lrios@redhat.com",
                    "isPrimary": True,
                    "id": "5b3b4c54-7bcc-45dc-adff-e99ccbc3ad54",
                    "isConfirmed": True,
                    "status": "active"
                }
                ]
            }
            ],
            "personalInformation": {
            "firstName": "foo",
            "lastNames": "faa",
            "prefix": "he",
            "localeCode": "23",
            "timeZone": "here",
            "rawOffset": "25"
            }
        }
    ]

    number_sec = 1 # delay seconds
    
    time.sleep(number_sec)
    print(f"find user delay: {number_sec}") 
    
    print("Mocking IT service")
    return jsonify(json_format_it_service)


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
