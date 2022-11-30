# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.contrib.auth.models import Group
from core.models import UNVERIFIED_USER_GROUP

def create_unverified_user_group(*args,**kwargs):
    Group.objects.get_or_create(name=UNVERIFIED_USER_GROUP)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_company_terms_agreed'),
    ]

    operations = [
        migrations.RunPython(create_unverified_user_group)
    ]
