# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_auto_20220413_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporaterequest',
            name='analyst_internal_doc',
            field=models.FileField(default=None, max_length=200, null=True, upload_to=core.models.request_content_file_name, blank=True),
        ),
        migrations.AddField(
            model_name='customrequest',
            name='analyst_internal_doc',
            field=models.FileField(default=None, max_length=200, null=True, upload_to=core.models.request_content_file_name, blank=True),
        ),
        migrations.AddField(
            model_name='request',
            name='analyst_internal_doc',
            field=models.FileField(default=None, max_length=200, null=True, upload_to=core.models.request_content_file_name, blank=True),
        ),
    ]
