# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-21 12:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0017_profile_payment_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='USD'),
        ),
    ]
