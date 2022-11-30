# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='status',
            name='name',
        ),
        migrations.AlterField(
            model_name='status',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
            preserve_default=True,
        ),
    ]
