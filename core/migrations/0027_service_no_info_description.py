# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_companyduediligencetypeselection_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='no_info_description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
