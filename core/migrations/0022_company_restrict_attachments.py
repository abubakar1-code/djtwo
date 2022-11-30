# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_requestarchive_archive_piece'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='restrict_attachments',
            field=models.BooleanField(default=False),
        ),
    ]
