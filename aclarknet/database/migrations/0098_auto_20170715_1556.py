# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-15 19:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0097_remove_project_flex_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='time',
            old_name='notes',
            new_name='log',
        ),
        migrations.AlterField(
            model_name='task',
            name='color',
            field=models.CharField(blank=True, choices=[('success', 'Success'), ('info', 'Info'), ('warning', 'Warning'), ('danger', 'Danger')], max_length=7, null=True),
        ),
    ]
