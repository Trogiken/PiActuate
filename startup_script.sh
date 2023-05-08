#!/bin/bash
DIR=$(dirname "$0")
WEBUI="$DIR/webui/"
GUNICORN_CONFIG_DIR="$DIR/config/gunicorn/"
GUNICORN_RUN_DIR="/var/run/gunicorn/"
GUNICORN_LOG_DIR="/var/log/gunicorn/"
cd "$DIR"
# concatenat $DIR and the path to the file you want to run


# Set environment variables (remove '#' to set a variable, or set them in your environment)
#export SECRET_KEY=""
#export IS_DEVELOPMENT=""
#export ALLOWED_HOSTS=""

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r docs/requirements.txt
sudo apt-get install -y nginx
clear

mkdir -pv $GUNICORN_CONFIG_DIR
# make file in $GUNICORN_CONFIG_DIR
touch $GUNICORN_CONFIG_DIR/gunicorn.conf.py
sudo mkdir -pv $GUNICORN_RUN_DIR
mkdir -pv $GUNICORN_LOG_DIR
# DEBUG sudo chown -cR ubuntu:ubuntu /var/{log,run}/gunicorn/

echo "
wsgi_app = 'webui.wsgi:application'

loglevel = 'debug'

workers = 2

bind = '0.0.0.0:8000'

reload = True

accesslog = errorlog = '/var/log/gunicorn/gunicorn.log'

capture_output = True

pidfile = '/var/run/gunicorn/gunicorn.pid'

daemon = True" > $GUNICORN_CONFIG_DIR/gunicorn.conf.py

clear

cd $WEBUI
gunicorn -c ../config/gunicorn/gunicorn.conf.py

# ideally have use nginx as a proxy to filter traffic between the two
# DEBUG gunicorn app.wsgi:application -b 0.0.0.0 -p 8000 --reload & daphne app.asgi:application -b 0.0.0.0 -p 8089 &
