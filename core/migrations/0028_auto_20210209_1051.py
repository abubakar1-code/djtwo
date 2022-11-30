# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_service_no_info_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyduediligencetypeselection',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='companyduediligencetypeselection',
            name='company',
            field=models.ForeignKey(default=None, blank=True, to='core.Company', null=True),
        ),
    ]
