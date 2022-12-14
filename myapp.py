#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import random

import click

from flask import Flask, current_app, g

import psycopg2


app = Flask(__name__)

app.config['DATABASE'] = f"postgresql://{ os.environ['POSTGRESQL_USER'] }:{ os.environ['POSTGRESQL_PASSWORD'] }@{ os.environ['POSTGRESQL_HOST'] }:{ os.environ['POSTGRESQL_PORT'] }/{ os.environ['POSTGRESQL_DATABASE'] }"


##########
# DB setup
##########

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(current_app.config['DATABASE'])

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


app.teardown_appcontext(close_db)


##########
# Routes
##########

@app.route('/request/<string:request_id>', methods=['GET'])
def get_request(request_id):
    """Test."""
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT created_at FROM requests WHERE request_id = %s", (request_id,))
    created_at = cur.fetchone()[0]
    return f"Request {request_id} crated at {created_at}"


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
                dispatched_at TIMESTAMP WITH TIME ZONE NULL);
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

    cur.execute("INSERT INTO requests (request_id, created_at) VALUES ('abc', NOW())")

    db.commit()
    cur.close()

    click.echo('Added a record to the database.')


app.cli.add_command(init_db_command)
app.cli.add_command(test_data_command)
