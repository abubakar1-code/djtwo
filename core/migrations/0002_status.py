# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted')])),
                ('datetime', models.DateTimeField(verbose_name=b'Date', db_index=True)),
                ('comments', models.TextField()),
                ('request_id', models.PositiveIntegerField()),
                ('request_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['-datetime'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
