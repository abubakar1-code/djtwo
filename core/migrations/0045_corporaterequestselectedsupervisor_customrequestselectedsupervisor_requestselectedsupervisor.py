# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_customrequest_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='CorporateRequestSelectedSupervisor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('corporate_request', models.ForeignKey(to='core.CorporateRequest')),
                ('supervisor', models.ForeignKey(to='core.CompanyEmployee')),
            ],
        ),
        migrations.CreateModel(
            name='CustomRequestSelectedSupervisor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('custom_request', models.ForeignKey(to='core.CustomRequest')),
                ('supervisor', models.ForeignKey(to='core.CompanyEmployee')),
            ],
        ),
        migrations.CreateModel(
            name='RequestSelectedSupervisor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request', models.ForeignKey(to='core.Request')),
                ('supervisor', models.ForeignKey(to='core.CompanyEmployee')),
            ],
        ),
    ]
