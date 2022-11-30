# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20160218_1501'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment', models.FileField(upload_to=core.models.request_content_file_name)),
                ('created_by', models.ForeignKey(to='core.CompanyEmployee')),
                ('request', models.ForeignKey(related_name='attachments', to='core.Request')),
            ],
        ),
        migrations.CreateModel(
            name='ClientAttachmentCorporate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment', models.FileField(upload_to=core.models.request_content_file_name)),
                ('created_by', models.ForeignKey(to='core.CompanyEmployee')),
                ('request', models.ForeignKey(related_name='attachments', to='core.CorporateRequest')),
            ],
        ),
        migrations.RemoveField(
            model_name='corporaterequeststatus',
            name='corporate_request',
        ),
        migrations.RemoveField(
            model_name='customrequeststatus',
            name='request',
        ),
        migrations.RemoveField(
            model_name='requeststatus',
            name='request',
        ),
        migrations.DeleteModel(
            name='CorporateRequestStatus',
        ),
        migrations.DeleteModel(
            name='CustomRequestStatus',
        ),
        migrations.DeleteModel(
            name='RequestStatus',
        ),
    ]
