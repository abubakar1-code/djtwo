# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('core', '0008_auto_20151105_1554'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted')])),
                ('datetime', models.DateTimeField(verbose_name=b'Date', db_index=True)),
                ('comments', models.TextField()),
                ('object_id', models.PositiveIntegerField()),
                ('name', models.TextField(default=b'', max_length=50)),
                ('content_type', models.ForeignKey(related_name='request', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['-datetime'],
                'db_table': 'core_status',
                'verbose_name': 'Statuses',
            },
            bases=(models.Model,),
        ),
    ]
