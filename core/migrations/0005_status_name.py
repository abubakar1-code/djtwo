# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20151104_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='name',
            field=models.TextField(default=b'', max_length=50),
            preserve_default=True,
        ),
    ]
