# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-02-13 20:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hgspeci', '0005_auto_20180213_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='spelements',
            name='Others',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='hgspecijob',
            name='CreatedDate',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 13, 15, 45, 1, 587383), verbose_name='date created'),
        ),
    ]
