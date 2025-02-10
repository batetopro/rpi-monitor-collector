# rpi-monitor-collector
Monitoring collector for the rpi-monitor


## Installation
```
# Install pip before continuing
sudo apt-get install python3-pip

# Install virtualenv
sudo apt-get install python3-virtualenv

# Create a user for the collector
sudo adduser --gecos 'Raspberry collector' rpi-collector

# Lock the user
sudo usermod -L rpi-collector

# Login as the rpi-collector user and go to its home
sudo su rpi-collector
cd ~

# Checkout the repo and enter it
git clone https://github.com/batetopro/rpi-monitor-collector.git
cd rpi-monitor-collector

# Create a virtual environment
python3 -m virtualenv venv

# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
Crate .env file and configure it.

```
cd monitoring/monitoring
cp .env.template .env
nano .env
```

The supported keys are:
* `DEBUG` - Whether to run Django in debug mode. 0 for False, 1 for True.
* `HOSTNAME` - Address, from which the collector will be accessed
* `SECRET_KEY` - Secret key, which is used by Django.
* `STATIC_ROOT` - Where to keep the served static files.
* `DB_BACKEND` - Which engine and configuration options tp use for storing the information. Suppored - `sqlite3`, `mysql`.
* `DB_NAME` - path to the sqlite database.

If you want to use mySQL or mariaDB for the database connection, then copy `my.ini.template` as `my.ini`.
Fill the connection options, see the MySQL documentation for `mysql_options()`.


Collect the static files
```
cd ..
python manage.py collectstatic
```

Run database migrations
```
python manage.py migrate
```

Create super user
```
python manage.py createsuperuser
```

Logout the rpi-collector user
```
exit
```

Configure the systemctl service.
```
sudo nano /etc/systemd/system/rpi-management.service
```
Enter the following:
```
[Unit]
Description=RPi collector management (Monitor your raspberries)
After=syslog.target
After=network.target

[Service]
RestartSec=2s
Type=simple
User=rpi-collector
Group=rpi-collector
WorkingDirectory=/home/rpi-collector/rpi-monitor-collector/monitoring
ExecStart=/home/rpi-collector/rpi-monitor-collector/venv/bin/gunicorn monitoring.wsgi -b 127.0.0.1:5001
Restart=always
Environment=USER=rpi-collector
HOME=/home/rpi-collector

[Install]
WantedBy=multi-user.target
```

Activate the managment service
```
sudo systemctl enable rpi-management.service
sudo systemctl start rpi-management.service
```

Install Nginx
```
sudo apt-get install nginx
```

Create Nginx configration file `/etc/nginx/conf.d/rpi-collector.conf`

```
server {
    listen 80;

    server_name rpi-collector.localhost;    # Change localhost to the real name of the server

    location /static/ {
        root $STATIC_ROOT;  # Set to the parent directory of STATIC_ROOT from .env file
    }
    location / {
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $remote_addr;
        proxy_set_header        X-Forwarded-Proto $scheme;
        proxy_set_header        Host $host;
        proxy_intercept_errors  on;
        proxy_pass http://127.0.0.1:5001/;  # Change 5001 to the port set in systemctl config
   }
}
```

Reload Nginx configuration
```
sudo systemctl reload nginx
```

Login as rpi-collector and generate a SSH pair.
Do not provide passpahrase!
```
sudo su rpi-collector

ssh-keygen -t rsa -b 4096 -f /home/rpi-collector/.ssh/id_rsa
```
Get the contents of the public key
```
cat /home/rpi-collector/.ssh/id_rsa.pub
```
Logout from rpi-collector
```
exit
```

In the administration panel go to:
http://rpi-collector.localhost/core/sshkeymodel/add/

And create an entry for the SSH key:
Name - rpi-collector
Identity file - /home/rpi-collector/.ssh/id_rsa
Public key - the contents of the public key (saved on /home/rpi-collector/.ssh/id_rsa.pub)
Save.


Configure the systemctl service for the collector.
```
sudo nano /etc/systemd/system/rpi-collector.service
```
Enter the following:
```
[Unit]
Description=RPi collector (Monitor your raspberries)
After=syslog.target
After=network.target

[Service]
RestartSec=2s
Type=simple
User=rpi-collector
Group=rpi-collector
WorkingDirectory=/home/rpi-collector/rpi-monitor-collector/monitoring
ExecStart=/home/rpi-collector/rpi-monitor-collector/venv/bin/python manage.py collect
Restart=always
Environment=USER=rpi-collector
HOME=/home/rpi-collector

[Install]
WantedBy=multi-user.target
```

Activate the collector service
```
sudo systemctl enable rpi-collector.service
sudo systemctl start rpi-collector.service
```

