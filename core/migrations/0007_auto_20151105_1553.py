# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('core', '0006_auto_20151105_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='content_type',
            field=models.ForeignKey(related_name='request', default=0, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='status',
            name='object_id',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
