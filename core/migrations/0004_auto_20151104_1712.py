# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20151104_1553'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='status',
            options={'ordering': ['-datetime'], 'verbose_name': 'Statuses'},
        ),
        migrations.AlterField(
            model_name='status',
            name='request_type',
            field=models.ForeignKey(related_name='request', to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AlterModelTable(
            name='status',
            table='core_status',
        ),
    ]
