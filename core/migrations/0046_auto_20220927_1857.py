# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_corporaterequestselectedsupervisor_customrequestselectedsupervisor_requestselectedsupervisor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='status',
            field=models.IntegerField(default=1, choices=[(0, b'In Review'), (1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted'), (10, b'Data Form'), (11, b'Archived')]),
        ),
    ]
