# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporaterequest',
            name='name',
            field=models.CharField(max_length=50, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='name',
            field=models.CharField(db_index=True, max_length=100, blank=True),
            preserve_default=True,
        ),
    ]
