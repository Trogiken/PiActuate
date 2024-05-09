#!/bin/bash
# Resources: https://saurabhgujjar.medium.com/django-channels-with-daphne-gunicorn-and-nginx-on-digitalocean-all-in-one-guide-28625eead962

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
WEBUI="$DIR/webui/"
ENV="$DIR/pythonenv/bin"

GUNICORN_NAME="gunicorn.service"
DAPHNE_NAME="daphne.service"
UVICORN_NAME="uvicorn.service"

# create a lock file
touch $DIR/update.lock

source $DIR/webenv
USER=$USER
SERVER_NAME=$SERVER_NAME

#############################################

# Create and activate environment
python -m pip install --upgrade pip
sudo -H pip install virtualenv
virtualenv $DIR/pythonenv
source $ENV/activate

# Install dependencies
pip install -r $DIR/docs/requirements.txt
deactivate
sudo apt-get install -y nginx
sudo systemctl start nginx
sudo apt-get install -y ufw

# Collect static files
source $ENV/activate
python $WEBUI/manage.py collectstatic --noinput
deactivate

# allow ports
sudo ufw allow 5900  # VNC port for debugging, may be removed
sudo ufw allow 80
sudo ufw allow 'Nginx Full'
sudo ufw enable

#############################################

# Configure Uvicorn
sudo touch /etc/systemd/system/$UVICORN_NAME
sudo cat <<EOF > /etc/systemd/system/$UVICORN_NAME
[Unit]
Description=Uvicorn daemon
After=network.target
[Service]
User=$USER
Group=www-data
WorkingDirectory=$DIR/engine
ExecStart=$ENV/uvicorn --host 0.0.0.0 --port 8002 api:app
RestartSec=3s
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF

#############################################

# Configure Gunicorn
sudo touch /etc/systemd/system/$GUNICORN_NAME
sudo cat <<EOF > /etc/systemd/system/$GUNICORN_NAME
[Unit]
Description=gunicorn daemon
After=network.target
[Service]
User=$USER
Group=www-data
WorkingDirectory=$DIR
ExecStart=$ENV/gunicorn --access-logfile - --workers 1 --pythonpath $WEBUI --bind unix:$DIR.sock webui.wsgi:application
RestartSec=3s
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF

#############################################

# Configure Daphne
sudo touch /etc/systemd/system/$DAPHNE_NAME
sudo cat <<EOF > /etc/systemd/system/$DAPHNE_NAME
[Unit]
Description=WebSocket Daphne Service
After=network.target
[Service]
Type=simple
User=$USER
WorkingDirectory=$WEBUI
ExecStart=$ENV/python $ENV/daphne -b 0.0.0.0 -p 8001 webui.asgi:application
RestartSec=3s
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF

#############################################

# Configure Nginx
sudo touch /etc/nginx/sites-available/webui
sudo cat <<EOF > /etc/nginx/sites-available/webui
upstream channels-backend {
    server localhost:8001;
}
server {
    listen 80;
    server_name $SERVER_NAME;

    location /static/ {
        alias $WEBUI/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$DIR.sock;
    }

    location /ws/ {
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host \$server_name;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/webui /etc/nginx/sites-enabled

#############################################

# Start services
sudo systemctl daemon-reload

sudo systemctl restart nginx.service
sudo systemctl enable uvicorn.service
sudo systemctl enable gunicorn.service
sudo systemctl enable daphne.service
sudo systemctl enable nginx.service

# Delete lock file
rm $DIR/update.lock

# Restart device
sudo reboot