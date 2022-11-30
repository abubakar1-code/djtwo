# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_requestarchive'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporaterequest',
            name='pdf_report',
            field=models.FileField(default=None, null=True, upload_to=core.models.pdf_corporate_report_file_name, blank=True),
        ),
        migrations.AddField(
            model_name='request',
            name='pdf_report',
            field=models.FileField(default=None, null=True, upload_to=core.models.pdf_report_file_name, blank=True),
        ),
        migrations.AlterField(
            model_name='customrequest',
            name='pdf_report',
            field=models.FileField(default=None, null=True, upload_to=core.models.pdf_custom_report_file_name, blank=True),
        ),
    ]
