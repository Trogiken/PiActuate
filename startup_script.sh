#!/bin/bash
DIR=$(dirname "$0")
cd "$DIR"

export SECRET_KEY=""
export IS_DEVELOPMENT=""
export ALLOWED_HOSTS=""

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r docs/requirements.txt
clear

python webui/manage.py runserver 0.0.0.0:8000  # DEBUG proper method?