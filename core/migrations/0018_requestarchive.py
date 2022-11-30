# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestArchive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(verbose_name=b'Date')),
                ('archive', models.FileField(upload_to=core.models.zip_archive_file_name)),
                ('company', models.ForeignKey(to='core.Company')),
                ('created_by', models.ForeignKey(to='core.CompanyEmployee')),
            ],
        ),
    ]
