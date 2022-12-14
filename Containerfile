FROM registry.access.redhat.com/ubi8/ubi

MAINTAINER Jan Hutar <jhutar@redhat.com>

WORKDIR /usr/src/app

ENV FLASK_APP myapp.py

RUN INSTALL_PKGS="python3" \
  && yum -y install $INSTALL_PKGS \
  && yum clean all

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir -U pip \
    && python3 -m pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY . /usr/src/app

USER 1001

CMD gunicorn --access-logfile - --error-logfile - --bind 0.0.0.0:5000 myapp:app
###CMD gunicorn --worker-class gthread --workers 3 --threads 3 --access-logfile - --error-logfile - --bind 0.0.0.0:5000 myapp:app
