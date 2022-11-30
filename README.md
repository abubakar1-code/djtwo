# Overview
This repository contains files for the Comply portal. It's currently running with outdated versions of python and django and should be upgraded to the latest versions.

# Setup
## 1. Prepare the app
Clone the application so that you have a local version of the code\

## 2. Create new virtual environment
If you're running python 3, then you'll need to create a virtualenv with version 2 of python\
First you need to find the path to your python2\
`which python2`

Then use that path in the following command to create a new virtualenv\
`virtualenv -p /usr/bin/python2 venv2`

Once the update is upgrade to python3, the following command will work:\
`python -m venv /path/to/new/virtual/environment`

## 3. Activate the virtual environment
`source /path/to/new/virtual/environment/bin/activate`

## 4. PostgreSQL Setup
Using SQL Shell:\
`postgres# CREATE USER username PASSWORD 'password';`\
`postgres# CREATE DATABASE databasename OWNER username;`

## 5. Create your own settings file
Copy from settings/local.py and create dev-yourname.py (with your database information from step 4). Change spotlit_due_diligence/manage.py to use your settings file.

## 6. Make sure you have Pip installed
`pip -V`

## 7. Remove psycopg2==2.8.5 from base.txt
I had to remove psycopg2==2.8.5 from base and install the binary (see step 9)

## 8. Install requirements.txt
Make sure you've checked out branch `develop` and then use pip to install the requirements\
When I install using the master branch (which has updated requirements file) all sorts of things break..\
`pip install -r requirements.txt`

## 9. Install psycopg2 from the binary
I don't know why, but psycopg2 doesn't install properly from requirements.txt so I have to run the following:\
`pip install psycopg2-binary`

from base.txt and rerun `pip install -r requirements.txt` to get requirements to install completely?

## 10. Manually install python-magic-bin
I then get the following error:\
`'magic.h' file not found #include <magic.h>`\
Which I was able to resolve by executing:\
`pip install python-magic-bin`

## 11. Create a superuser in django
https://docs.djangoproject.com/en/1.8/intro/tutorial02/

## 12. Run the server!
`python spotlit_due_diligence/manage.py runserver`

## 13. Create the user groups in django admin
Navigate to http://127.0.0.1:8000/admin_console and sign-in with the admin user you created\
Create the following groups: https://cdn.zappy.app/e0f5750d5285e944717b9ed6bc75c4b3.png \
Give the "reviewer" the following permissions: https://cdn.zappy.app/91ac20ddbe0a0095fc47b925f24fd479.png 

## 14. Login as a manager and create a new company
In order to have all the roles work, you need to login as a manager role and create a company profile, define a due diligence package and then create a company employee. A video of that can be see below in step 15.

## 15. Here is a demo video of how the portal works
https://cdn.zappy.app/1a5b963f2fe0d63949b631f86c0349b7.mov
