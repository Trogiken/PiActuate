#!/bin/bash
DIR=$(dirname "$0")
cd "$DIR"

# Set environment variables (remove '#' to set a variable, or set them in your environment)
#export SECRET_KEY=""
#export IS_DEVELOPMENT=""
#export ALLOWED_HOSTS=""

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r docs/requirements.txt
sudo apt-get install -y nginx
clear

mkdir -pv config/gunicorn/
touch config/gunicorn/gunicorn.conf.py
echo "
wsgi_app = 'webui.wsgi:application'

loglevel = 'debug'

workers = 2

bind = '0.0.0.0:8000'

reload = True

accesslog = errorlog = '/var/log/gunicorn/dev.log'

capture_output = True

pidfile = '/var/run/gunicorn/dev.pid'

daemon = True" > config/gunicorn/gunicorn.conf.py

sudo mkdir -pv /var/{log,run}/gunicorn/
# DEBUG sudo chown -cR ubuntu:ubuntu /var/{log,run}/gunicorn/

clear

cd webui
gunicorn -c ../config/gunicorn/gunicorn.conf.py


cd webui
# ideally have use nginx as a proxy to filter traffic between the two
# DEBUG gunicorn app.wsgi:application -b 0.0.0.0 -p 8000 --reload & daphne app.asgi:application -b 0.0.0.0 -p 8089 &
