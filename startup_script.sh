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

cd webui
# ideally have use nginx as a proxy to filter traffic between the two
gunicorn app.wsgi:application -b 0.0.0.0 -p 8000 --reload & daphne app.asgi:application -b 0.0.0.0 -p 8089 &
