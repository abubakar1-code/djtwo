# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_corporaterequestdetailstatus_customrequestdetailstatus_requestdetailstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporaterequest',
            name='submitted_status',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='core.Status', null=True),
        ),
        migrations.AddField(
            model_name='customrequest',
            name='submitted_status',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='core.Status', null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='submitted_status',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='core.Status', null=True),
        ),
    ]
