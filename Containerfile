FROM registry.access.redhat.com/ubi9/ubi

MAINTAINER Jan Hutar <jhutar@redhat.com>

WORKDIR /usr/src/app

ENV FLASK_APP myapp.py

RUN INSTALL_PKGS="python3 python3-pip" \
  && dnf -y install $INSTALL_PKGS \
  && dnf clean all

COPY requirements.txt .

RUN chmod -R 777 /usr/src/app/

RUN python3 -m pip install --no-cache-dir -U pip \
    && python3 -m pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY . /usr/src/app

USER 1001

CMD gunicorn --worker-class sync --workers 5 --threads 6 --access-logfile - --error-logfile - --bind 0.0.0.0:5000 myapp:app
