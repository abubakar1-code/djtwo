# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_company_restrict_attachments'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChargeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=250, null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Charge Types',
            },
        ),
        migrations.CreateModel(
            name='Surcharge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref_number', models.CharField(max_length=100, null=True, blank=True)),
                ('request_id', models.CharField(max_length=25)),
                ('request_type', models.CharField(max_length=25)),
                ('price', models.DecimalField(max_digits=20, decimal_places=2)),
                ('notes', models.CharField(max_length=250, null=True, blank=True)),
                ('charge_type', models.ForeignKey(to='core.ChargeType')),
            ],
            options={
                'verbose_name_plural': 'Surcharges',
            },
        ),
    ]
