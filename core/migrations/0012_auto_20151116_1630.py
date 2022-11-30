# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20151116_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporaterequest',
            name='completed_status',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='core.Status', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='corporaterequest',
            name='in_progress_status',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='core.Status', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customrequest',
            name='completed_status',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='core.Status', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customrequest',
            name='in_progress_status',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='core.Status', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='completed_status',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='core.Status', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='in_progress_status',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='core.Status', null=True),
            preserve_default=True,
        ),
    ]
