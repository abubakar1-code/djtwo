# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20160114_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='customrequest',
            name='pdf_report',
            field=models.FileField(default=None, null=True, upload_to=core.models.pdf_report_file_name, blank=True),
        ),
    ]
