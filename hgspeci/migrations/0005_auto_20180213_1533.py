# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-02-13 20:33
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hgspeci', '0004_auto_20180213_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='hgspecijob',
            name='SPTitle',
            field=models.CharField(default='AQUA-MER SOLUTION', max_length=100),
        ),
        migrations.AlterField(
            model_name='hgspecijob',
            name='CreatedDate',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 13, 15, 33, 22, 906055), verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='spelements',
            name='Concentration',
            field=models.FloatField(blank=True),
        ),
    ]
