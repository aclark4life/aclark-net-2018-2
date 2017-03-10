ACLARK.NET, LLC — DB
====================

Client & Contractor Database Application
----------------------------------------

Based on data exported from `Harvest <https://www.getharvest.com/>`_

Heroku
~~~~~~

::

    git remote add heroku git@heroku.com:aclarknet-database.git
    git remote add heroku git@heroku.com:aclarknet-database2.git

Social
~~~~~~

- http://artandlogic.com/2014/04/tutorial-adding-facebooktwittergoogle-authentication-to-a-django-application/
- https://console.developers.google.com/


Models
~~~~~~

.. image:: graph_models.png


AWS
~~~

::

    Ubuntu 16.04.1 LTS

::

    sudo apt-get install aptitude awscli graphviz graphviz-dev jq libpq-dev libxml2 libxml2-dev libxslt-dev make nginx postgresql python python3 python3-pip python3-virtualenv python-dev

systemd
~~~~~~~

gunicorn.service
++++++++++++++++

::

    [Unit]
    Description=gunicorn daemon
    Requires=gunicorn.socket
    After=network.target

    [Service]
    # env | sort > /srv/aclarknet-database/env
    EnvironmentFile=/srv/aclarknet-database/env

    PIDFile=/run/gunicorn/pid
    User=ubuntu
    Group=ubuntu
    RuntimeDirectory=gunicorn
    WorkingDirectory=/srv/aclarknet-database
    ExecStart=/srv/aclarknet-database/bin/gunicorn -c /srv/aclarknet-database/logging.conf --pid /run/gunicorn/pid --bind unix:/run/gunicorn/socket aclarknet.wsgi
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/bin/kill -s TERM $MAINPID
    PrivateTmp=true

    [Install]
    WantedBy=multi-user.target

gunicorn.socket
+++++++++++++++

::

    [Unit]
    Description=gunicorn socket

    [Socket]
    ListenStream=/run/gunicorn/socket

    [Install]
    WantedBy=sockets.target

NGINX
~~~~~

/etc/nginx/sites-enabled/default 
++++++++++++++++++++++++++++++++

::

    server {
        listen 443 ssl default_server;
        listen [::]:443 ssl default_server;

        ssl    on;
        ssl_certificate    /etc/letsencrypt/live/db.aclark.net/fullchain.pem;
        ssl_certificate_key    /etc/letsencrypt/live/db.aclark.net/privkey.pem;

        root /var/www/html;

        index index.html index.htm index.nginx-debian.html;

        server_name _;

        location / {
            proxy_pass http://unix:/run/gunicorn/socket;
            proxy_set_header Host      $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    server {
        listen 80;
        listen [::]:80;

        server_name _;

        root /var/www/example.com;
        index index.html;

        location / {
            try_files $uri $uri/ =404;
        }

        return 301 https://$host$request_uri;
    }
