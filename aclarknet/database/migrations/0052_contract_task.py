# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-13 15:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0051_auto_20170613_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='database.Task'),
        ),
    ]
