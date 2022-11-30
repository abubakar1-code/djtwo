# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20210209_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='annual_income_exceeds_75000',
            field=models.BooleanField(default=False),
        ),
    ]
