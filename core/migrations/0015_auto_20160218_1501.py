# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20160114_1357'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientAttachmentCustom',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment', models.FileField(upload_to=core.models.request_content_file_name)),
                ('created_by', models.ForeignKey(to='core.CompanyEmployee')),
            ],
        ),
        migrations.AlterField(
            model_name='corporaterequest',
            name='attachment',
            field=models.FileField(default=None, max_length=200, null=True, upload_to=core.models.request_content_file_name, blank=True),
        ),
        migrations.AlterField(
            model_name='corporaterequest',
            name='client_attachment',
            field=models.FileField(default=None, max_length=200, null=True, upload_to=core.models.request_content_file_name, blank=True),
        ),
        migrations.AlterField(
            model_name='customrequest',
            name='attachment',
            field=models.FileField(default=None, max_length=200, null=True, upload_to=core.models.request_content_file_name, blank=True),
        ),
        migrations.AlterField(
            model_name='request',
            name='attachment',
            field=models.FileField(default=None, max_length=200, null=True, upload_to=core.models.request_content_file_name, blank=True),
        ),
        migrations.AddField(
            model_name='clientattachmentcustom',
            name='request',
            field=models.ForeignKey(related_name='attachments', to='core.CustomRequest'),
        ),
    ]
