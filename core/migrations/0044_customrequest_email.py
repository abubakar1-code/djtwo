# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20220628_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='customrequest',
            name='email',
            field=models.CharField(default=b'', max_length=50, null=True, verbose_name=b'Email', blank=True),
        ),
    ]
