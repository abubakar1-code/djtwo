# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20220610_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporaterequest',
            name='due_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='customrequest',
            name='due_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='request',
            name='due_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
