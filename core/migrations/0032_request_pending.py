# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20210323_0739'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='pending',
            field=models.BooleanField(default=False),
        ),
    ]
