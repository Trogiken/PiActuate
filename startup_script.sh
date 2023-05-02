#!/bin/bash
DIR=$(dirname "$0")
cd "$DIR"

python webui/manage.py runserver 0.0.0.0:8000