from __future__ import absolute_import

import os
import socket

from celery import Celery

if socket.gethostname() == 'CHI1004':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spotlit_due_diligence.settings.dev-conrad")

else:
	# set the default Django settings module for the 'celery' program.
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlit_due_diligence.settings.production')

from django.conf import settings  # noqa

app = Celery('spotlit_due_diligence')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')

# load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))