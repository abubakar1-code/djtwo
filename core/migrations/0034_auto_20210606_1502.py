# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_companydisabledpackage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='surcharge',
            old_name='price',
            new_name='estimated_cost',
        ),
        migrations.AddField(
            model_name='surcharge',
            name='order_number',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='surcharge',
            name='processing_fee',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='surcharge',
            name='source',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
    ]
