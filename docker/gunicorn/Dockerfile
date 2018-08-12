FROM debian:stretch-slim

RUN apt-get update -y
RUN apt-get install -y python3 python3-dev python3-pip git expect
RUN git clone https://github.com/h3nr1-g/Smart-Pump-Backend.git /opt/spb
RUN rm -rf /opt/spb/docker

COPY productive.py /opt/spb/spb/spb/settings/productive.py
COPY wsgi.py /opt/spb/spb/spb/wsgi.py
COPY changepassword.sh /opt/spb/changepassword.sh

WORKDIR /opt/spb
RUN pip3 install -r requirements/runtime.txt
RUN pip3 install gunicorn
WORKDIR /opt/spb/spb
RUN python3 manage.py makemigrations --settings=spb.settings.productive api monitor
RUN python3 manage.py migrate --settings=spb.settings.productive
RUN python3 manage.py createsuperuser --username admin --email=admin@spb.net --noinput --settings=spb.settings.dev
RUN ["/opt/spb/changepassword.sh", "admin", "admin123456789"]

EXPOSE 8000

CMD python3 manage.py collectstatic --noinput --settings=spb.settings.productive && gunicorn --access-logfile - --workers 3 --bind 0.0.0.0:8000 spb.wsgi
