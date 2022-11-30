# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20151110_1137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='corporaterequest',
            name='completed_status',
        ),
        migrations.RemoveField(
            model_name='corporaterequest',
            name='in_progress_status',
        ),
        migrations.RemoveField(
            model_name='customrequest',
            name='completed_status',
        ),
        migrations.RemoveField(
            model_name='customrequest',
            name='in_progress_status',
        ),
        migrations.RemoveField(
            model_name='request',
            name='completed_status',
        ),
        migrations.RemoveField(
            model_name='request',
            name='in_progress_status',
        ),
    ]
