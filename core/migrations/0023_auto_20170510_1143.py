# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_company_restrict_attachments'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyduediligencetypeselection',
            name='invoice_instructions',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='companyduediligencetypeselection',
            name='price',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
