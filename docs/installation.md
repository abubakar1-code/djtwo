# Installation

## Local Development Setup

1. Make virtual environment.
1. Install requirements file.

### Create your own settings file

Copy from settings/local.py and create dev-yourname.py. Change manage.py to use your settings file.

### Windows Setup

Install libmagic with cygwin and move the following files to system 32:

* cygmagic-1.dll (rename as magic1.dll)
* cygwin.dll
* cygz.dll

### PostgreSQL Setup

Using SQL Shell:

```sh
postgres# CREATE USER comply-dev PASSWORD 'password';
postgres# CREATE DATABASE comply-dev OWNER comply-dev;
```

### RabbitMQ and Celery

#### RabbitMQ

1. [Install Erlang](http://www.erlang.org/downloads)
1. [Install RabbitMQ](https://www.rabbitmq.com/install-windows.html)
1. Install Pika for python.

## Linux Sandbox Development Setup With Apache

### Installing Apache

First we need to get Apache, mod-wsgi, and python's package manager, PIP

```sh
sudo apt-get install python-pip apache2 libapache2-mod-wsgi
```
### Create Virtual Environment

First install virtualenv
```sh
$ sudo pip install virtualenv
```

Now lets start creating the project. Create a directory where you want to keep it.

```sh
$ mkdir ~/comply
$ cd ~/comply
```

Create the virtual environment

```sh
$ virtualenv complyenv
```
This creates a directory with a local version of Python and PIP. We can use this to create and install an isolated environment.

Next Activate the Virtual Environment

```sh
$ source complyenv/bin/activate
```

### Get Source From our BitBucket Server

Install git if it's not already

```sh
$ sudo apt-get install git
```

clone the repo

```sh
$ git clone http://{your_username}@jira.prescient.com:7990/scm/pc/prescientcomply.git
```

### Install Requirements

Now that we have a virtual environment and the source code lets install the requirements.

First ensure you are working on the virtual environment. You should see (complyenv) before your username in the terminal. If not,

```sh
$ source complyenv/bin/activate
```

Then install all of the requirements.

```sh
$ pip install -r prescientcomply/requirements/base.txt
```

### Configure Apache

Edit virtual host file:

```sh
$ sudo nano /etc/apache2/sites-available/000-default.conf
```

 "..path to" should be replaced by the full path to your project.

```xml
<VirtualHost *:80>
	...
	Alias /static ..path to/comply/prescientcomply/spotlit_due_diligence/static
    <Directory ..path to/comply/prescientcomply/spotlit_due_diligence/static>
                Require all granted
    </Directory>

    <Directory ..path to/comply/prescientcomply/spotlit_due_diligence/spotlit_due_diligence>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
        WSGIDaemonProcess spotlit_due_diligence python-path=..path to/comply/prescientcomply/spotlit_due_diligence:..path to/comply/complyenv/lib/python2.7/site-packages
        WSGIProcessGroup spotlit_due_diligence
        WSGIScriptAlias / ..path to/comply/prescientcomply/spotlit_due_diligence/spotlit_due_diligence/wsgi.py
</VirtualHost>
 ```

Next we need to grant Apache permission to access the project.

```
$ sudo chown :www-data ..path to/comply
```

Also to the /var/www folder

```
$ sudo chown :www-data /var/www
```

### Set up Environment Vars
There are several variables that should not be stored in the django settings file due to there sensitive nature, so they are stored in apache as environment variables.

```
$ sudo nano /etc/apache2/envvars
```

And add the necessary environment variables to the file.

```sh
export AWS_ACCESS_KEY_ID={get from http://aws.amazon.com/}
export AWS_SECRET_ACCESS_KEY={get from http://aws.amazon.com/}
export AWS_BUCKET={get from http://aws.amazon.com/}
export DJANGO_S3=1
  
export EMAIL_HOST={if not provided defaults to smtp.office365.com}
export EMAIL_HOST_PASSWORD={password}
export EMAIL_HOST_USER={if not provided defaults to admin@spotlit.com}
export EMAIL_PORT={if not provided defaults to 587}

export DATABASE_URL={postgres://USER:PASSWORD@HOST:PORT/NAME}
  
export SECRET_KEY={set this to something unique}
```    

### Restart Apache

```sh
sudo service apache2 restart
```

## Heroku

Install [Heroku Toolbelt](https://toolbelt.heroku.com/).
