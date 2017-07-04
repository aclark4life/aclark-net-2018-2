# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-04 12:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0081_proposal'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
