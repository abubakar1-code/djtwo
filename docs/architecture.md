# Architecture
## Overall
### Django
### PostgreSQL
### RabbitMQ

#### Installed Apps
##### Celery
Asynchronous task queuer.
##### Crispy Forms
Helps with form rendering and validation. Adds default styling for help messages, etc.
##### Django Braces
Mixins for Django's class-based views.
##### core
This app.
##### localflavor
Additional functionality for certain countries (e.g. form fields)
##### django_countries
List of countres
##### eztables
Datatables for django. Handles pagination and ajax.
##### djangojs
Dependency of eztables
##### storages
Used for S3 storage.
##### magic
Determine file extension for file uploads.
##### djangosecure
Security library
##### encrypted_fields
Encrypted fields
##### ho
Pisa dependency?
##### reportlab
Generate pdf reports.
##### axes
Traffic monitoring (login attempts and lockout).

## Development
### Apache

### Modwsgi

## Production

### Heroku


## Batch Download

### RabbitMQ

Used as message broker for Celery tasks.

### Celery

Asynchronous task runner. Worker is created with specific functionality and is called from parent application.