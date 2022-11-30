# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_request_analyst_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporaterequest',
            name='analyst_notes',
            field=models.TextField(default=b'', blank=True),
        ),
        migrations.AddField(
            model_name='customrequest',
            name='analyst_notes',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
