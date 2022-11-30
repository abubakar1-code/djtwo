# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20210606_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='analyst_notes',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
