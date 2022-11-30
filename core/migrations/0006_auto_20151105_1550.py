# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_status_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='status',
            name='request_id',
        ),
        migrations.RemoveField(
            model_name='status',
            name='request_type',
        ),
    ]
