# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_request_state_of_employment'),
    ]

    operations = [
        migrations.CreateModel(
            name='CorporateRequestDetailStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Inital database checks in-progress'), (2, b'Request for verification in-progress'), (3, b'Pending Court Runner(s)'), (4, b'Pending Employment Verification(s)'), (5, b'Pending Education Verification(s)'), (6, b'Final database checks and write-up in-progress'), (7, b'Other')])),
                ('datetime', models.DateTimeField(verbose_name=b'Date', db_index=True)),
                ('reason', models.TextField(null=True, blank=True)),
                ('request', models.ForeignKey(to='core.CorporateRequest')),
            ],
            options={
                'ordering': ['-datetime'],
                'db_table': 'core_corporaterequestdetailstatus',
                'verbose_name_plural': 'Corporate Request Detail Statuses',
            },
        ),
        migrations.CreateModel(
            name='CustomRequestDetailStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Inital database checks in-progress'), (2, b'Request for verification in-progress'), (3, b'Pending Court Runner(s)'), (4, b'Pending Employment Verification(s)'), (5, b'Pending Education Verification(s)'), (6, b'Final database checks and write-up in-progress'), (7, b'Other')])),
                ('datetime', models.DateTimeField(verbose_name=b'Date', db_index=True)),
                ('reason', models.TextField(null=True, blank=True)),
                ('request', models.ForeignKey(to='core.CustomRequest')),
            ],
            options={
                'ordering': ['-datetime'],
                'db_table': 'core_customrequestdetailstatus',
                'verbose_name_plural': 'Custom Request Detail Statuses',
            },
        ),
        migrations.CreateModel(
            name='RequestDetailStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Inital database checks in-progress'), (2, b'Request for verification in-progress'), (3, b'Pending Court Runner(s)'), (4, b'Pending Employment Verification(s)'), (5, b'Pending Education Verification(s)'), (6, b'Final database checks and write-up in-progress'), (7, b'Other')])),
                ('datetime', models.DateTimeField(verbose_name=b'Date', db_index=True)),
                ('reason', models.TextField(null=True, blank=True)),
                ('request', models.ForeignKey(to='core.Request')),
            ],
            options={
                'ordering': ['-datetime'],
                'db_table': 'core_requestdetailstatus',
                'verbose_name_plural': 'Request Detail Statuses',
            },
        ),
    ]
