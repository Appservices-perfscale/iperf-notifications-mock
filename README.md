Notifications webhooks mock
===========================

Mock application to act as a target for notifications webhooks.

Usage
-----

TODO

Developing
----------

Start DB:

    podman run -d --name postgresql_database -e POSTGRESQL_USER=user -e POSTGRESQL_PASSWORD=pass -e POSTGRESQL_DATABASE=db -p 5432:5432 quay.io/centos7/postgresql-13-centos7

Setup terminal environment with what you need to run the app:

    python -m venv venv
    source venv/bin/activate
    python -m pip install -U pip
    python -m pip install -r requirements.txt
    export FLASK_APP=myapp.py
    export POSTGRESQL_HOST=localhost
    export POSTGRESQL_PORT=5432
    export POSTGRESQL_USER=user
    export POSTGRESQL_PASSWORD=pass
    export POSTGRESQL_DATABASE=db

And finally this will get you the server running on `http://127.0.0.1:5000/`:

    flask run

Handy command to look into the DB:

    PGPASSWORD=$POSTGRESQL_PASSWORD psql --host=$POSTGRESQL_HOST --username=$POSTGRESQL_USER --port=$POSTGRESQL_PORT $POSTGRESQL_DATABASE


Build image
-----------

Image should be available form quay.io repo:

    podman pull quay.io/rhcloudperfscale/perfscale-demo-app

BUt if you want to build the image locally from git repo:

    sudo podman build -t perfscale-demo-app .

And to run it:

    podman run --rm -ti -p 5000:5000 perfscale-demo-app


Testing
-------

There is a simple Locust script to use:

    flask init-db
    flask test-data
    flask run
    locust --locustfile testing.py --headless --users 50 --spawn-rate 50 -H http://localhost:5000 --run-time 30 --print-stats --only-summary --stop-timeout 10
