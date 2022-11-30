# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_request_annual_income_exceeds_75000'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='terms_agreed',
            field=models.BooleanField(default=True),
        ),
    ]
