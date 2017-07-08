ACLARK.NET, LLC — DB
====================

Client & Contractor Database Application
----------------------------------------

.. image:: screenshot.png

Based on data exported from `Harvest <https://www.getharvest.com/>`_

Models
~~~~~~

.. image:: graph_models.png


Social
~~~~~~

- http://artandlogic.com/2014/04/tutorial-adding-facebooktwittergoogle-authentication-to-a-django-application/
- https://console.developers.google.com/

AWS
~~~

::

    Ubuntu 16.04.1 LTS

::

    sudo apt-get update
    sudo apt-get install aptitude awscli graphviz graphviz-dev jq letsencrypt \
        libpq-dev libxml2 libxml2-dev libxslt-dev make nginx pkg-config       \
        postgresql python python-pip python3 python3-pip python-virtualenv    \
        python3-virtualenv python-dev -y
    sudo aptitude upgrade -y

systemd
~~~~~~~

::

    sudo systemctl enable /srv/aclarknet-database/systemd/db.service 
    sudo systemctl enable /srv/aclarknet-database/systemd/db.socket
    sudo systemctl start db.service 
    sudo systemctl start db.socket

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

Letsencrypt
~~~~~~~~~~~

::

    $ sudo letsencrypt certonly

    …

    IMPORTANT NOTES:
     - Congratulations! Your certificate and chain have been saved at
       /etc/letsencrypt/live/db.aclark.net/fullchain.pem. Your cert will
       expire on 2017-06-08. To obtain a new version of the certificate in
       the future, simply run Let's Encrypt again.
     - If you like Let's Encrypt, please consider supporting our work by:

       Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
       Donating to EFF:                    https://eff.org/donate-le

Django
~~~~~~

If memory < 1G, increase swap before installing. [1]_

::

    sudo dd if=/dev/zero of=/swapfile bs=1024 count=524288
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile

Then:

::

    git clone git@github.com:ACLARKNET/aclarknet-database.git
    sudo mv aclarknet-database /srv
    cd /srv/aclarknet-database
    virtualenv --python=python3 .
    bin/pip install -r requirements.txt

.. [1] http://stackoverflow.com/a/26762938/185820

PostGIS
~~~~~~~

(Via http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.html#Appendix.PostgreSQL.CommonDBATasks.PostGIS)

::

    create extension postgis;
    create extension fuzzystrmatch;
    create extension postgis_tiger_geocoder;
    create extension postgis_topology;

::

    postgres=> \dn
         List of schemas
         Name     |   Owner
    --------------+-----------
     public       | myawsuser
     tiger        | rdsadmin
     tiger_data   | rdsadmin
     topology     | rdsadmin
    (4 rows) 

::

    alter schema tiger owner to rds_superuser;
    alter schema tiger_data owner to rds_superuser;
    alter schema topology owner to rds_superuser;

::

    postgres=> \dn
           List of schemas
         Name     |     Owner
    --------------+---------------
     public       | myawsuser
     tiger        | rds_superuser
    tiger_data    | rds_superuser
     topology     | rds_superuser
    (4 rows) 

::

    CREATE FUNCTION exec(text) returns text language plpgsql volatile AS $f$ BEGIN EXECUTE $1; RETURN $1; END; $f$;

::

    SELECT exec('ALTER TABLE ' || quote_ident(s.nspname) || '.' || quote_ident(s.relname) || ' OWNER TO rds_superuser;')
      FROM (
        SELECT nspname, relname
        FROM pg_class c JOIN pg_namespace n ON (c.relnamespace = n.oid) 
        WHERE nspname in ('tiger','topology') AND
        relkind IN ('r','S','v') ORDER BY relkind = 'S')
    s;
      
::

    SET search_path=public,tiger;         
      
::

    select na.address, na.streetname, na.streettypeabbrev, na.zip
    from normalize_address('1 Devonshire Place, Boston, MA 02109') as na;

::

    address | streetname | streettypeabbrev |  zip
    ---------+------------+------------------+-------
           1 | Devonshire | Pl               | 02109
    (1 row) 

::

    select topology.createtopology('my_new_topo',26986,0.5);

::

    createtopology
    ----------------
                  1
    (1 row) 
