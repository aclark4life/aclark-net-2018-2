# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-13 00:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0095_auto_20170710_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='note',
            field=models.ManyToManyField(blank=True, to='database.Note'),
        ),
    ]
