# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-11 00:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0093_auto_20170710_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='dashboard_order',
            field=models.CharField(blank=True, default='data,invoices,notes,projects,totals', max_length=255, null=True),
        ),
    ]
