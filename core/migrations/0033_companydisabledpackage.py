# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_request_pending'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyDisabledPackage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.ForeignKey(to='core.Company')),
                ('package', models.ForeignKey(to='core.CompanyDueDiligenceTypeSelection')),
            ],
            options={
                'verbose_name_plural': 'Company Disabled Public Packages',
            },
        ),
    ]
