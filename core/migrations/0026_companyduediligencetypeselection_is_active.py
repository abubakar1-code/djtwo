# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyduediligencetypeselection',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
