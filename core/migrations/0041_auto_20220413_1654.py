# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_auto_20220216_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporaterequest',
            name='reassigned_analyst_notes',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='corporaterequest',
            name='reassigned_reviewer_notes',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='customrequest',
            name='reassigned_analyst_notes',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='customrequest',
            name='reassigned_reviewer_notes',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='request',
            name='reassigned_analyst_notes',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='request',
            name='reassigned_reviewer_notes',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='status',
            name='status',
            field=models.IntegerField(default=1, choices=[(0, b'In Review'), (1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted'), (10, b'Data Form')]),
        ),
    ]
