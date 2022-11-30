# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20160407_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestarchive',
            name='archive_piece',
            field=models.CharField(default=b'Part 1 of 1', max_length=100),
        ),
    ]
