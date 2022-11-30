# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20151118_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporaterequest',
            name='reviewer',
            field=models.ForeignKey(related_name='corporate_reviewer', default=None, blank=True, to='core.SpotLitStaff', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customrequest',
            name='reviewer',
            field=models.ForeignKey(related_name='custom_reviewer', default=None, blank=True, to='core.SpotLitStaff', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='reviewer',
            field=models.ForeignKey(related_name='reviewer', default=None, blank=True, to='core.SpotLitStaff', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='corporaterequeststatus',
            name='status',
            field=models.IntegerField(default=1, choices=[(0, b'In Review'), (1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='customrequeststatus',
            name='status',
            field=models.IntegerField(default=1, choices=[(0, b'In Review'), (1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='requeststatus',
            name='status',
            field=models.IntegerField(default=1, choices=[(0, b'In Review'), (1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='status',
            name='status',
            field=models.IntegerField(default=1, choices=[(0, b'In Review'), (1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted')]),
            preserve_default=True,
        ),
    ]
