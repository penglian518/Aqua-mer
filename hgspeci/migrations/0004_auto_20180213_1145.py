# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-02-13 16:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hgspeci', '0003_auto_20180212_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hgspecijob',
            name='CreatedDate',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 13, 11, 45, 10, 646165), verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='spelements',
            name='SPJobID',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='nested', to='hgspeci.HgSpeciJob'),
        ),
    ]
