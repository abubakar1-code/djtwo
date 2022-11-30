# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20160308_1716'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name_plural': 'Adresses'},
        ),
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name_plural': 'Companies'},
        ),
        migrations.AlterModelOptions(
            name='companyduediligencetypeselection',
            options={'verbose_name_plural': 'Company Due Diligencte Type Selections'},
        ),
        migrations.AlterModelOptions(
            name='companyserviceselection',
            options={'verbose_name_plural': 'Company Service Selections'},
        ),
        migrations.AlterModelOptions(
            name='corporaterequestservicestatus',
            options={'verbose_name_plural': 'Corporate Request Service Statuses'},
        ),
        migrations.AlterModelOptions(
            name='customrequest',
            options={'verbose_name_plural': 'Custom Requests'},
        ),
        migrations.AlterModelOptions(
            name='customrequestfields',
            options={'verbose_name_plural': 'Custom Request Fields'},
        ),
        migrations.AlterModelOptions(
            name='customrequestservicestatus',
            options={'verbose_name_plural': 'Custom Request Service Statuses'},
        ),
        migrations.AlterModelOptions(
            name='duediligencetype',
            options={'verbose_name_plural': 'Due Diligence Types'},
        ),
        migrations.AlterModelOptions(
            name='duediligencetypeservices',
            options={'verbose_name_plural': 'Due Diligence Type Services'},
        ),
        migrations.AlterModelOptions(
            name='dynamicrequestformfields',
            options={'verbose_name_plural': 'Dynamic Request Form Fields'},
        ),
        migrations.AlterModelOptions(
            name='reports',
            options={'verbose_name_plural': 'Reports'},
        ),
        migrations.AlterModelOptions(
            name='request',
            options={'verbose_name_plural': 'Requests'},
        ),
        migrations.AlterModelOptions(
            name='requestservicestatus',
            options={'verbose_name_plural': 'Request Service Statuses'},
        ),
        migrations.AlterModelOptions(
            name='spotlitstaff',
            options={'verbose_name_plural': 'Spotlit Staff'},
        ),
        migrations.AlterModelOptions(
            name='status',
            options={'ordering': ['-datetime'], 'verbose_name_plural': 'Statuses'},
        ),
    ]
